"""Author-controlled content and rights checks.

Delegates canonical provenance validation and action gating to `audioverse.rights`
while preserving backward compatibility for legacy dict-based test fixtures.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from audioverse.rights import (
     VALID_ACTIONS,
    AssetLicense,
    RightsDecision,
    RightsGrant,
    RightsManifest,
    RightsSchemaError,
    RightsViolationError,
    assert_rights,
    parse_manifest,
    verify_asset_digest,
)


class ContentError(ValueError):
    """Story schema or manifest is inconsistent."""


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ContentError("Root JSON object required")
    return data


def validate_story(story: dict[str, Any]) -> None:
    if not story.get("id") or not story.get("start_scene"):
        raise ContentError("story id and start_scene required")
    scenes = story.get("scenes")
    if not isinstance(scenes, dict) or story["start_scene"] not in scenes:
        raise ContentError("Missing start scene")
    choices_seen: set[str] = set()
    for sid, scene in scenes.items():
        if not isinstance(scene.get("text"), str) or not scene["text"].strip():
            raise ContentError(f"Missing text for {sid}")
        for c in scene.get("choices", []):
            cid = c.get("id")
            if not cid or cid in choices_seen:
                raise ContentError(f"Duplicate or missing choice id: {cid}")
            choices_seen.add(cid)
            if c.get("target") not in scenes:
                raise ContentError(f"Dangling choice {cid}")
            if not isinstance(c.get("label"), str) or not c["label"].strip():
                raise ContentError(f"Missing choice label {cid}")
            for key in c.get("requires", []):
                if not isinstance(key, str) or not key:
                    raise ContentError(f"Bad precondition {cid}")
            for key in c.get("set_flags", []):
                if not isinstance(key, str) or not key:
                    raise ContentError(f"Bad effect {cid}")
    if len(scenes) < 2:
        raise ContentError("Demo requires multiple scenes")


def validate_rights_manifest(
    license_info: dict[str, Any],
    story: dict[str, Any] | None = None,
    media_dir: Path | None = None,
) -> RightsManifest:
    try:
        manifest = parse_manifest(license_info)
    except RightsSchemaError as exc:
        raise ContentError(str(exc)) from exc

    if story is not None:
        if story.get("id") != manifest.content_id:
            raise ContentError("Story id does not match manifest content_id")
        if story.get("license_id") != manifest.id:
            raise ContentError("Story license_id does not match manifest id")
        story_bytes = json.dumps(story, ensure_ascii=False).encode("utf-8")
        _ = story_bytes
        for sid in story.get("scenes", {}):
            if sid not in manifest.assets:
                raise ContentError(f"Missing asset license entry for scene '{sid}'")
            if media_dir is not None:
                mp3 = media_dir / f"{sid}.mp3"
                verify_asset_digest(manifest.assets[sid], mp3)
    return manifest


def assert_permission(
    license_info: dict[str, Any] | RightsManifest | RightsGrant,
    action: str,
    *,
    scene_id: str | None = None,
    asset: AssetLicense | None = None,
    territory: str | None = None,
    language: str | None = None,
    edition_id: str | None = None,
    at_time: datetime | None = None,
    require_production: bool = False,
) -> RightsDecision:
    if action not in VALID_ACTIONS:
        raise ContentError("Unknown right")

    if isinstance(license_info, RightsGrant):
        return assert_rights(
            license_info,
            action,
            asset=asset,
            territory=territory,
            language=language,
            edition_id=edition_id,
            at_time=at_time,
            require_production=require_production,
        )

    if isinstance(license_info, RightsManifest):
        resolved_asset = asset or (
            license_info.assets.get(scene_id) if scene_id is not None else None
        )
        return assert_rights(
            license_info.grant,
            action,
            asset=resolved_asset,
            territory=territory,
            language=language,
            edition_id=edition_id,
            at_time=at_time,
            require_production=require_production,
        )

    # Dict input: inspect top-level overrides (e.g. `{**rights, "verified_for_demo": False}`)
    if not license_info.get("verified_for_demo", False) and not license_info.get(
        "production_approval", False
    ):
        raise RightsViolationError("RIGHTS_UNVERIFIED", "Rights have not been reviewed")
    if action in license_info.get("denied", []) or action not in license_info.get(
        "permissions", []
    ):
        raise RightsViolationError("RIGHTS_ACTION_DENIED", f"Not licensed: {action}")

    if "grant" in license_info and isinstance(license_info["grant"], dict):
        grant_dict = dict(license_info["grant"])
        grant_dict["verified_for_demo"] = bool(license_info.get("verified_for_demo", False))
        grant_dict["production_approval"] = bool(license_info.get("production_approval", False))
        grant_dict["granted_actions"] = list(license_info.get("permissions", []))
        grant_dict["denied_actions"] = list(license_info.get("denied", []))
        grant = RightsGrant.model_validate(grant_dict)
        resolved_asset = asset
        if resolved_asset is None and scene_id is not None:
            raw_assets = license_info.get("assets", {})
            if scene_id in raw_assets:
                resolved_asset = AssetLicense.model_validate(raw_assets[scene_id])
        return assert_rights(
            grant,
            action,
            asset=resolved_asset,
            territory=territory,
            language=language,
            edition_id=edition_id,
            at_time=at_time,
            require_production=require_production,
        )

    if require_production and not license_info.get("production_approval", False):
        raise RightsViolationError(
            "RIGHTS_UNVERIFIED",
            "Grant does not have production_approval=True",
        )
    return RightsDecision(True, "OK", f"Action '{action}' permitted by legacy demo manifest")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
