"""Private audio object registry, short-lived signed URLs, entitlement checks, and range delivery.

Implements T004 secure media delivery (`PLY-10`, `PLY-15`, `SEC-09`):
- Registers opaque `asset_id` entries in `media_objects` with SHA-256, byte size, and `cache_epoch`.
- Validates user/actor authentication, `user_entitlements` (stream vs. offline, expiry, revocation),
  and `RightsManifest` permissions before issuing short-lived HMAC-SHA256 media tokens.
- Revalidates token signature, TTL, actor binding, active device session, entitlement, `cache_epoch`,
  rights version, and live rights/quarantine/takedown state at media delivery time.
- Supports HTTP Range (`206 Partial Content`) with private cache headers and redacted audit logging.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from audioverse.auth import Principal
from audioverse.content import assert_permission
from audioverse.rights import RightsManifest, RightsViolationError
from audioverse.storage import _connect

MediaAction = Literal["stream", "offline"]


class MediaAccessError(PermissionError):
    """Media authorization or signed URL delivery failure."""

    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


@dataclass(frozen=True)
class ByteRangeSlice:
    data: bytes
    status_code: int
    content_type: str
    headers: dict[str, str]
    bytes_served: int


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(text: str) -> bytes:
    pad = "=" * ((4 - len(text) % 4) % 4)
    return base64.urlsafe_b64decode((text + pad).encode("ascii"))


def sync_media_registry(
    db_path: Path,
    manifest: RightsManifest,
    media_dir: Path,
) -> int:
    """Register or synchronize `manifest.assets` into the private `media_objects` table."""
    count = 0
    with _connect(db_path) as con:
        con.execute("BEGIN IMMEDIATE")
        try:
            for scene_id, asset in manifest.assets.items():
                relpath = f"{scene_id}.mp3"
                mp3_file = (media_dir / relpath).resolve()
                if not mp3_file.is_relative_to(media_dir.resolve()):
                    raise ValueError(f"Unsafe media path for scene {scene_id}")
                size = mp3_file.stat().st_size if mp3_file.is_file() else 0
                con.execute(
                    """
                    INSERT INTO media_objects(
                        asset_id, work_id, edition_id, scene_id, storage_relpath,
                        sha256, byte_size, content_type, rights_grant_id,
                        rights_grant_version, status, cache_epoch
                    ) VALUES(?, ?, ?, ?, ?, ?, ?, 'audio/mpeg', ?, ?, ?, 1)
                    ON CONFLICT(asset_id) DO UPDATE SET
                        sha256=excluded.sha256,
                        byte_size=excluded.byte_size,
                        rights_grant_id=excluded.rights_grant_id,
                        rights_grant_version=excluded.rights_grant_version,
                        status=excluded.status
                    """,
                    (
                        asset.asset_id,
                        asset.work_id,
                        asset.edition_id,
                        scene_id,
                        relpath,
                        asset.sha256,
                        size,
                        asset.rights_grant_id,
                        asset.rights_grant_version,
                        asset.status,
                    ),
                )
                count += 1
            con.execute("COMMIT")
        except Exception:
            if con.in_transaction:
                con.execute("ROLLBACK")
            raise
    return count


def log_media_delivery(
    db_path: Path,
    *,
    actor_id: str,
    asset_id: str,
    action: str,
    status_code: int,
    bytes_served: int = 0,
    detail: str,
) -> None:
    with _connect(db_path) as con:
        con.execute(
            """
            INSERT INTO media_delivery_logs(
                actor_id, asset_id, action, status_code, bytes_served, detail
            ) VALUES(?, ?, ?, ?, ?, ?)
            """,
            (actor_id, asset_id, action, status_code, bytes_served, detail),
        )


def grant_entitlement(
    db_path: Path,
    *,
    user_id: str,
    work_id: str,
    allow_stream: bool = True,
    allow_offline: bool = False,
    expires_at: datetime,
) -> dict[str, Any]:
    eid = str(uuid4())
    exp_iso = expires_at.astimezone(UTC).isoformat()
    with _connect(db_path) as con:
        con.execute(
            """
            INSERT INTO user_entitlements(
                id, user_id, work_id, allow_stream, allow_offline, expires_at
            ) VALUES(?, ?, ?, ?, ?, ?)
            """,
            (eid, user_id, work_id, int(allow_stream), int(allow_offline), exp_iso),
        )
        row = con.execute("SELECT * FROM user_entitlements WHERE id=?", (eid,)).fetchone()
    return dict(row)


def revoke_entitlement(db_path: Path, *, entitlement_id: str) -> bool:
    now_iso = datetime.now(UTC).isoformat()
    with _connect(db_path) as con:
        cur = con.execute(
            "UPDATE user_entitlements SET revoked_at=COALESCE(revoked_at, ?) WHERE id=?",
            (now_iso, entitlement_id),
        )
        return cur.rowcount > 0


def invalidate_media_cache(db_path: Path, *, asset_id: str) -> int:
    """Bump `cache_epoch` for `asset_id` so previously issued signed URLs fail closed."""
    with _connect(db_path) as con:
        cur = con.execute(
            "UPDATE media_objects SET cache_epoch = cache_epoch + 1 WHERE asset_id=?",
            (asset_id,),
        )
        if cur.rowcount == 0:
            raise MediaAccessError(404, "MEDIA_ASSET_NOT_FOUND", f"Unknown asset '{asset_id}'")
        row = con.execute(
            "SELECT cache_epoch FROM media_objects WHERE asset_id=?", (asset_id,)
        ).fetchone()
    return int(row["cache_epoch"])


def _check_entitlement(
    con: Any,
    *,
    actor_id: str,
    work_id: str,
    action: MediaAction,
    now: datetime,
    require_entitlement: bool,
) -> None:
    rows = con.execute(
        """
        SELECT * FROM user_entitlements
        WHERE user_id=? AND work_id IN (?, '*')
        ORDER BY created_at DESC
        """,
        (actor_id, work_id),
    ).fetchall()

    if not rows:
        if require_entitlement:
            raise MediaAccessError(
                403,
                "ENTITLEMENT_REQUIRED",
                f"User '{actor_id}' has no active entitlement for work '{work_id}'",
            )
        return

    # If entitlement records exist for this user+work, at least one must be active & permit action
    active_rows = []
    for r in rows:
        if r["revoked_at"] is not None:
            continue
        exp = datetime.fromisoformat(r["expires_at"])
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=UTC)
        if now < exp:
            active_rows.append(r)

    if not active_rows:
        raise MediaAccessError(
            403,
            "ENTITLEMENT_EXPIRED",
            f"Entitlement for user '{actor_id}' on work '{work_id}' is expired or revoked",
        )

    if action == "offline" and not any(bool(r["allow_offline"]) for r in active_rows):
        raise MediaAccessError(
            403,
            "OFFLINE_ENTITLEMENT_REQUIRED",
            "Active entitlement permits streaming only, not offline downloads",
        )
    if action == "stream" and not any(bool(r["allow_stream"]) for r in active_rows):
        raise MediaAccessError(
            403,
            "STREAM_ENTITLEMENT_REQUIRED",
            "Active entitlement does not permit streaming",
        )


def mint_media_token(
    *,
    secret: str,
    actor_id: str,
    session_id: str | None,
    asset_id: str,
    work_id: str,
    edition_id: str,
    scene_id: str,
    action: MediaAction,
    territory: str,
    rights_version: int,
    cache_epoch: int,
    now: datetime | None = None,
    ttl_seconds: int = 300,
) -> tuple[str, datetime]:
    if ttl_seconds < 1 or ttl_seconds > 900:
        raise ValueError("Media token ttl_seconds must be between 1 and 900 seconds")
    issued = now or datetime.now(UTC)
    exp = issued + timedelta(seconds=ttl_seconds)
    payload_bytes = json.dumps(
        {
            "sub": actor_id,
            "sid": session_id,
            "aid": asset_id,
            "wid": work_id,
            "eid": edition_id,
            "scn": scene_id,
            "act": action,
            "ter": territory,
            "rv": rights_version,
            "ce": cache_epoch,
            "iat": int(issued.timestamp()),
            "exp": int(exp.timestamp()),
        },
        separators=(",", ":"),
    ).encode("utf-8")
    payload_b64 = _b64url_encode(payload_bytes)
    sig_b64 = _b64url_encode(
        hmac.new(secret.encode("utf-8"), payload_b64.encode("ascii"), hashlib.sha256).digest()
    )
    return f"{payload_b64}.{sig_b64}", exp


def authorize_playback(
    db_path: Path,
    *,
    secret: str,
    manifest: RightsManifest,
    principal: Principal,
    work_id: str,
    scene_id: str,
    action: MediaAction = "stream",
    edition_id: str | None = None,
    territory: str = "VN",
    ttl_seconds: int = 300,
    require_entitlement: bool = False,
    now: datetime | None = None,
) -> dict[str, Any]:
    check_time = now or datetime.now(UTC)
    target_edition = edition_id or manifest.grant.edition_id

    if work_id != manifest.content_id:
        raise MediaAccessError(404, "WORK_NOT_FOUND", f"Unknown work '{work_id}'")
    if scene_id not in manifest.assets:
        raise MediaAccessError(404, "SCENE_NOT_FOUND", f"Unknown scene '{scene_id}'")

    # 1. Rights & AssetLicense check
    try:
        assert_permission(
            manifest,
            action,
            scene_id=scene_id,
            territory=territory,
            edition_id=target_edition,
            at_time=check_time,
        )
    except RightsViolationError as exc:
        log_media_delivery(
            db_path,
            actor_id=principal.actor_id,
            asset_id=manifest.assets[scene_id].asset_id,
            action=f"authorize_{action}",
            status_code=403,
            detail=f"Denied by rights gate: {exc.code}",
        )
        raise MediaAccessError(403, exc.code, exc.reason) from exc

    with _connect(db_path) as con:
        # 2. Entitlement check
        try:
            _check_entitlement(
                con,
                actor_id=principal.actor_id,
                work_id=work_id,
                action=action,
                now=check_time,
                require_entitlement=require_entitlement,
            )
        except MediaAccessError as exc:
            log_media_delivery(
                db_path,
                actor_id=principal.actor_id,
                asset_id=manifest.assets[scene_id].asset_id,
                action=f"authorize_{action}",
                status_code=exc.status_code,
                detail=f"Denied by entitlement gate: {exc.code}",
            )
            raise

        asset_meta = manifest.assets[scene_id]
        obj = con.execute(
            "SELECT * FROM media_objects WHERE asset_id=?", (asset_meta.asset_id,)
        ).fetchone()
        if obj is None:
            raise MediaAccessError(
                404, "MEDIA_ASSET_NOT_FOUND", f"Asset '{asset_meta.asset_id}' not registered"
            )
        if obj["status"] not in {"approved", "published"}:
            raise MediaAccessError(
                403,
                "RIGHTS_ASSET_QUARANTINED",
                f"Asset '{asset_meta.asset_id}' status is '{obj['status']}'",
            )

    token, exp = mint_media_token(
        secret=secret,
        actor_id=principal.actor_id,
        session_id=principal.session_id,
        asset_id=obj["asset_id"],
        work_id=work_id,
        edition_id=target_edition,
        scene_id=scene_id,
        action=action,
        territory=territory,
        rights_version=manifest.grant.version,
        cache_epoch=int(obj["cache_epoch"]),
        now=check_time,
        ttl_seconds=ttl_seconds,
    )
    log_media_delivery(
        db_path,
        actor_id=principal.actor_id,
        asset_id=obj["asset_id"],
        action=f"authorize_{action}",
        status_code=200,
        detail=f"Issued signed {action} token ttl={ttl_seconds}s",
    )
    return {
        "asset_id": obj["asset_id"],
        "work_id": work_id,
        "edition_id": target_edition,
        "scene_id": scene_id,
        "action": action,
        "url": f"/api/v1/media/{obj['asset_id']}?token={token}",
        "token": token,
        "expires_at": exp.isoformat(),
        "ttl_seconds": ttl_seconds,
        "sha256": obj["sha256"],
        "byte_size": obj["byte_size"],
    }


def _parse_range_header(range_header: str, file_size: int) -> tuple[int, int]:
    m = re.fullmatch(r"bytes=(\d*)-(\d*)", range_header.strip())
    if not m or file_size <= 0:
        raise MediaAccessError(416, "INVALID_BYTE_RANGE", "Malformed Range header")
    start_s, end_s = m.groups()
    if not start_s and not end_s:
        raise MediaAccessError(416, "INVALID_BYTE_RANGE", "Empty Range bounds")
    if not start_s:
        # Suffix range: bytes=-N
        suffix_len = int(end_s)
        if suffix_len <= 0:
            raise MediaAccessError(416, "INVALID_BYTE_RANGE", "Invalid suffix length")
        start = max(0, file_size - suffix_len)
        end = file_size - 1
    else:
        start = int(start_s)
        end = int(end_s) if end_s else file_size - 1
    if start < 0 or start >= file_size or end < start:
        raise MediaAccessError(
            416, "RANGE_NOT_SATISFIABLE", f"Range {range_header} out of bounds for {file_size}"
        )
    return start, min(end, file_size - 1)


def deliver_signed_media(
    db_path: Path,
    *,
    secret: str,
    manifest: RightsManifest,
    media_dir: Path,
    asset_id: str,
    token: str,
    caller_actor_id: str | None = None,
    range_header: str | None = None,
    require_entitlement: bool = False,
    now: datetime | None = None,
) -> ByteRangeSlice:
    check_time = now or datetime.now(UTC)
    parts = token.split(".")
    if len(parts) != 2:
        raise MediaAccessError(401, "MEDIA_TOKEN_MALFORMED", "Malformed media token")
    payload_b64, sig_b64 = parts
    expected_sig = _b64url_encode(
        hmac.new(secret.encode("utf-8"), payload_b64.encode("ascii"), hashlib.sha256).digest()
    )
    if not hmac.compare_digest(sig_b64, expected_sig):
        raise MediaAccessError(401, "MEDIA_TOKEN_INVALID_SIGNATURE", "Invalid media token signature")

    try:
        claims = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
    except Exception as exc:
        raise MediaAccessError(401, "MEDIA_TOKEN_MALFORMED", "Invalid token payload") from exc

    exp_ts = int(claims.get("exp", 0))
    now_ts = int(check_time.timestamp())
    if exp_ts <= now_ts:
        raise MediaAccessError(401, "MEDIA_TOKEN_EXPIRED", "Signed media URL has expired")

    if claims.get("aid") != asset_id:
        raise MediaAccessError(
            403,
            "MEDIA_ASSET_MISMATCH",
            "Signed token is not valid for the requested asset_id",
        )

    token_actor = str(claims.get("sub") or "")
    if caller_actor_id is not None and caller_actor_id != token_actor:
        raise MediaAccessError(
            403,
            "MEDIA_ACTOR_MISMATCH",
            "Signed media URL belongs to a different user/actor",
        )

    token_sid = claims.get("sid")
    action: MediaAction = claims.get("act", "stream")
    scene_id = str(claims.get("scn") or "")
    edition_id = str(claims.get("eid") or "")
    territory = str(claims.get("ter") or "VN")
    token_rv = int(claims.get("rv", 0))
    token_ce = int(claims.get("ce", 0))

    with _connect(db_path) as con:
        # 1. If bound to an authenticated device session, verify session is still active
        if token_sid is not None:
            session = con.execute(
                "SELECT revoked_at, expires_at FROM device_sessions WHERE id=? AND user_id=?",
                (token_sid, token_actor),
            ).fetchone()
            if session is None or session["revoked_at"] is not None:
                raise MediaAccessError(
                    401,
                    "AUTH_SESSION_REVOKED",
                    "Device session was logged out or revoked",
                )

        # 2. Verify entitlement has not been revoked or expired since token issuance
        _check_entitlement(
            con,
            actor_id=token_actor,
            work_id=str(claims.get("wid") or ""),
            action=action,
            now=check_time,
            require_entitlement=require_entitlement,
        )

        # 3. Verify media_objects registry, cache_epoch, and rights_grant_version
        obj = con.execute(
            "SELECT * FROM media_objects WHERE asset_id=?", (asset_id,)
        ).fetchone()
        if obj is None:
            raise MediaAccessError(404, "MEDIA_ASSET_NOT_FOUND", f"Asset '{asset_id}' not found")
        if int(obj["cache_epoch"]) != token_ce:
            raise MediaAccessError(
                403,
                "MEDIA_CACHE_INVALIDATED",
                "Signed URL was invalidated by a cache/rights update",
            )
        if token_rv != manifest.grant.version or int(obj["rights_grant_version"]) != token_rv:
            raise MediaAccessError(
                403,
                "RIGHTS_VERSION_MISMATCH",
                "Signed URL rights grant version is stale",
            )
        if obj["status"] not in {"approved", "published"}:
            raise MediaAccessError(
                403,
                "RIGHTS_ASSET_QUARANTINED",
                f"Asset '{asset_id}' is in status '{obj['status']}'",
            )

    # 4. Revalidate rights at delivery time (catches takedowns, disputes, or expiry after mint)
    try:
        assert_permission(
            manifest,
            action,
            scene_id=scene_id,
            territory=territory,
            edition_id=edition_id,
            at_time=check_time,
        )
    except RightsViolationError as exc:
        log_media_delivery(
            db_path,
            actor_id=token_actor,
            asset_id=asset_id,
            action=f"deliver_{action}",
            status_code=403,
            detail=f"Blocked at delivery by rights gate: {exc.code}",
        )
        raise MediaAccessError(403, exc.code, exc.reason) from exc

    # 5. Resolve file safely with path traversal guard
    base_dir = media_dir.resolve()
    file_path = (base_dir / obj["storage_relpath"]).resolve()
    if not file_path.is_relative_to(base_dir) or not file_path.is_file():
        raise MediaAccessError(404, "MEDIA_FILE_MISSING", "Underlying media file unavailable")

    raw_bytes = file_path.read_bytes()
    total_size = len(raw_bytes)
    remaining_ttl = max(0, exp_ts - now_ts)
    disposition = "attachment" if action == "offline" else "inline"
    common_headers = {
        "Accept-Ranges": "bytes",
        "Cache-Control": f"private, max-age={remaining_ttl}, must-revalidate",
        "Content-Disposition": f'{disposition}; filename="{asset_id}.mp3"',
        "ETag": f'"{obj["sha256"]}"',
        "X-Content-Type-Options": "nosniff",
    }

    if range_header:
        start, end = _parse_range_header(range_header, total_size)
        chunk = raw_bytes[start : end + 1]
        headers = {
            **common_headers,
            "Content-Range": f"bytes {start}-{end}/{total_size}",
            "Content-Length": str(len(chunk)),
        }
        log_media_delivery(
            db_path,
            actor_id=token_actor,
            asset_id=asset_id,
            action="deliver_range",
            status_code=206,
            bytes_served=len(chunk),
            detail=f"Served bytes {start}-{end}/{total_size}",
        )
        return ByteRangeSlice(
            data=chunk,
            status_code=206,
            content_type=obj["content_type"],
            headers=headers,
            bytes_served=len(chunk),
        )

    headers = {
        **common_headers,
        "Content-Length": str(total_size),
    }
    log_media_delivery(
        db_path,
        actor_id=token_actor,
        asset_id=asset_id,
        action=f"deliver_{action}",
        status_code=200,
        bytes_served=total_size,
        detail=f"Served full {action} asset ({total_size} bytes)",
    )
    return ByteRangeSlice(
        data=raw_bytes,
        status_code=200,
        content_type=obj["content_type"],
        headers=headers,
        bytes_served=total_size,
    )
