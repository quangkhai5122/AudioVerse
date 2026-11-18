from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from audioverse.main import create_app
from audioverse.media import grant_entitlement, revoke_entitlement
from audioverse.settings import ROOT, Settings
from fastapi.testclient import TestClient


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_library_follow_toggle_progress_writeback_and_continue_listening(tmp_path: Path):
    cfg = Settings(
        db_path=tmp_path / "lifecycle1.db",
        content_path=ROOT / "content/demo_story/story.json",
        license_path=ROOT / "content/licenses/demo_license.json",
        media_path=ROOT / "media/demo",
        web_path=ROOT / "web",
        allow_demo_header=False,
    )
    with TestClient(create_app(cfg)) as client:
        user = client.post(
            "/api/v1/auth/register",
            json={
                "email": "listener@example.com",
                "password": "Password12345!",
                "display_name": "Listener",
            },
        ).json()
        hdr = _bearer(user["access_token"])

        # LIB-01: Repeated follow/unfollow toggles reconcile deterministically
        f1 = client.post(
            "/api/v1/me/library/ben-kia-canh-cua",
            json={"followed": True},
            headers=hdr,
        )
        assert f1.status_code == 200 and f1.json()["followed"] is True
        f2 = client.post(
            "/api/v1/me/library/ben-kia-canh-cua",
            json={"followed": True},
            headers=hdr,
        )
        assert f2.status_code == 200 and f2.json()["followed"] is True
        lib_items = client.get("/api/v1/me/library", headers=hdr).json()
        assert len(lib_items) == 1

        f3 = client.post(
            "/api/v1/me/library/ben-kia-canh-cua",
            json={"followed": False},
            headers=hdr,
        )
        assert f3.status_code == 200 and f3.json()["followed"] is False
        assert client.get("/api/v1/me/library", headers=hdr).json() == []

        # PLY-08 / PLY-05 / INT-12 / LIB-02: Start run, write back position & speed, and resume
        run = client.post(
            "/api/v1/runs",
            json={"story_id": "ben-kia-canh-cua"},
            headers=hdr,
        ).json()
        rid = run["run_id"]
        assert run["position_ms"] == 0
        assert run["playback_speed"] == 1.0

        saved = client.post(
            f"/api/v1/runs/{rid}/progress",
            json={"scene_id": "s0", "position_ms": 8450, "playback_speed": 1.25},
            headers=hdr,
        )
        assert saved.status_code == 200
        assert saved.json()["position_ms"] == 8450
        assert saved.json()["playback_speed"] == 1.25

        # Saving progress on a mismatched scene returns 409
        bad_scene = client.post(
            f"/api/v1/runs/{rid}/progress",
            json={"scene_id": "s1", "position_ms": 1000, "playback_speed": 1.0},
            headers=hdr,
        )
        assert bad_scene.status_code == 409

        # Continue-listening returns the exact committed scene, position_ms, and speed
        cont = client.get("/api/v1/me/continue-listening", headers=hdr)
        assert cont.status_code == 200
        assert len(cont.json()) == 1
        assert cont.json()[0]["run_id"] == rid
        assert cont.json()[0]["position_ms"] == 8450
        assert cont.json()[0]["playback_speed"] == 1.25

        # Advancing to next scene resets position_ms to 0 while keeping playback_speed
        advanced = client.post(
            f"/api/v1/runs/{rid}/choices",
            json={
                "choice_id": "follow-tracks",
                "expected_version": 0,
                "idempotency_key": "progress-reset-key-01",
            },
            headers=hdr,
        )
        assert advanced.status_code == 200
        assert advanced.json()["scene"]["id"] == "s1"
        assert advanced.json()["position_ms"] == 0
        assert advanced.json()["playback_speed"] == 1.25


def test_offline_download_lease_quota_metadata_and_expiry_revalidation(tmp_path: Path):
    db_file = tmp_path / "lifecycle2.db"
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
                "email": "offline@example.com",
                "password": "Password12345!",
                "display_name": "Offline User",
            },
        ).json()
        uid = user["user"]["id"]
        hdr = _bearer(user["access_token"])

        ent = grant_entitlement(
            db_file,
            user_id=uid,
            work_id="ben-kia-canh-cua",
            allow_stream=True,
            allow_offline=True,
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )

        # PLY-11: Exceeding storage quota fails closed
        quota_fail = client.post(
            "/api/v1/downloads/leases",
            json={
                "work_id": "ben-kia-canh-cua",
                "scene_id": "s0",
                "max_quota_bytes": 2048,
            },
            headers=hdr,
        )
        assert quota_fail.status_code == 403
        assert quota_fail.json()["detail"]["code"] == "OFFLINE_STORAGE_QUOTA_EXCEEDED"

        # PLY-10 / PLY-18: Issue valid offline lease with scene metadata & transcript
        lease_resp = client.post(
            "/api/v1/downloads/leases",
            json={
                "work_id": "ben-kia-canh-cua",
                "scene_id": "s0",
                "lease_hours": 24,
            },
            headers=hdr,
        )
        assert lease_resp.status_code == 201
        lease = lease_resp.json()
        assert lease["scene_id"] == "s0"
        assert "Mưa rơi trên mái tôn" in lease["transcript"]
        assert lease["attribution"]
        lease_id = lease["lease_id"]

        # Validate offline lease succeeds while license and cache_epoch are valid
        val_ok = client.get(
            f"/api/v1/downloads/leases/{lease_id}/validate",
            headers=hdr,
        )
        assert val_ok.status_code == 200
        assert val_ok.json()["valid"] is True

        # Revoking entitlement does not allow new offline download URL access
        revoke_entitlement(db_file, entitlement_id=ent["id"])
        dl_blocked = client.get(lease["download_url"], headers=hdr)
        assert dl_blocked.status_code == 403
        assert dl_blocked.json()["detail"]["code"] == "ENTITLEMENT_EXPIRED"
