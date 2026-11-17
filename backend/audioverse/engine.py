"""Deterministic branching engine: only the engine may commit canonical facts."""
from dataclasses import dataclass
from typing import Any


class InvalidChoice(ValueError):
    pass


@dataclass(frozen=True)
class Transition:
    target: str
    flags: dict[str, bool]
    choice_id: str


def options(story: dict[str, Any], scene_id: str, flags: dict[str, bool]) -> list[dict[str, str]]:
    scene = story["scenes"][scene_id]
    return [
        {"id": c["id"], "label": c["label"]}
        for c in scene.get("choices", [])
        if all(flags.get(flag, False) for flag in c.get("requires", []))
    ]


def transition(story: dict[str, Any], scene_id: str, choice_id: str,
               flags: dict[str, bool]) -> Transition:
    candidates = story["scenes"][scene_id].get("choices", [])
    match = next((c for c in candidates if c["id"] == choice_id), None)
    if match is None:
        raise InvalidChoice("Choice does not belong to current scene")
    if any(not flags.get(flag, False) for flag in match.get("requires", [])):
        raise InvalidChoice("Preconditions not satisfied")
    new_flags = dict(flags)
    for flag in match.get("set_flags", []):
        new_flags[flag] = True
    return Transition(target=match["target"], flags=new_flags, choice_id=choice_id)


def visible_scene(story: dict[str, Any], scene_id: str,
                  flags: dict[str, bool]) -> dict[str, Any]:
    scene = story["scenes"][scene_id]
    annotations = [p["text"] for p in scene.get("conditional_notes", [])
                   if all(flags.get(x, False) for x in p.get("requires", []))]
    return {
        "id": scene_id,
        "title": scene["title"],
        "text": scene["text"],
        "memory_notes": annotations,
        "choices": options(story, scene_id, flags),
        "ending": len(scene.get("choices", [])) == 0,
    }
