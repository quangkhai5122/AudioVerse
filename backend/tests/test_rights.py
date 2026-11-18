from __future__ import annotations

import copy
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from audioverse.content import (
    assert_permission,
    read_json,
    validate_rights_manifest,
)
from audioverse.main import create_app
from audioverse.rights import (
    AssetLicense,
    ChainOfTitle,
    ContractEvidence,
    RightsGrant,
    RightsViolationError,
    approve_grant,
    assert_rights,
    begin_review,
    renewal_warning_level,
    submit_evidence,
    trigger_dispute_hold,
    trigger_takedown,
)
from audioverse.settings import ROOT, Settings
from fastapi.testclient import TestClient

SHA_OK = "a" * 64


def _make_base_grant(
    *,
    source_type: str = "licensed_text",
    actions: list[str] | None = None,
    submitter_id: str = "creator-linh",
    state: str = "DRAFT",
    valid_from: datetime | None = None,
    expires_at: datetime | None = None,
) -> RightsGrant:
    now = datetime(2026, 11, 18, 0, 0, tzinfo=UTC)
    granted = actions or ["stream"]
    denied = [a for a in ("voice_clone", "training") if a not in granted]
    return RightsGrant(
        grant_id="grant-001",
        version=1,
        work_id="work-001",
        edition_id="work-001-ed1",
        source_type=source_type,  # type: ignore[arg-type]
        submitter_id=submitter_id,
        state=state,  # type: ignore[arg-type]
        granted_actions=granted,  # type: ignore[arg-type]
        denied_actions=denied,  # type: ignore[arg-type]
        territories=["VN"],
        languages=["vi-VN"],
        valid_from=valid_from or (now - timedelta(days=10)),
        expires_at=expires_at or (now + timedelta(days=90)),
        chain_of_title=ChainOfTitle(
            literary_author="Nguyễn Văn A",
            economic_rights_holder="Studio Truyện Việt",
            source_language="vi-VN",
            is_translated=False,
            adaptation_holder="Studio Truyện Việt",
            performer_holder="Nghệ sĩ Thu Hà",
            master_recording_holder="Studio Truyện Việt",
            voice_consent_holder=None,
            attribution_text="Tác giả Nguyễn Văn A · Giọng đọc Thu Hà",
            voice_label="human_narrated",
        ),
        evidence=ContractEvidence(
            evidence_id="ev-001",
            contract_version=1,
            document_sha256=SHA_OK,
            submitted_by=submitter_id,
            submitted_at=now - timedelta(days=11),
            source_url="https://contracts.internal.example/ev-001.pdf",
        ),
    )


def _approve_for_prod(grant: RightsGrant, reviewer_id: str = "reviewer-minh") -> RightsGrant:
    step1 = submit_evidence(grant, grant.submitter_id, grant.evidence)
    step2 = begin_review(step1, reviewer_id, "legal_reviewer")
    return approve_grant(
        step2,
        audit_id="audit-001",
        reviewer_id=reviewer_id,
        reviewer_role="legal_reviewer",
        note="Verified signed chain-of-title contract v1",
        decided_at=datetime(2026, 11, 18, 1, 0, tzinfo=UTC),
        production_approval=True,
        publish_immediately=True,
    )


def test_demo_manifest_validates_all_11_scene_asset_digests():
    story = read_json(ROOT / "content/demo_story/story.json")
    raw = read_json(ROOT / "content/licenses/demo_license.json")
    manifest = validate_rights_manifest(raw, story=story, media_dir=ROOT / "media/demo")
    assert len(manifest.assets) == 11
    decision = assert_permission(
        manifest,
        "stream",
        scene_id="s0",
        territory="VN",
        language="vi-VN",
        edition_id="ben-kia-canh-cua-ed1",
    )
    assert decision.allowed is True
    with pytest.raises(RightsViolationError) as exc:
        assert_permission(manifest, "stream", require_production=True)
    assert exc.value.code == "RIGHTS_UNVERIFIED"


def test_stream_only_grant_denies_offline_derivative_tts_and_voice_clone():
    grant = _approve_for_prod(_make_base_grant(actions=["stream"]))
    now = datetime(2026, 11, 18, 2, 0, tzinfo=UTC)
    assert assert_rights(grant, "stream", territory="VN", at_time=now, require_production=True).allowed
    for forbidden in ("offline", "derivative", "tts", "voice_clone", "training"):
        with pytest.raises(RightsViolationError) as exc:
            assert_rights(grant, forbidden, territory="VN", at_time=now, require_production=True)
        assert exc.value.code == "RIGHTS_ACTION_DENIED"


def test_maker_checker_blocks_creator_self_approval():
    grant = _make_base_grant(submitter_id="creator-linh")
    submitted = submit_evidence(grant, "creator-linh", grant.evidence)
    with pytest.raises(RightsViolationError) as exc:
        begin_review(submitted, "creator-linh", "legal_reviewer")
    assert exc.value.code == "RIGHTS_SELF_APPROVAL_FORBIDDEN"

    # Even if forced into a forged state, evaluate_rights fails closed on self-approval.
    forged = submitted.model_copy(
        update={
            "reviewer_id": "creator-linh",
            "state": "PUBLISHED",
            "production_approval": True,
        }
    )
    with pytest.raises(RightsViolationError) as exc2:
        assert_rights(forged, "stream", require_production=True)
    assert exc2.value.code == "RIGHTS_SELF_APPROVAL_FORBIDDEN"


def test_chain_of_title_gates_translation_derivative_human_and_voice_clone():
    # 1. Translated work missing translation_holder
    g_trans = _make_base_grant(actions=["stream"])
    g_trans = g_trans.model_copy(
        update={
            "chain_of_title": g_trans.chain_of_title.model_copy(
                update={"is_translated": True, "translation_holder": None}
            )
        }
    )
    s_trans = begin_review(
        submit_evidence(g_trans, g_trans.submitter_id, g_trans.evidence),
        "reviewer-1",
        "legal_reviewer",
    )
    with pytest.raises(RightsViolationError) as exc1:
        approve_grant(
            s_trans,
            audit_id="a1",
            reviewer_id="reviewer-1",
            reviewer_role="legal_reviewer",
            note="try approve",
        )
    assert exc1.value.code == "RIGHTS_MISSING_CHAIN_OF_TITLE"

    # 2. Derivative action missing adaptation_holder
    g_deriv = _make_base_grant(actions=["stream", "derivative"])
    g_deriv = g_deriv.model_copy(
        update={
            "chain_of_title": g_deriv.chain_of_title.model_copy(
                update={"adaptation_holder": None}
            )
        }
    )
    s_deriv = begin_review(
        submit_evidence(g_deriv, g_deriv.submitter_id, g_deriv.evidence),
        "reviewer-1",
        "legal_reviewer",
    )
    with pytest.raises(RightsViolationError) as exc2:
        approve_grant(
            s_deriv,
            audit_id="a2",
            reviewer_id="reviewer-1",
            reviewer_role="legal_reviewer",
            note="try approve",
        )
    assert exc2.value.code == "RIGHTS_MISSING_CHAIN_OF_TITLE"

    # 3. Human narration missing performer_holder
    g_human = _make_base_grant(source_type="human_narration", actions=["stream"])
    g_human = g_human.model_copy(
        update={
            "chain_of_title": g_human.chain_of_title.model_copy(
                update={"performer_holder": None}
            )
        }
    )
    s_human = begin_review(
        submit_evidence(g_human, g_human.submitter_id, g_human.evidence),
        "reviewer-1",
        "legal_reviewer",
    )
    with pytest.raises(RightsViolationError) as exc3:
        approve_grant(
            s_human,
            audit_id="a3",
            reviewer_id="reviewer-1",
            reviewer_role="legal_reviewer",
            note="try approve",
        )
    assert exc3.value.code == "RIGHTS_MISSING_CHAIN_OF_TITLE"

    # 4. Voice cloning without explicit voice_consent_holder
    g_voice = _make_base_grant(actions=["stream", "voice_clone"])
    g_voice = g_voice.model_copy(update={"denied_actions": ["training"]})
    s_voice = begin_review(
        submit_evidence(g_voice, g_voice.submitter_id, g_voice.evidence),
        "reviewer-1",
        "legal_reviewer",
    )
    with pytest.raises(RightsViolationError) as exc4:
        approve_grant(
            s_voice,
            audit_id="a4",
            reviewer_id="reviewer-1",
            reviewer_role="legal_reviewer",
            note="try approve",
        )
    assert exc4.value.code == "RIGHTS_VOICE_CONSENT_REQUIRED"


def test_prohibited_public_scrape_urls_rejected():
    now = datetime(2026, 11, 18, 0, 0, tzinfo=UTC)
    for bad_url in (
        "https://www.youtube.com/watch?v=abc123",
        "https://youtu.be/abc123",
        "https://www.tiktok.com/@user/video/123",
        "https://soundcloud.com/artist/track",
        "https://example.com/podcast/feed.rss",
    ):
        with pytest.raises(RightsViolationError) as exc:
            ContractEvidence(
                evidence_id="ev-bad",
                contract_version=1,
                document_sha256=SHA_OK,
                submitted_by="creator-1",
                submitted_at=now,
                source_url=bad_url,
            )
        assert exc.value.code == "RIGHTS_UNAUTHORIZED_SOURCE_URL"


def test_territory_language_edition_expiry_and_renewal_warnings():
    start = datetime(2026, 11, 1, 0, 0, tzinfo=UTC)
    end = datetime(2026, 12, 31, 0, 0, tzinfo=UTC)
    grant = _approve_for_prod(_make_base_grant(valid_from=start, expires_at=end))

    # Not yet valid
    with pytest.raises(RightsViolationError) as exc_early:
        assert_rights(
            grant,
            "stream",
            at_time=start - timedelta(seconds=1),
            require_production=True,
        )
    assert exc_early.value.code == "RIGHTS_NOT_YET_VALID"

    # Expired
    with pytest.raises(RightsViolationError) as exc_exp:
        assert_rights(grant, "stream", at_time=end, require_production=True)
    assert exc_exp.value.code == "RIGHTS_EXPIRED"

    # Territory mismatch
    with pytest.raises(RightsViolationError) as exc_terr:
        assert_rights(
            grant,
            "stream",
            territory="US",
            at_time=start + timedelta(days=5),
            require_production=True,
        )
    assert exc_terr.value.code == "RIGHTS_TERRITORY_DENIED"

    # Language mismatch
    with pytest.raises(RightsViolationError) as exc_lang:
        assert_rights(
            grant,
            "stream",
            language="en-US",
            at_time=start + timedelta(days=5),
            require_production=True,
        )
    assert exc_lang.value.code == "RIGHTS_LANGUAGE_DENIED"

    # Edition mismatch
    with pytest.raises(RightsViolationError) as exc_ed:
        assert_rights(
            grant,
            "stream",
            edition_id="wrong-edition",
            at_time=start + timedelta(days=5),
            require_production=True,
        )
    assert exc_ed.value.code == "RIGHTS_EDITION_MISMATCH"

    # 60 / 30 / 7 day renewal warnings
    assert renewal_warning_level(grant, end - timedelta(days=45)) == "60_DAYS"
    assert renewal_warning_level(grant, end - timedelta(days=20)) == "30_DAYS"
    assert renewal_warning_level(grant, end - timedelta(days=5)) == "7_DAYS"
    assert renewal_warning_level(grant, end) == "EXPIRED"


def test_takedown_dispute_and_quarantined_asset_freeze_access():
    grant = _approve_for_prod(_make_base_grant(actions=["stream", "offline", "derivative"]))
    now = datetime(2026, 11, 18, 3, 0, tzinfo=UTC)

    quarantined_asset = AssetLicense(
        asset_id="asset-q1",
        work_id=grant.work_id,
        edition_id=grant.edition_id,
        scene_id="s0",
        source_type="synthetic_tts",
        sha256=SHA_OK,
        rights_grant_id=grant.grant_id,
        rights_grant_version=grant.version,
        status="quarantine",
    )
    with pytest.raises(RightsViolationError) as exc_q:
        assert_rights(grant, "stream", asset=quarantined_asset, at_time=now, require_production=True)
    assert exc_q.value.code == "RIGHTS_ASSET_QUARANTINED"

    disputed = trigger_dispute_hold(
        grant,
        audit_id="audit-disp-1",
        reviewer_id="reviewer-minh",
        reviewer_role="rights_officer",
        reason="Third-party authorship claim under investigation",
        decided_at=now,
    )
    with pytest.raises(RightsViolationError) as exc_d:
        assert_rights(disputed, "stream", at_time=now, require_production=True)
    assert exc_d.value.code == "RIGHTS_DISPUTE_HOLD"

    taken_down = trigger_takedown(
        grant,
        audit_id="audit-td-1",
        reviewer_id="reviewer-minh",
        reviewer_role="compliance_admin",
        reason="Contract terminated by rights holder",
        decided_at=now,
    )
    for action in ("stream", "offline", "derivative"):
        with pytest.raises(RightsViolationError) as exc_td:
            assert_rights(taken_down, action, at_time=now, require_production=True)
        assert exc_td.value.code == "RIGHTS_TAKEDOWN_ACTIVE"
    assert taken_down.audit_log[-1].decision == "TAKEDOWN"


def test_api_rights_endpoint_and_takedown_or_quarantine_enforcement(tmp_path: Path):
    raw = read_json(ROOT / "content/licenses/demo_license.json")

    # 1. Default demo app exposes provenance & attribution
    cfg_ok = Settings(
        db_path=tmp_path / "ok.db",
        content_path=ROOT / "content/demo_story/story.json",
        license_path=ROOT / "content/licenses/demo_license.json",
        media_path=ROOT / "media/demo",
        web_path=ROOT / "web",
    )
    with TestClient(create_app(cfg_ok)) as client:
        cat = client.get("/api/v1/catalog").json()[0]
        assert cat["attribution"] == "Tác phẩm gốc AudioVerse · Giọng tổng hợp kỹ thuật (eSpeak)"
        assert cat["voice_label"] == "synthetic_tts"
        rights_resp = client.get("/api/v1/works/ben-kia-canh-cua/rights")
        assert rights_resp.status_code == 200
        body = rights_resp.json()
        assert body["grant_id"] == "original-demo-2026"
        assert body["asset_count"] == 11
        assert body["production_approval"] is False

    # 2. Quarantined scene asset blocks streaming with 403 while other scenes still stream
    quarantined_manifest = copy.deepcopy(raw)
    quarantined_manifest["assets"]["s0"]["status"] = "quarantine"
    lic_path = tmp_path / "quarantined_license.json"
    lic_path.write_text(json.dumps(quarantined_manifest, ensure_ascii=False), encoding="utf-8")
    cfg_q = Settings(
        db_path=tmp_path / "q.db",
        content_path=ROOT / "content/demo_story/story.json",
        license_path=lic_path,
        media_path=ROOT / "media/demo",
        web_path=ROOT / "web",
    )
    with TestClient(create_app(cfg_q)) as client_q:
        r_s0 = client_q.get("/api/v1/audio/s0.mp3")
        assert r_s0.status_code == 403
        assert r_s0.json()["detail"]["code"] == "RIGHTS_ASSET_QUARANTINED"
        assert client_q.get("/api/v1/audio/s1.mp3").status_code == 200

    # 3. Corrupted MP3 digest fails closed at startup validation
    bad_digest_manifest = copy.deepcopy(raw)
    bad_digest_manifest["assets"]["s0"]["sha256"] = "0" * 64
    bad_lic_path = tmp_path / "bad_digest.json"
    bad_lic_path.write_text(json.dumps(bad_digest_manifest, ensure_ascii=False), encoding="utf-8")
    cfg_bad = Settings(
        db_path=tmp_path / "bad.db",
        content_path=ROOT / "content/demo_story/story.json",
        license_path=bad_lic_path,
        media_path=ROOT / "media/demo",
        web_path=ROOT / "web",
    )
    with pytest.raises(RightsViolationError) as exc_bad:
        create_app(cfg_bad)
    assert exc_bad.value.code == "RIGHTS_EVIDENCE_MISMATCH"
