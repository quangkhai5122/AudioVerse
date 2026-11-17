"""Author-controlled demo content and rights checks.

This is not a licensing verifier: approval is a manual governance step.
"""
import json
from pathlib import Path
from typing import Any


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


def assert_permission(license_info: dict[str, Any], action: str) -> None:
    if action not in {"stream", "offline", "derivative", "tts", "voice_clone", "training"}:
        raise ContentError("Unknown right")
    if not license_info.get("verified_for_demo", False):
        raise PermissionError("Rights have not been reviewed")
    if action not in license_info.get("permissions", []):
        raise PermissionError(f"Not licensed: {action}")
    # Production also checks: identity, chain of title, territory, term,
    # version, sublicense conditions, takedown and immutable approval record.
