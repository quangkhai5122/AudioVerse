from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta
from pathlib import Path

from audioverse.auth import register_user
from audioverse.main import create_app
from audioverse.media import (
    grant_entitlement,
    mint_media_token,
    revoke_entitlement,
)
from audioverse.settings import ROOT, Settings
from audioverse.storage import _connect
from fastapi.testclient import TestClient


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_signed_media_authorize_full_and_range_delivery_and_cache_headers(tmp_path: Path):
    cfg = Settings(
        db_path=tmp_path / "media1.db",
        content_path=ROOT / "content/demo_story/story.json",
        license_path=ROOT / "content/licenses/demo_license.json",
        media_path=ROOT / "media/demo",
        web_path=ROOT / "web",
        allow_demo_header=False,
        allow_public_sample_audio=False,
    )
    with TestClient(create_app(cfg)) as client:
        # Public sample route is disabled when allow_public_sample_audio=False
        pub_resp = client.get("/api/v1/audio/s0.mp3")
        assert pub_resp.status_code == 403
        assert pub_resp.json()["detail"]["code"] == "PUBLIC_SAMPLE_ROUTE_DISABLED"

        # Register user and request playback authorization
        user = client.post(
            "/api/v1/auth/register",
            json={
                "email": "listener@example.com",
                "password": "Password12345!",
                "display_name": "Listener",
            },
        ).json()
        hdr = _bearer(user["access_token"])

        auth_resp = client.post(
            "/api/v1/playback/authorize",
            json={
                "work_id": "ben-kia-canh-cua",
                "scene_id": "s0",
                "action": "stream",
                "territory": "VN",
                "ttl_seconds": 180,
            },
            headers=hdr,
        )
        assert auth_resp.status_code == 200
        grant_data = auth_resp.json()
        assert grant_data["asset_id"] == "demo-audio-s0"
        signed_url = grant_data["url"]

        # Full 200 OK delivery with private cache headers
        full_resp = client.get(signed_url, headers=hdr)
        assert full_resp.status_code == 200
        assert full_resp.headers["content-type"].startswith("audio/mpeg")
        assert "private" in full_resp.headers["cache-control"]
        assert "must-revalidate" in full_resp.headers["cache-control"]
        assert full_resp.headers["x-content-type-options"] == "nosniff"
        assert (
            hashlib.sha256(full_resp.content).hexdigest()
            == grant_data["sha256"]
        )

        # HTTP Range 206 Partial Content delivery
        range_resp = client.get(
            signed_url,
            headers={**hdr, "Range": "bytes=0-31"},
        )
        assert range_resp.status_code == 206
        assert len(range_resp.content) == 32
        assert range_resp.content == full_resp.content[:32]
        assert range_resp.headers["content-range"] == f"bytes 0-31/{grant_data['byte_size']}"

        # Out-of-bounds Range returns 416
        bad_range = client.get(
            signed_url,
            headers={**hdr, "Range": "bytes=9999999-99999999"},
        )
        assert bad_range.status_code == 416


def test_signed_media_rejects_expired_tampered_cross_asset_cross_user_and_logged_out_tokens(
    tmp_path: Path,
):
    db_file = tmp_path / "media2.db"
    cfg = Settings(
        db_path=db_file,
        content_path=ROOT / "content/demo_story/story.json",
        license_path=ROOT / "content/licenses/demo_license.json",
        media_path=ROOT / "media/demo",
        web_path=ROOT / "web",
        allow_demo_header=False,
    )
    with TestClient(create_app(cfg)) as client:
        alice = client.post(
            "/api/v1/auth/register",
            json={
                "email": "alice@example.com",
                "password": "Password12345!",
                "display_name": "Alice",
            },
        ).json()
        bob = client.post(
            "/api/v1/auth/register",
            json={
                "email": "bob@example.com",
                "password": "Password12345!",
                "display_name": "Bob",
            },
        ).json()
        alice_hdr = _bearer(alice["access_token"])
        bob_hdr = _bearer(bob["access_token"])

        auth_data = client.post(
            "/api/v1/playback/authorize",
            json={"work_id": "ben-kia-canh-cua", "scene_id": "s0"},
            headers=alice_hdr,
        ).json()
        token = auth_data["token"]

        # 1. Tampered signature -> 401
        tampered = token[:-4] + ("aaaa" if not token.endswith("aaaa") else "bbbb")
        r_tamp = client.get(f"/api/v1/media/demo-audio-s0?token={tampered}")
        assert r_tamp.status_code == 401
        assert r_tamp.json()["detail"]["code"] == "MEDIA_TOKEN_INVALID_SIGNATURE"
        assert r_tamp.headers["cache-control"] == "no-store"

        # 2. Expired token -> 401
        exp_token, _ = mint_media_token(
            secret=cfg.auth_secret,
            actor_id=alice["user"]["id"],
            session_id=alice["session_id"],
            asset_id="demo-audio-s0",
            work_id="ben-kia-canh-cua",
            edition_id="ben-kia-canh-cua-ed1",
            scene_id="s0",
            action="stream",
            territory="VN",
            rights_version=1,
            cache_epoch=1,
            now=datetime.now(UTC) - timedelta(minutes=15),
            ttl_seconds=60,
        )
        r_exp = client.get(f"/api/v1/media/demo-audio-s0?token={exp_token}")
        assert r_exp.status_code == 401
        assert r_exp.json()["detail"]["code"] == "MEDIA_TOKEN_EXPIRED"

        # 3. Cross-asset substitution (using s0 token on s1) -> 403
        r_cross_asset = client.get(f"/api/v1/media/demo-audio-s1?token={token}")
        assert r_cross_asset.status_code == 403
        assert r_cross_asset.json()["detail"]["code"] == "MEDIA_ASSET_MISMATCH"

        # 4. Cross-user access (Bob using Alice's signed URL) -> 403
        r_cross_user = client.get(auth_data["url"], headers=bob_hdr)
        assert r_cross_user.status_code == 403
        assert r_cross_user.json()["detail"]["code"] == "MEDIA_ACTOR_MISMATCH"

        # 5. Logout revokes device session; Alice's signed URL stops working immediately
        client.post("/api/v1/auth/logout", headers=alice_hdr)
        r_logged_out = client.get(auth_data["url"])
        assert r_logged_out.status_code == 401
        assert r_logged_out.json()["detail"]["code"] == "AUTH_SESSION_REVOKED"


def test_entitlement_gates_stream_vs_offline_and_cache_invalidation(tmp_path: Path):
    db_file = tmp_path / "media3.db"
    cfg = Settings(
        db_path=db_file,
        content_path=ROOT / "content/demo_story/story.json",
        license_path=ROOT / "content/licenses/demo_license.json",
        media_path=ROOT / "media/demo",
        web_path=ROOT / "web",
        allow_demo_header=False,
        require_entitlement=True,
    )
    with TestClient(create_app(cfg)) as client:
        user = client.post(
            "/api/v1/auth/register",
            json={
                "email": "sub@example.com",
                "password": "Password12345!",
                "display_name": "Subscriber",
            },
        ).json()
        uid = user["user"]["id"]
        hdr = _bearer(user["access_token"])

        # 1. Without entitlement, playback/authorize is denied (403 ENTITLEMENT_REQUIRED)
        no_ent = client.post(
            "/api/v1/playback/authorize",
            json={"work_id": "ben-kia-canh-cua", "scene_id": "s0", "action": "stream"},
            headers=hdr,
        )
        assert no_ent.status_code == 403
        assert no_ent.json()["detail"]["code"] == "ENTITLEMENT_REQUIRED"

        # 2. Grant stream-only entitlement -> stream succeeds, offline is denied
        ent_stream = grant_entitlement(
            db_file,
            user_id=uid,
            work_id="ben-kia-canh-cua",
            allow_stream=True,
            allow_offline=False,
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
        ok_stream = client.post(
            "/api/v1/playback/authorize",
            json={"work_id": "ben-kia-canh-cua", "scene_id": "s0", "action": "stream"},
            headers=hdr,
        )
        assert ok_stream.status_code == 200
        stream_url = ok_stream.json()["url"]

        deny_offline = client.post(
            "/api/v1/playback/authorize",
            json={"work_id": "ben-kia-canh-cua", "scene_id": "s0", "action": "offline"},
            headers=hdr,
        )
        assert deny_offline.status_code == 403
        assert deny_offline.json()["detail"]["code"] == "OFFLINE_ENTITLEMENT_REQUIRED"

        # 3. Revoking entitlement blocks already-minted signed URL at delivery time
        revoke_entitlement(db_file, entitlement_id=ent_stream["id"])
        blocked_after_revoke = client.get(stream_url, headers=hdr)
        assert blocked_after_revoke.status_code == 403
        assert blocked_after_revoke.json()["detail"]["code"] == "ENTITLEMENT_EXPIRED"

        # 4. Grant full stream+offline entitlement and test cache invalidation by staff
        grant_entitlement(
            db_file,
            user_id=uid,
            work_id="ben-kia-canh-cua",
            allow_stream=True,
            allow_offline=True,
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
        dl_auth = client.post(
            "/api/v1/playback/authorize",
            json={"work_id": "ben-kia-canh-cua", "scene_id": "s0", "action": "offline"},
            headers=hdr,
        )
        assert dl_auth.status_code == 200
        dl_url = dl_auth.json()["url"]

        dl_resp = client.get(dl_url, headers=hdr)
        assert dl_resp.status_code == 200
        assert dl_resp.headers["content-disposition"].startswith("attachment;")

        # Staff invalidates demo-audio-s0 cache epoch
        staff = register_user(
            db_file,
            secret=cfg.auth_secret,
            email="staff@example.com",
            password="Password12345!",
            display_name="Rights Officer",
            role="rights_officer",
        )
        inv = client.post(
            "/api/v1/admin/media/demo-audio-s0/invalidate",
            headers=_bearer(staff["access_token"]),
        )
        assert inv.status_code == 200
        assert inv.json()["cache_epoch"] == 2

        # Previously issued dl_url (cache_epoch=1) now fails closed with 403 MEDIA_CACHE_INVALIDATED
        stale_dl = client.get(dl_url, headers=hdr)
        assert stale_dl.status_code == 403
        assert stale_dl.json()["detail"]["code"] == "MEDIA_CACHE_INVALIDATED"

        # Verify delivery logs contain no story text or raw token secrets
        with _connect(db_file) as con:
            logs = con.execute("SELECT detail FROM media_delivery_logs").fetchall()
        assert len(logs) >= 5
        for row in logs:
            assert "Mưa rơi trên mái tôn" not in row["detail"]
