from __future__ import annotations

import copy
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from audioverse.auth import (
    mint_access_token,
    register_user,
    verify_security_audit_chain,
)
from audioverse.content import read_json
from audioverse.main import create_app
from audioverse.migrations import postgres_target_ddl
from audioverse.settings import ROOT, Settings
from audioverse.storage import _connect, get_run, init_db
from fastapi.testclient import TestClient


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_production_auth_mode_blocks_unauthenticated_and_isolates_tenants(tmp_path: Path):
    cfg = Settings(
        db_path=tmp_path / "auth.db",
        content_path=ROOT / "content/demo_story/story.json",
        license_path=ROOT / "content/licenses/demo_license.json",
        media_path=ROOT / "media/demo",
        web_path=ROOT / "web",
        allow_demo_header=False,
    )
    with TestClient(create_app(cfg)) as client:
        # ACC-01: Anonymous browse of free catalog and work metadata is allowed
        assert client.get("/api/v1/catalog").status_code == 200
        assert client.get("/api/v1/works/ben-kia-canh-cua").status_code == 200

        # SEC-01: Unauthenticated run creation is denied even if X-Demo-Actor is supplied
        unauth = client.post(
            "/api/v1/runs",
            json={"story_id": "ben-kia-canh-cua"},
            headers={"X-Demo-Actor": "spoofed-actor"},
        )
        assert unauth.status_code == 401
        assert unauth.json()["detail"]["code"] == "AUTH_REQUIRED"

        # ACC-02: Register Alice and Bob
        alice = client.post(
            "/api/v1/auth/register",
            json={
                "email": "alice@example.com",
                "password": "StrongPassword123!",
                "display_name": "Alice Nguyễn",
                "device_name": "Pixel 6",
            },
        ).json()
        bob = client.post(
            "/api/v1/auth/register",
            json={
                "email": "bob@example.com",
                "password": "StrongPassword456!",
                "display_name": "Bob Trần",
                "device_name": "Galaxy S24",
            },
        ).json()

        alice_hdr = _auth_header(alice["access_token"])
        bob_hdr = _auth_header(bob["access_token"])

        # Alice creates a run and makes a choice
        run_resp = client.post(
            "/api/v1/runs",
            json={"story_id": "ben-kia-canh-cua"},
            headers=alice_hdr,
        )
        assert run_resp.status_code == 201
        run_id = run_resp.json()["run_id"]
        assert run_resp.json()["edition_id"] == "ben-kia-canh-cua-ed1"

        c_resp = client.post(
            f"/api/v1/runs/{run_id}/choices",
            json={
                "choice_id": "follow-tracks",
                "expected_version": 0,
                "idempotency_key": "alice-choice-key-0001",
            },
            headers=alice_hdr,
        )
        assert c_resp.status_code == 200
        assert c_resp.json()["scene"]["id"] == "s1"

        # SEC-02 / SEC-14: Bob cannot read, mutate, view events, or restore Alice's run
        assert client.get(f"/api/v1/runs/{run_id}", headers=bob_hdr).status_code == 404
        assert (
            client.post(
                f"/api/v1/runs/{run_id}/choices",
                json={
                    "choice_id": "take-key",
                    "expected_version": 1,
                    "idempotency_key": "bob-attack-key-0001",
                },
                headers=bob_hdr,
            ).status_code
            == 404
        )
        assert client.get(f"/api/v1/runs/{run_id}/events", headers=bob_hdr).status_code == 404
        assert client.post(f"/api/v1/runs/{run_id}/restore", headers=bob_hdr).status_code == 404


def test_token_expiry_refresh_rotation_and_device_revocation(tmp_path: Path):
    db_file = tmp_path / "sessions.db"
    cfg = Settings(
        db_path=db_file,
        content_path=ROOT / "content/demo_story/story.json",
        license_path=ROOT / "content/licenses/demo_license.json",
        media_path=ROOT / "media/demo",
        web_path=ROOT / "web",
        allow_demo_header=False,
    )
    with TestClient(create_app(cfg)) as client:
        reg = client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "password": "Password12345!",
                "display_name": "Minh",
                "device_name": "Phone-1",
            },
        ).json()
        old_access = reg["access_token"]
        old_refresh = reg["refresh_token"]
        sid = reg["session_id"]
        uid = reg["user"]["id"]

        # Expired token is rejected
        expired_tok = mint_access_token(
            secret=cfg.auth_secret,
            user_id=uid,
            role="listener",
            session_id=sid,
            jti="any-jti",
            now=datetime.now(UTC) - timedelta(hours=2),
            ttl_seconds=60,
        )
        r_exp = client.get("/api/v1/me/devices", headers=_auth_header(expired_tok))
        assert r_exp.status_code == 401
        assert r_exp.json()["detail"]["code"] == "AUTH_TOKEN_EXPIRED"

        # Refresh rotates access_jti and refresh_token (ACC-04)
        refreshed = client.post(
            "/api/v1/auth/refresh",
            json={"session_id": sid, "refresh_token": old_refresh},
        )
        assert refreshed.status_code == 200
        new_access = refreshed.json()["access_token"]

        # Old access token is superseded immediately
        r_old = client.get("/api/v1/me/devices", headers=_auth_header(old_access))
        assert r_old.status_code == 401
        assert r_old.json()["detail"]["code"] == "AUTH_TOKEN_ROTATED"

        # New access token works
        devices = client.get("/api/v1/me/devices", headers=_auth_header(new_access))
        assert devices.status_code == 200
        assert len(devices.json()) == 1

        # Replaying old refresh token revokes the session immediately
        replay_ref = client.post(
            "/api/v1/auth/refresh",
            json={"session_id": sid, "refresh_token": old_refresh},
        )
        assert replay_ref.status_code == 401
        assert replay_ref.json()["detail"]["code"] == "AUTH_INVALID_REFRESH_TOKEN"

        # Now even new_access is rejected because session was revoked
        r_rev = client.get("/api/v1/me/devices", headers=_auth_header(new_access))
        assert r_rev.status_code == 401
        assert r_rev.json()["detail"]["code"] == "AUTH_SESSION_REVOKED"


def test_guest_migration_export_and_account_deletion(tmp_path: Path):
    cfg = Settings(
        db_path=tmp_path / "lifecycle.db",
        content_path=ROOT / "content/demo_story/story.json",
        license_path=ROOT / "content/licenses/demo_license.json",
        media_path=ROOT / "media/demo",
        web_path=ROOT / "web",
        allow_demo_header=True,
    )
    with TestClient(create_app(cfg)) as client:
        # Guest creates a run using X-Demo-Actor
        guest_run = client.post(
            "/api/v1/runs",
            json={"story_id": "ben-kia-canh-cua"},
            headers={"X-Demo-Actor": "guest-device-99"},
        ).json()
        run_id = guest_run["run_id"]

        # Register User A and User B
        user_a = client.post(
            "/api/v1/auth/register",
            json={
                "email": "lan@example.com",
                "password": "Password12345!",
                "display_name": "Lan",
            },
        ).json()
        user_b = client.post(
            "/api/v1/auth/register",
            json={
                "email": "hung@example.com",
                "password": "Password12345!",
                "display_name": "Hùng",
            },
        ).json()
        hdr_a = _auth_header(user_a["access_token"])
        hdr_b = _auth_header(user_b["access_token"])

        # ACC-03: Migrate guest-device-99 to User A
        mig1 = client.post(
            "/api/v1/me/migrate-guest",
            json={"guest_actor": "guest-device-99"},
            headers=hdr_a,
        )
        assert mig1.status_code == 200
        assert mig1.json()["migrated_runs"] == 1
        assert mig1.json()["already_migrated"] is False

        # Repeating migration for same user is idempotent
        mig2 = client.post(
            "/api/v1/me/migrate-guest",
            json={"guest_actor": "guest-device-99"},
            headers=hdr_a,
        )
        assert mig2.status_code == 200
        assert mig2.json()["already_migrated"] is True

        # User B cannot claim already-migrated guest
        mig_b = client.post(
            "/api/v1/me/migrate-guest",
            json={"guest_actor": "guest-device-99"},
            headers=hdr_b,
        )
        assert mig_b.status_code == 409

        # ACC-07: User A exports personal data and sees the migrated run
        exp = client.get("/api/v1/me/export", headers=hdr_a)
        assert exp.status_code == 200
        assert len(exp.json()["runs"]) == 1
        assert exp.json()["runs"][0]["run_id"] == run_id

        # ACC-06: User A deletes account; token is revoked and run is anonymized
        deleted = client.delete("/api/v1/me", headers=hdr_a)
        assert deleted.status_code == 200
        assert deleted.json()["anonymized_runs"] == 1
        assert client.get("/api/v1/me/export", headers=hdr_a).status_code == 401


def test_rbac_blocks_privilege_escalation_and_enforces_immutable_audit_and_events(
    tmp_path: Path,
):
    db_file = tmp_path / "rbac.db"
    cfg = Settings(
        db_path=db_file,
        content_path=ROOT / "content/demo_story/story.json",
        license_path=ROOT / "content/licenses/demo_license.json",
        media_path=ROOT / "media/demo",
        web_path=ROOT / "web",
        allow_demo_header=False,
    )
    with TestClient(create_app(cfg)) as client:
        listener = client.post(
            "/api/v1/auth/register",
            json={
                "email": "listener@example.com",
                "password": "Password12345!",
                "display_name": "Listener",
            },
        ).json()
        # Listener attempting staff audit route is denied and audited (ACC-10, SEC-12)
        denied = client.get(
            "/api/v1/admin/security-audit",
            headers=_auth_header(listener["access_token"]),
        )
        assert denied.status_code == 403
        assert denied.json()["detail"]["code"] == "RBAC_ROLE_DENIED"

        # Staff legal_reviewer can inspect security audit chain
        reviewer = register_user(
            db_file,
            secret=cfg.auth_secret,
            email="reviewer@example.com",
            password="Password12345!",
            display_name="Legal Reviewer",
            role="legal_reviewer",
        )
        allowed = client.get(
            "/api/v1/admin/security-audit",
            headers=_auth_header(reviewer["access_token"]),
        )
        assert allowed.status_code == 200
        assert allowed.json()["chain_valid"] is True
        assert verify_security_audit_chain(db_file) is True

        # Create a run + event, then verify DB triggers block UPDATE and DELETE on events & audit
        r = client.post(
            "/api/v1/runs",
            json={"story_id": "ben-kia-canh-cua"},
            headers=_auth_header(listener["access_token"]),
        ).json()
        client.post(
            f"/api/v1/runs/{r['run_id']}/choices",
            json={
                "choice_id": "follow-tracks",
                "expected_version": 0,
                "idempotency_key": "immut-check-0001",
            },
            headers=_auth_header(listener["access_token"]),
        )

        with _connect(db_file) as con:
            with pytest.raises(sqlite3.IntegrityError, match="append-only and immutable"):
                con.execute("UPDATE events SET to_scene='s9'")
            with pytest.raises(sqlite3.IntegrityError, match="append-only and immutable"):
                con.execute("DELETE FROM events")
            with pytest.raises(sqlite3.IntegrityError, match="append-only and immutable"):
                con.execute("UPDATE security_audit_log SET decision='ALLOW'")
            with pytest.raises(sqlite3.IntegrityError, match="append-only and immutable"):
                con.execute("DELETE FROM security_audit_log")


def test_edition_pinning_snapshot_replay_and_postgres_rls_ddl(tmp_path: Path):
    db_file = tmp_path / "replay.db"
    story_v1 = read_json(ROOT / "content/demo_story/story.json")
    story_v1["edition_id"] = "ben-kia-canh-cua-ed1"
    init_db(db_file, initial_story=story_v1)

    cfg = Settings(
        db_path=db_file,
        content_path=ROOT / "content/demo_story/story.json",
        license_path=ROOT / "content/licenses/demo_license.json",
        media_path=ROOT / "media/demo",
        web_path=ROOT / "web",
    )
    with TestClient(create_app(cfg)) as client:
        state = client.post("/api/v1/runs", json={"story_id": "ben-kia-canh-cua"}).json()
        rid = state["run_id"]
        for choice_id in ("follow-tracks", "take-key", "open-cellar"):
            state = client.post(
                f"/api/v1/runs/{rid}/choices",
                json={
                    "choice_id": choice_id,
                    "expected_version": state["version"],
                    "idempotency_key": f"key-{choice_id}-001",
                },
            ).json()
        assert state["scene"]["id"] == "s4"
        assert state["version"] == 3

        # INT-08: Even if a mutated story dict (edition v2) is passed to get_run,
        # the run resolves against its pinned edition_id ('ben-kia-canh-cua-ed1') stored in DB.
        mutated_story_v2 = copy.deepcopy(story_v1)
        mutated_story_v2["edition_id"] = "ben-kia-canh-cua-ed2"
        mutated_story_v2["scenes"]["s4"]["title"] = "TITLE FROM UNPINNED V2"
        pinned = get_run(db_file, mutated_story_v2, "demo-local", rid)
        assert pinned["edition_id"] == "ben-kia-canh-cua-ed1"
        assert pinned["scene"]["title"] == "Tầng hầm không có sóng"

        # INT-18: Deterministic replay restore verifies event hash chain and reproduces state
        restored = client.post(f"/api/v1/runs/{rid}/restore")
        assert restored.status_code == 200
        assert restored.json() == state

    ddl = postgres_target_ddl()
    assert "ENABLE ROW LEVEL SECURITY" in ddl
    assert "CREATE POLICY tenant_isolation_runs ON runs" in ddl
    assert "CREATE POLICY tenant_isolation_events ON events" in ddl
