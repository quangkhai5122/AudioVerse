"""Canonical rights provenance schema, maker-checker workflow, and fail-closed policy evaluator.

Enforces ADR-001 and ADR-007: stream, offline, derivative, tts, voice_clone, and training
are independent grants backed by chain-of-title and versioned contract evidence.
Creator self-approval and public platform scraping URLs are rejected.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, model_validator

RightAction = Literal["stream", "offline", "derivative", "tts", "voice_clone", "training"]
VALID_ACTIONS: set[str] = {"stream", "offline", "derivative", "tts", "voice_clone", "training"}

ReviewState = Literal[
    "DRAFT",
    "EVIDENCE_SUBMITTED",
    "UNDER_REVIEW",
    "APPROVED",
    "PUBLISHED",
    "EXPIRING",
    "EXPIRED",
    "REVOKED",
    "TAKEDOWN",
    "DISPUTED",
    "QUARANTINED",
]
ACTIVE_STATES: set[str] = {"APPROVED", "PUBLISHED", "EXPIRING"}

ReviewerRole = Literal["legal_reviewer", "rights_officer", "compliance_admin"]
SourceType = Literal["original_project", "licensed_text", "human_narration", "synthetic_tts"]
AssetStatus = Literal["quarantine", "approved", "published", "takedown", "disputed", "expired"]

PROHIBITED_SCRAPE_HOSTS: tuple[str, ...] = (
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
    "tiktok.com",
    "www.tiktok.com",
    "facebook.com",
    "www.facebook.com",
    "fb.watch",
    "soundcloud.com",
    "www.soundcloud.com",
    "spotify.com",
    "open.spotify.com",
)


class RightsSchemaError(ValueError):
    """Rights schema or provenance payload is invalid."""


class RightsViolationError(PermissionError):
    """Fail-closed rights policy denial with an auditable machine code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.reason = message


@dataclass(frozen=True)
class RightsDecision:
    allowed: bool
    code: str
    reason: str
    renewal_alert: str | None = None


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def check_prohibited_source_url(url: str | None) -> None:
    if not url:
        return
    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").lower()
    path = (parsed.path or "").lower()
    if any(host == h or host.endswith(f".{h}") for h in PROHIBITED_SCRAPE_HOSTS):
        raise RightsViolationError(
            "RIGHTS_UNAUTHORIZED_SOURCE_URL",
            f"Public streaming/social URL ({host}) is not a valid license or ingest source",
        )
    if path.endswith((".rss", ".xml", "/rss", "/feed")):
        raise RightsViolationError(
            "RIGHTS_UNAUTHORIZED_SOURCE_URL",
            "Public RSS/podcast feed URL is not a valid license grant",
        )


class ChainOfTitle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    literary_author: str = Field(min_length=1, max_length=256)
    economic_rights_holder: str = Field(min_length=1, max_length=256)
    source_language: str = Field(min_length=2, max_length=32, default="vi-VN")
    is_translated: bool = False
    translation_holder: str | None = None
    adaptation_holder: str | None = None
    performer_holder: str | None = None
    master_recording_holder: str | None = None
    voice_consent_holder: str | None = None
    attribution_text: str = Field(min_length=1, max_length=512)
    voice_label: Literal["human_narrated", "synthetic_tts"] = "synthetic_tts"


class ContractEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str = Field(min_length=1, max_length=128)
    contract_version: int = Field(ge=1)
    document_sha256: str = Field(pattern=r"^[a-fA-F0-9]{64}$")
    submitted_by: str = Field(min_length=1, max_length=128)
    submitted_at: datetime
    source_url: str | None = None
    notes: str = Field(default="", max_length=512)

    @model_validator(mode="after")
    def _validate_url(self) -> ContractEvidence:
        check_prohibited_source_url(self.source_url)
        return self


class ReviewAuditEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    audit_id: str = Field(min_length=1, max_length=128)
    reviewer_id: str = Field(min_length=1, max_length=128)
    reviewer_role: ReviewerRole
    decision: Literal["APPROVE", "REJECT", "TAKEDOWN", "DISPUTE_HOLD", "EXPIRE"]
    decided_at: datetime
    evidence_version: int = Field(ge=1)
    note: str = Field(min_length=1, max_length=512)


class RightsGrant(BaseModel):
    model_config = ConfigDict(extra="forbid")

    grant_id: str = Field(min_length=1, max_length=128)
    version: int = Field(ge=1)
    work_id: str = Field(min_length=1, max_length=128)
    edition_id: str = Field(min_length=1, max_length=128)
    source_type: SourceType
    submitter_id: str = Field(min_length=1, max_length=128)
    reviewer_id: str | None = None
    state: ReviewState = "DRAFT"
    granted_actions: list[RightAction]
    denied_actions: list[RightAction] = Field(default_factory=list)
    territories: list[str] = Field(min_length=1)
    languages: list[str] = Field(min_length=1)
    valid_from: datetime
    expires_at: datetime | None = None
    takedown_active: bool = False
    dispute_active: bool = False
    verified_for_demo: bool = False
    production_approval: bool = False
    chain_of_title: ChainOfTitle
    evidence: ContractEvidence
    audit_log: list[ReviewAuditEntry] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_window(self) -> RightsGrant:
        if self.expires_at is not None and _ensure_utc(self.expires_at) <= _ensure_utc(
            self.valid_from
        ):
            raise RightsSchemaError("expires_at must be strictly after valid_from")
        overlap = set(self.granted_actions) & set(self.denied_actions)
        if overlap:
            raise RightsSchemaError(f"Actions cannot be both granted and denied: {sorted(overlap)}")
        return self


class AssetLicense(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asset_id: str = Field(min_length=1, max_length=128)
    work_id: str = Field(min_length=1, max_length=128)
    edition_id: str = Field(min_length=1, max_length=128)
    scene_id: str | None = None
    source_type: Literal["human_narration", "synthetic_tts"]
    sha256: str = Field(pattern=r"^[a-fA-F0-9]{64}$")
    rights_grant_id: str = Field(min_length=1, max_length=128)
    rights_grant_version: int = Field(ge=1)
    status: AssetStatus = "quarantine"
    voice_owner_id: str | None = None
    master_owner_id: str | None = None
    model_version: str | None = None
    original_url: str | None = None

    @model_validator(mode="after")
    def _validate_url(self) -> AssetLicense:
        check_prohibited_source_url(self.original_url)
        return self


class RightsManifest(BaseModel):
    """Combined manifest supporting both legacy demo keys and canonical T002 provenance."""

    model_config = ConfigDict(extra="forbid")

    id: str
    content_id: str
    type: str
    rights_holder: str
    provenance: str
    verified_for_demo: bool
    permissions: list[RightAction]
    denied: list[RightAction]
    territory: str
    evidence: str
    production_approval: bool
    reviewer_note: str
    grant: RightsGrant
    assets: dict[str, AssetLicense] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check_consistency(self) -> RightsManifest:
        if self.id != self.grant.grant_id:
            raise RightsSchemaError("Manifest id must match grant.grant_id")
        if self.content_id != self.grant.work_id:
            raise RightsSchemaError("Manifest content_id must match grant.work_id")
        if set(self.permissions) != set(self.grant.granted_actions):
            raise RightsSchemaError("Manifest permissions must match grant.granted_actions")
        if set(self.denied) != set(self.grant.denied_actions):
            raise RightsSchemaError("Manifest denied must match grant.denied_actions")
        if self.verified_for_demo != self.grant.verified_for_demo:
            raise RightsSchemaError("Manifest verified_for_demo must match grant.verified_for_demo")
        if self.production_approval != self.grant.production_approval:
            raise RightsSchemaError(
                "Manifest production_approval must match grant.production_approval"
            )
        return self


def renewal_warning_level(grant: RightsGrant, at_time: datetime | None = None) -> str | None:
    """Return 60/30/7 day expiration warning tier or EXPIRED per CONTENT_PIPELINE.md."""
    if grant.expires_at is None:
        return None
    now = _ensure_utc(at_time or datetime.now(UTC))
    exp = _ensure_utc(grant.expires_at)
    if now >= exp:
        return "EXPIRED"
    remaining_days = (exp - now).total_seconds() / 86400.0
    if remaining_days <= 7:
        return "7_DAYS"
    if remaining_days <= 30:
        return "30_DAYS"
    if remaining_days <= 60:
        return "60_DAYS"
    return None


def _validate_chain_of_title_for_action(grant: RightsGrant, action: str) -> RightsDecision | None:
    cot = grant.chain_of_title
    if cot.is_translated and not (cot.translation_holder and cot.translation_holder.strip()):
        return RightsDecision(
            False,
            "RIGHTS_MISSING_CHAIN_OF_TITLE",
            "Translated work requires translation_holder in chain_of_title",
        )
    if action == "derivative" and not (cot.adaptation_holder and cot.adaptation_holder.strip()):
        return RightsDecision(
            False,
            "RIGHTS_MISSING_CHAIN_OF_TITLE",
            "Derivative/branching use requires adaptation_holder in chain_of_title",
        )
    if grant.source_type == "human_narration":
        if not (cot.performer_holder and cot.performer_holder.strip()) or not (
            cot.master_recording_holder and cot.master_recording_holder.strip()
        ):
            return RightsDecision(
                False,
                "RIGHTS_MISSING_CHAIN_OF_TITLE",
                "Human narration requires performer_holder and master_recording_holder",
            )
    if action in {"voice_clone", "training"} and not (
        cot.voice_consent_holder and cot.voice_consent_holder.strip()
    ):
        return RightsDecision(
            False,
            "RIGHTS_VOICE_CONSENT_REQUIRED",
            f"Action '{action}' requires explicit voice_consent_holder authorization",
        )
    return None


def _validate_maker_checker(grant: RightsGrant) -> RightsDecision | None:
    if not grant.reviewer_id or not grant.reviewer_id.strip():
        return RightsDecision(
            False,
            "RIGHTS_UNVERIFIED",
            "Missing authenticated reviewer_id on rights grant",
        )
    submitter = grant.submitter_id.strip()
    evidence_submitter = grant.evidence.submitted_by.strip()
    reviewer = grant.reviewer_id.strip()
    if reviewer == submitter or reviewer == evidence_submitter:
        return RightsDecision(
            False,
            "RIGHTS_SELF_APPROVAL_FORBIDDEN",
            f"Maker-checker violation: submitter '{submitter}' cannot approve own rights grant",
        )
    matching_approvals = [
        entry
        for entry in grant.audit_log
        if entry.decision == "APPROVE"
        and entry.reviewer_id == reviewer
        and entry.evidence_version == grant.evidence.contract_version
    ]
    if not matching_approvals:
        return RightsDecision(
            False,
            "RIGHTS_EVIDENCE_MISMATCH",
            "No matching APPROVE audit log entry for current contract evidence version",
        )
    return None


def evaluate_rights(
    grant: RightsGrant,
    action: str,
    *,
    asset: AssetLicense | None = None,
    territory: str | None = None,
    language: str | None = None,
    edition_id: str | None = None,
    at_time: datetime | None = None,
    require_production: bool = False,
) -> RightsDecision:
    """Deterministically evaluate whether `action` is permitted under `grant` and `asset`."""
    if action not in VALID_ACTIONS:
        raise ValueError(f"Unknown right: {action}")

    now = _ensure_utc(at_time or datetime.now(UTC))

    # 1. Takedown / Revocation / Dispute checks (highest priority freeze)
    if grant.takedown_active or grant.state in {"TAKEDOWN", "REVOKED"}:
        return RightsDecision(
            False,
            "RIGHTS_TAKEDOWN_ACTIVE",
            f"Grant '{grant.grant_id}' is under takedown or revoked",
        )
    if asset is not None and asset.status == "takedown":
        return RightsDecision(
            False,
            "RIGHTS_TAKEDOWN_ACTIVE",
            f"Asset '{asset.asset_id}' is under takedown",
        )
    if grant.dispute_active or grant.state == "DISPUTED":
        return RightsDecision(
            False,
            "RIGHTS_DISPUTE_HOLD",
            f"Grant '{grant.grant_id}' is paused due to an active rights dispute",
        )
    if asset is not None and asset.status == "disputed":
        return RightsDecision(
            False,
            "RIGHTS_DISPUTE_HOLD",
            f"Asset '{asset.asset_id}' is paused due to an active rights dispute",
        )

    # 2. Maker-checker / self-approval guard (always enforced when reviewer is set or non-demo)
    if (
        require_production
        or grant.production_approval
        or grant.source_type != "original_project"
        or grant.reviewer_id is not None
    ):
        mc_failure = _validate_maker_checker(grant)
        if mc_failure is not None:
            return mc_failure

    # 3. Lifecycle state & demo vs. production gate
    if require_production:
        if not grant.production_approval:
            return RightsDecision(
                False,
                "RIGHTS_UNVERIFIED",
                "Grant does not have production_approval=True",
            )
        if grant.state not in ACTIVE_STATES:
            return RightsDecision(
                False,
                "RIGHTS_STATE_NOT_ELIGIBLE",
                f"Grant state '{grant.state}' is not eligible for production delivery",
            )
    else:
        if not (grant.verified_for_demo or grant.production_approval):
            return RightsDecision(
                False,
                "RIGHTS_UNVERIFIED",
                "Rights have not been reviewed",
            )
        if grant.state not in ACTIVE_STATES:
            return RightsDecision(
                False,
                "RIGHTS_STATE_NOT_ELIGIBLE",
                f"Grant state '{grant.state}' is not active",
            )

    # 4. Effective time window
    if now < _ensure_utc(grant.valid_from):
        return RightsDecision(
            False,
            "RIGHTS_NOT_YET_VALID",
            f"Grant '{grant.grant_id}' is not valid until {grant.valid_from.isoformat()}",
        )
    if grant.expires_at is not None and now >= _ensure_utc(grant.expires_at):
        return RightsDecision(
            False,
            "RIGHTS_EXPIRED",
            f"Grant '{grant.grant_id}' expired at {grant.expires_at.isoformat()}",
            renewal_alert="EXPIRED",
        )

    # 5. Territory, language, and edition scoping
    if territory is not None:
        allowed_territories = {t.upper() for t in grant.territories}
        if territory.upper() not in allowed_territories and "WORLD" not in allowed_territories:
            return RightsDecision(
                False,
                "RIGHTS_TERRITORY_DENIED",
                f"Territory '{territory}' is outside licensed territories {grant.territories}",
            )
    if language is not None and language not in grant.languages:
        return RightsDecision(
            False,
            "RIGHTS_LANGUAGE_DENIED",
            f"Language '{language}' is outside licensed languages {grant.languages}",
        )
    if edition_id is not None and edition_id != grant.edition_id:
        return RightsDecision(
            False,
            "RIGHTS_EDITION_MISMATCH",
            f"Edition '{edition_id}' does not match licensed edition '{grant.edition_id}'",
        )

    # 6. Action permission & explicit denial
    if action in grant.denied_actions or action not in grant.granted_actions:
        return RightsDecision(
            False,
            "RIGHTS_ACTION_DENIED",
            f"Not licensed: {action}",
        )

    # 7. Chain-of-title completeness for the requested action
    cot_failure = _validate_chain_of_title_for_action(grant, action)
    if cot_failure is not None:
        return cot_failure

    # 8. Asset quarantine & grant binding check
    if asset is not None:
        if asset.rights_grant_id != grant.grant_id or asset.rights_grant_version != grant.version:
            return RightsDecision(
                False,
                "RIGHTS_EVIDENCE_MISMATCH",
                f"Asset '{asset.asset_id}' is not bound to grant {grant.grant_id}@v{grant.version}",
            )
        if asset.work_id != grant.work_id or asset.edition_id != grant.edition_id:
            return RightsDecision(
                False,
                "RIGHTS_EDITION_MISMATCH",
                f"Asset '{asset.asset_id}' work/edition mismatch with grant",
            )
        if asset.status not in {"approved", "published"}:
            return RightsDecision(
                False,
                "RIGHTS_ASSET_QUARANTINED",
                f"Asset '{asset.asset_id}' is in status '{asset.status}' and cannot be delivered",
            )
        if asset.source_type == "human_narration" and (
            not asset.voice_owner_id or not asset.master_owner_id
        ):
            return RightsDecision(
                False,
                "RIGHTS_MISSING_CHAIN_OF_TITLE",
                f"Human narration asset '{asset.asset_id}' lacks voice/master owner IDs",
            )

    return RightsDecision(
        True,
        "OK",
        f"Action '{action}' permitted by grant {grant.grant_id}@v{grant.version}",
        renewal_alert=renewal_warning_level(grant, now),
    )


def assert_rights(
    grant: RightsGrant,
    action: str,
    *,
    asset: AssetLicense | None = None,
    territory: str | None = None,
    language: str | None = None,
    edition_id: str | None = None,
    at_time: datetime | None = None,
    require_production: bool = False,
) -> RightsDecision:
    decision = evaluate_rights(
        grant,
        action,
        asset=asset,
        territory=territory,
        language=language,
        edition_id=edition_id,
        at_time=at_time,
        require_production=require_production,
    )
    if not decision.allowed:
        raise RightsViolationError(decision.code, decision.reason)
    return decision


# --- Maker-Checker Workflow Transitions ---


def submit_evidence(
    grant: RightsGrant,
    actor_id: str,
    evidence: ContractEvidence,
) -> RightsGrant:
    if actor_id != grant.submitter_id or evidence.submitted_by != actor_id:
        raise RightsViolationError(
            "RIGHTS_EVIDENCE_MISMATCH",
            "Only the designated submitter may attach contract evidence",
        )
    if grant.state not in {"DRAFT", "EVIDENCE_SUBMITTED"}:
        raise RightsViolationError(
            "RIGHTS_STATE_NOT_ELIGIBLE",
            f"Cannot submit evidence from state '{grant.state}'",
        )
    return grant.model_copy(
        update={
            "evidence": evidence,
            "state": "EVIDENCE_SUBMITTED",
        }
    )


def begin_review(
    grant: RightsGrant,
    reviewer_id: str,
    reviewer_role: ReviewerRole,
) -> RightsGrant:
    if reviewer_id == grant.submitter_id or reviewer_id == grant.evidence.submitted_by:
        raise RightsViolationError(
            "RIGHTS_SELF_APPROVAL_FORBIDDEN",
            "Reviewer must be distinct from the submitting creator",
        )
    if grant.state != "EVIDENCE_SUBMITTED":
        raise RightsViolationError(
            "RIGHTS_STATE_NOT_ELIGIBLE",
            f"Grant must be in EVIDENCE_SUBMITTED to begin review (current: {grant.state})",
        )
    return grant.model_copy(
        update={
            "reviewer_id": reviewer_id,
            "state": "UNDER_REVIEW",
        }
    )


def approve_grant(
    grant: RightsGrant,
    *,
    audit_id: str,
    reviewer_id: str,
    reviewer_role: ReviewerRole,
    note: str,
    decided_at: datetime | None = None,
    production_approval: bool = False,
    publish_immediately: bool = False,
) -> RightsGrant:
    if grant.state != "UNDER_REVIEW":
        raise RightsViolationError(
            "RIGHTS_STATE_NOT_ELIGIBLE",
            f"Grant must be in UNDER_REVIEW to approve (current: {grant.state})",
        )
    if reviewer_id == grant.submitter_id or reviewer_id == grant.evidence.submitted_by:
        raise RightsViolationError(
            "RIGHTS_SELF_APPROVAL_FORBIDDEN",
            "Creator/submitter cannot self-approve rights grant",
        )
    for act in grant.granted_actions:
        cot_err = _validate_chain_of_title_for_action(grant, act)
        if cot_err is not None:
            raise RightsViolationError(cot_err.code, cot_err.reason)

    ts = _ensure_utc(decided_at or datetime.now(UTC))
    entry = ReviewAuditEntry(
        audit_id=audit_id,
        reviewer_id=reviewer_id,
        reviewer_role=reviewer_role,
        decision="APPROVE",
        decided_at=ts,
        evidence_version=grant.evidence.contract_version,
        note=note,
    )
    next_state: ReviewState = "PUBLISHED" if publish_immediately else "APPROVED"
    return grant.model_copy(
        update={
            "reviewer_id": reviewer_id,
            "state": next_state,
            "production_approval": production_approval,
            "audit_log": [*grant.audit_log, entry],
        }
    )


def trigger_takedown(
    grant: RightsGrant,
    *,
    audit_id: str,
    reviewer_id: str,
    reviewer_role: ReviewerRole,
    reason: str,
    decided_at: datetime | None = None,
) -> RightsGrant:
    ts = _ensure_utc(decided_at or datetime.now(UTC))
    entry = ReviewAuditEntry(
        audit_id=audit_id,
        reviewer_id=reviewer_id,
        reviewer_role=reviewer_role,
        decision="TAKEDOWN",
        decided_at=ts,
        evidence_version=grant.evidence.contract_version,
        note=reason,
    )
    return grant.model_copy(
        update={
            "takedown_active": True,
            "state": "TAKEDOWN",
            "audit_log": [*grant.audit_log, entry],
        }
    )


def trigger_dispute_hold(
    grant: RightsGrant,
    *,
    audit_id: str,
    reviewer_id: str,
    reviewer_role: ReviewerRole,
    reason: str,
    decided_at: datetime | None = None,
) -> RightsGrant:
    ts = _ensure_utc(decided_at or datetime.now(UTC))
    entry = ReviewAuditEntry(
        audit_id=audit_id,
        reviewer_id=reviewer_id,
        reviewer_role=reviewer_role,
        decision="DISPUTE_HOLD",
        decided_at=ts,
        evidence_version=grant.evidence.contract_version,
        note=reason,
    )
    return grant.model_copy(
        update={
            "dispute_active": True,
            "state": "DISPUTED",
            "audit_log": [*grant.audit_log, entry],
        }
    )


def verify_asset_digest(asset: AssetLicense, file_path: Path) -> None:
    if not file_path.is_file():
        raise RightsViolationError(
            "RIGHTS_ASSET_QUARANTINED",
            f"Missing media file for asset '{asset.asset_id}': {file_path}",
        )
    actual = hashlib.sha256(file_path.read_bytes()).hexdigest()
    if actual.lower() != asset.sha256.lower():
        raise RightsViolationError(
            "RIGHTS_EVIDENCE_MISMATCH",
            f"SHA-256 mismatch for asset '{asset.asset_id}'",
        )


def parse_manifest(raw: dict[str, Any]) -> RightsManifest:
    try:
        return RightsManifest.model_validate(raw)
    except Exception as exc:
        raise RightsSchemaError(f"Invalid rights manifest: {exc}") from exc
