"""Authentication, device sessions, token rotation/revocation, RBAC, and tamper-evident audit log.

Implements T003 security controls (`ACC-01`..`ACC-07`, `ACC-10`, `SEC-01`..`SEC-03`, `SEC-12`, `SEC-14`):
- Scrypt password hashing with per-user random salt.
- HMAC-SHA256 signed access tokens bound to revocable `device_sessions` and `access_jti`.
- Guest-to-account idempotent one-time migration (`ACC-03`).
- Personal data export (`ACC-07`) and account deletion/anonymization (`ACC-06`, `SEC-07`).
- Role-based access control (`listener`, `creator`, `legal_reviewer`, `rights_officer`, `compliance_admin`)
  with append-only audit logging of privilege escalation attempts (`ACC-10`, `SEC-12`).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from audioverse.storage import _connect

UserRole = Literal["listener", "creator", "legal_reviewer", "rights_officer", "compliance_admin"]
VALID_ROLES: set[str] = {
    "listener",
    "creator",
    "legal_reviewer",
    "rights_officer",
    "compliance_admin",
}
STAFF_REVIEWER_ROLES: set[str] = {"legal_reviewer", "rights_officer", "compliance_admin"}


class AuthError(PermissionError):
    """Authentication failure (401 Unauthorized)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class ForbiddenError(PermissionError):
    """Authorization / RBAC failure (403 Forbidden)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class Principal:
    actor_id: str
    role: UserRole
    authenticated: bool
    session_id: str | None = None
    email: str | None = None


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(text: str) -> bytes:
    pad = "=" * ((4 - len(text) % 4) % 4)
    return base64.urlsafe_b64decode((text + pad).encode("ascii"))


def hash_password(password: str, salt: bytes | None = None) -> str:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    raw_salt = salt or secrets.token_bytes(16)
    derived = hashlib.scrypt(
        password.encode("utf-8"),
        salt=raw_salt,
        n=2**14,
        r=8,
        p=1,
        dklen=32,
    )
    return f"scrypt${_b64url_encode(raw_salt)}${_b64url_encode(derived)}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        scheme, salt_b64, digest_b64 = stored_hash.split("$", 2)
        if scheme != "scrypt":
            return False
        raw_salt = _b64url_decode(salt_b64)
        expected = _b64url_decode(digest_b64)
        actual = hashlib.scrypt(
            password.encode("utf-8"),
            salt=raw_salt,
            n=2**14,
            r=8,
            p=1,
            dklen=len(expected),
        )
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def mint_access_token(
    *,
    secret: str,
    user_id: str,
    role: UserRole,
    session_id: str,
    jti: str,
    now: datetime | None = None,
    ttl_seconds: int = 3600,
) -> str:
    issued = now or datetime.now(UTC)
    exp = issued + timedelta(seconds=ttl_seconds)
    header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode("utf-8"))
    payload = _b64url_encode(
        json.dumps(
            {
                "sub": user_id,
                "role": role,
                "sid": session_id,
                "jti": jti,
                "iat": int(issued.timestamp()),
                "exp": int(exp.timestamp()),
            },
            separators=(",", ":"),
        ).encode("utf-8")
    )
    signing_input = f"{header}.{payload}".encode("ascii")
    sig = _b64url_encode(
        hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    )
    return f"{header}.{payload}.{sig}"


def append_security_audit(
    db_path: Path,
    *,
    actor_id: str,
    actor_role: str,
    action: str,
    target_id: str | None,
    decision: str,
    detail: str,
) -> dict[str, Any]:
    with _connect(db_path) as con:
        con.execute("BEGIN IMMEDIATE")
        try:
            last = con.execute(
                "SELECT entry_hash FROM security_audit_log ORDER BY id DESC LIMIT 1"
            ).fetchone()
            prev_hash = last["entry_hash"] if last is not None else "0" * 64
            payload = f"{prev_hash}|{actor_id}|{actor_role}|{action}|{target_id or ''}|{decision}|{detail}"
            entry_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
            con.execute(
                """
                INSERT INTO security_audit_log(
                    actor_id, actor_role, action, target_id, decision, detail, prev_hash, entry_hash
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    actor_id,
                    actor_role,
                    action,
                    target_id,
                    decision,
                    detail,
                    prev_hash,
                    entry_hash,
                ),
            )
            row = con.execute(
                "SELECT * FROM security_audit_log ORDER BY id DESC LIMIT 1"
            ).fetchone()
            con.execute("COMMIT")
            return dict(row)
        except Exception:
            con.execute("ROLLBACK")
            raise


def verify_security_audit_chain(db_path: Path) -> bool:
    with _connect(db_path) as con:
        rows = con.execute("SELECT * FROM security_audit_log ORDER BY id ASC").fetchall()
    prev = "0" * 64
    for r in rows:
        if r["prev_hash"] != prev:
            return False
        payload = (
            f"{prev}|{r['actor_id']}|{r['actor_role']}|{r['action']}|"
            f"{r['target_id'] or ''}|{r['decision']}|{r['detail']}"
        )
        expected = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        if r["entry_hash"] != expected:
            return False
        prev = expected
    return True


def register_user(
    db_path: Path,
    *,
    secret: str,
    email: str,
    password: str,
    display_name: str,
    device_name: str = "default-device",
    role: UserRole = "listener",
) -> dict[str, Any]:
    norm_email = email.strip().lower()
    if "@" not in norm_email or len(norm_email) < 5:
        raise ValueError("Invalid email address")
    if role not in VALID_ROLES:
        raise ValueError(f"Invalid role: {role}")
    pw_hash = hash_password(password)
    uid = str(uuid4())
    sid = str(uuid4())
    jti = secrets.token_hex(16)
    refresh_token = secrets.token_urlsafe(32)
    now = datetime.now(UTC)
    exp = (now + timedelta(days=30)).isoformat()

    with _connect(db_path) as con:
        con.execute("BEGIN IMMEDIATE")
        try:
            existing = con.execute(
                "SELECT id FROM users WHERE email=?", (norm_email,)
            ).fetchone()
            if existing is not None:
                raise ValueError("Email is already registered")
            con.execute(
                """
                INSERT INTO users(id, email, password_hash, role, display_name, status)
                VALUES(?, ?, ?, ?, ?, 'active')
                """,
                (uid, norm_email, pw_hash, role, display_name.strip()),
            )
            con.execute(
                """
                INSERT INTO device_sessions(
                    id, user_id, device_name, refresh_token_hash, access_jti, expires_at
                ) VALUES(?, ?, ?, ?, ?, ?)
                """,
                (sid, uid, device_name.strip(), _hash_token(refresh_token), jti, exp),
            )
            con.execute("COMMIT")
        except Exception:
            con.execute("ROLLBACK")
            raise

    append_security_audit(
        db_path,
        actor_id=uid,
        actor_role=role,
        action="USER_REGISTER",
        target_id=uid,
        decision="ALLOW",
        detail=f"Registered user {norm_email} on device {device_name}",
    )
    access_token = mint_access_token(
        secret=secret,
        user_id=uid,
        role=role,
        session_id=sid,
        jti=jti,
        now=now,
    )
    return {
        "user": {
            "id": uid,
            "email": norm_email,
            "display_name": display_name.strip(),
            "role": role,
        },
        "session_id": sid,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


def login_user(
    db_path: Path,
    *,
    secret: str,
    email: str,
    password: str,
    device_name: str = "default-device",
) -> dict[str, Any]:
    norm_email = email.strip().lower()
    with _connect(db_path) as con:
        user = con.execute("SELECT * FROM users WHERE email=?", (norm_email,)).fetchone()
        if (
            user is None
            or user["status"] != "active"
            or not verify_password(password, user["password_hash"])
        ):
            raise AuthError("AUTH_INVALID_CREDENTIALS", "Invalid email or password")

        uid = user["id"]
        role: UserRole = user["role"]
        sid = str(uuid4())
        jti = secrets.token_hex(16)
        refresh_token = secrets.token_urlsafe(32)
        now = datetime.now(UTC)
        exp = (now + timedelta(days=30)).isoformat()
        con.execute(
            """
            INSERT INTO device_sessions(
                id, user_id, device_name, refresh_token_hash, access_jti, expires_at
            ) VALUES(?, ?, ?, ?, ?, ?)
            """,
            (sid, uid, device_name.strip(), _hash_token(refresh_token), jti, exp),
        )

    access_token = mint_access_token(
        secret=secret,
        user_id=uid,
        role=role,
        session_id=sid,
        jti=jti,
        now=now,
    )
    return {
        "user": {
            "id": uid,
            "email": user["email"],
            "display_name": user["display_name"],
            "role": role,
        },
        "session_id": sid,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


def verify_access_token(
    db_path: Path,
    *,
    secret: str,
    token: str,
    now: datetime | None = None,
) -> Principal:
    parts = token.split(".")
    if len(parts) != 3:
        raise AuthError("AUTH_MALFORMED_TOKEN", "Malformed access token")
    header_b64, payload_b64, sig_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    expected_sig = _b64url_encode(
        hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    )
    if not hmac.compare_digest(sig_b64, expected_sig):
        raise AuthError("AUTH_INVALID_SIGNATURE", "Invalid token signature")
    try:
        payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
    except Exception as exc:
        raise AuthError("AUTH_MALFORMED_TOKEN", "Invalid token payload") from exc

    check_time = now or datetime.now(UTC)
    if int(payload.get("exp", 0)) <= int(check_time.timestamp()):
        raise AuthError("AUTH_TOKEN_EXPIRED", "Access token has expired")

    uid = payload.get("sub")
    sid = payload.get("sid")
    jti = payload.get("jti")
    if not uid or not sid or not jti:
        raise AuthError("AUTH_MALFORMED_TOKEN", "Missing required token claims")

    with _connect(db_path) as con:
        user = con.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        if user is None or user["status"] != "active":
            raise AuthError("AUTH_USER_INACTIVE", "User account is inactive or deleted")
        session = con.execute(
            "SELECT * FROM device_sessions WHERE id=? AND user_id=?",
            (sid, uid),
        ).fetchone()
        if session is None or session["revoked_at"] is not None:
            raise AuthError("AUTH_SESSION_REVOKED", "Device session has been revoked")
        if session["access_jti"] != jti:
            raise AuthError("AUTH_TOKEN_ROTATED", "Access token has been superseded")
        sess_exp = datetime.fromisoformat(session["expires_at"])
        if sess_exp.tzinfo is None:
            sess_exp = sess_exp.replace(tzinfo=UTC)
        if check_time >= sess_exp:
            raise AuthError("AUTH_SESSION_EXPIRED", "Device session has expired")

    return Principal(
        actor_id=uid,
        role=user["role"],
        authenticated=True,
        session_id=sid,
        email=user["email"],
    )


def refresh_device_session(
    db_path: Path,
    *,
    secret: str,
    session_id: str,
    refresh_token: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    check_time = now or datetime.now(UTC)
    new_jti = secrets.token_hex(16)
    new_refresh = secrets.token_urlsafe(32)
    new_exp = (check_time + timedelta(days=30)).isoformat()

    with _connect(db_path) as con:
        con.execute("BEGIN IMMEDIATE")
        try:
            session = con.execute(
                "SELECT * FROM device_sessions WHERE id=?", (session_id,)
            ).fetchone()
            if session is None or session["revoked_at"] is not None:
                raise AuthError("AUTH_SESSION_REVOKED", "Session is invalid or revoked")
            if not hmac.compare_digest(
                session["refresh_token_hash"], _hash_token(refresh_token)
            ):
                # Potential refresh token replay: revoke the session immediately
                con.execute(
                    "UPDATE device_sessions SET revoked_at=? WHERE id=?",
                    (check_time.isoformat(), session_id),
                )
                con.execute("COMMIT")
                raise AuthError("AUTH_INVALID_REFRESH_TOKEN", "Invalid refresh token")
            user = con.execute(
                "SELECT * FROM users WHERE id=?", (session["user_id"],)
            ).fetchone()
            if user is None or user["status"] != "active":
                raise AuthError("AUTH_USER_INACTIVE", "User is inactive")
            con.execute(
                """
                UPDATE device_sessions
                SET refresh_token_hash=?, access_jti=?, expires_at=?
                WHERE id=?
                """,
                (_hash_token(new_refresh), new_jti, new_exp, session_id),
            )
            con.execute("COMMIT")
        except Exception:
            if con.in_transaction:
                con.execute("ROLLBACK")
            raise

    access_token = mint_access_token(
        secret=secret,
        user_id=user["id"],
        role=user["role"],
        session_id=session_id,
        jti=new_jti,
        now=check_time,
    )
    return {
        "session_id": session_id,
        "access_token": access_token,
        "refresh_token": new_refresh,
    }


def revoke_device_session(
    db_path: Path,
    *,
    user_id: str,
    session_id: str,
) -> bool:
    now_iso = datetime.now(UTC).isoformat()
    with _connect(db_path) as con:
        cur = con.execute(
            """
            UPDATE device_sessions
            SET revoked_at=COALESCE(revoked_at, ?)
            WHERE id=? AND user_id=?
            """,
            (now_iso, session_id, user_id),
        )
        return cur.rowcount > 0


def list_device_sessions(db_path: Path, *, user_id: str) -> list[dict[str, Any]]:
    with _connect(db_path) as con:
        rows = con.execute(
            """
            SELECT id, device_name, expires_at, revoked_at, created_at
            FROM device_sessions
            WHERE user_id=?
            ORDER BY created_at DESC
            """,
            (user_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def migrate_guest_runs(
    db_path: Path,
    *,
    guest_actor: str,
    target_user_id: str,
) -> dict[str, Any]:
    """Migrate guest demo runs to an authenticated user account idempotently (`ACC-03`)."""
    if guest_actor == target_user_id:
        raise ValueError("guest_actor must be distinct from target_user_id")
    with _connect(db_path) as con:
        con.execute("BEGIN IMMEDIATE")
        try:
            existing = con.execute(
                "SELECT * FROM guest_migrations WHERE guest_actor=?",
                (guest_actor,),
            ).fetchone()
            if existing is not None:
                if existing["target_user_id"] != target_user_id:
                    raise ForbiddenError(
                        "MIGRATION_ALREADY_CLAIMED",
                        "Guest identity was already migrated to another account",
                    )
                con.execute("COMMIT")
                return {
                    "guest_actor": guest_actor,
                    "target_user_id": target_user_id,
                    "migrated_runs": existing["migrated_runs"],
                    "already_migrated": True,
                }
            cur = con.execute(
                "UPDATE runs SET demo_actor=?, updated_at=CURRENT_TIMESTAMP WHERE demo_actor=?",
                (target_user_id, guest_actor),
            )
            count = cur.rowcount
            con.execute(
                """
                INSERT INTO guest_migrations(guest_actor, target_user_id, migrated_runs)
                VALUES(?, ?, ?)
                """,
                (guest_actor, target_user_id, count),
            )
            con.execute("COMMIT")
        except Exception:
            if con.in_transaction:
                con.execute("ROLLBACK")
            raise

    append_security_audit(
        db_path,
        actor_id=target_user_id,
        actor_role="listener",
        action="GUEST_MIGRATION",
        target_id=guest_actor,
        decision="ALLOW",
        detail=f"Migrated {count} runs from guest '{guest_actor}'",
    )
    return {
        "guest_actor": guest_actor,
        "target_user_id": target_user_id,
        "migrated_runs": count,
        "already_migrated": False,
    }


def export_user_data(db_path: Path, *, user_id: str) -> dict[str, Any]:
    """Export personal profile, device sessions, and owned story runs/events (`ACC-07`)."""
    with _connect(db_path) as con:
        user = con.execute(
            "SELECT id, email, display_name, role, status, created_at FROM users WHERE id=?",
            (user_id,),
        ).fetchone()
        if user is None:
            raise AuthError("AUTH_USER_NOT_FOUND", "User not found")
        sessions = con.execute(
            "SELECT id, device_name, expires_at, revoked_at, created_at "
            "FROM device_sessions WHERE user_id=? ORDER BY id",
            (user_id,),
        ).fetchall()
        runs = con.execute(
            "SELECT id, story_id, edition_id, scene_id, flags_json, version, state_checksum, "
            "created_at, updated_at FROM runs WHERE demo_actor=? ORDER BY created_at",
            (user_id,),
        ).fetchall()
        exported_runs: list[dict[str, Any]] = []
        for r in runs:
            events = con.execute(
                "SELECT choice_id, from_scene, to_scene, event_hash, created_at "
                "FROM events WHERE run_id=? ORDER BY id",
                (r["id"],),
            ).fetchall()
            exported_runs.append(
                {
                    "run_id": r["id"],
                    "story_id": r["story_id"],
                    "edition_id": r["edition_id"],
                    "scene_id": r["scene_id"],
                    "flags": json.loads(r["flags_json"]),
                    "version": r["version"],
                    "state_checksum": r["state_checksum"],
                    "created_at": r["created_at"],
                    "updated_at": r["updated_at"],
                    "events": [dict(e) for e in events],
                }
            )
    return {
        "user": dict(user),
        "device_sessions": [dict(s) for s in sessions],
        "runs": exported_runs,
    }


def delete_user_account(db_path: Path, *, user_id: str) -> dict[str, Any]:
    """Delete/anonymize user account, revoke all sessions, and anonymize owned runs (`ACC-06`)."""
    now_iso = datetime.now(UTC).isoformat()
    tombstone_actor = f"deleted-{hashlib.sha256(user_id.encode('utf-8')).hexdigest()[:16]}"
    with _connect(db_path) as con:
        con.execute("BEGIN IMMEDIATE")
        try:
            user = con.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
            if user is None or user["status"] == "deleted":
                raise AuthError("AUTH_USER_NOT_FOUND", "User account not found")
            con.execute(
                "UPDATE device_sessions SET revoked_at=COALESCE(revoked_at, ?) WHERE user_id=?",
                (now_iso, user_id),
            )
            runs_cur = con.execute(
                "UPDATE runs SET demo_actor=?, updated_at=CURRENT_TIMESTAMP WHERE demo_actor=?",
                (tombstone_actor, user_id),
            )
            con.execute(
                """
                UPDATE users
                SET email=?, password_hash='deleted', display_name='Deleted User',
                    status='deleted', deleted_at=?
                WHERE id=?
                """,
                (f"{tombstone_actor}@deleted.invalid", now_iso, user_id),
            )
            con.execute("COMMIT")
        except Exception:
            if con.in_transaction:
                con.execute("ROLLBACK")
            raise

    append_security_audit(
        db_path,
        actor_id=user_id,
        actor_role=user["role"],
        action="USER_ACCOUNT_DELETE",
        target_id=user_id,
        decision="ALLOW",
        detail=f"Deleted account and anonymized {runs_cur.rowcount} runs",
    )
    return {
        "deleted_user_id": user_id,
        "anonymized_runs": runs_cur.rowcount,
        "status": "deleted",
    }


def require_role(
    db_path: Path,
    principal: Principal,
    allowed_roles: set[str],
    *,
    action: str,
    target_id: str | None = None,
) -> None:
    if not principal.authenticated:
        raise AuthError("AUTH_REQUIRED", "Authentication is required for this resource")
    if principal.role not in allowed_roles:
        append_security_audit(
            db_path,
            actor_id=principal.actor_id,
            actor_role=principal.role,
            action=action,
            target_id=target_id,
            decision="DENY_ROLE_ESCALATION",
            detail=f"Role '{principal.role}' denied access requiring {sorted(allowed_roles)}",
        )
        raise ForbiddenError(
            "RBAC_ROLE_DENIED",
            f"Role '{principal.role}' is not authorized for '{action}'",
        )
