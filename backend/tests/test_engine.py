import copy

import pytest
from audioverse.ai import DemoNarrativeProvider, DisabledRemoteProvider
from audioverse.content import ContentError, assert_permission, read_json, validate_story
from audioverse.engine import InvalidChoice, options, transition, visible_scene
from audioverse.settings import ROOT


@pytest.fixture
def story():
    return read_json(ROOT / "content/demo_story/story.json")


def test_seed_story_graph_has_unique_valid_choices(story):
    validate_story(story)
    assert len(story["scenes"]) >= 10


def test_requires_are_enforced(story):
    assert "open-cellar" not in [c["id"] for c in options(story, "s3", {})]
    with pytest.raises(InvalidChoice):
        transition(story, "s3", "open-cellar", {})
    result = transition(story, "s3", "open-cellar", {"has_key": True})
    assert result.target == "s4"
    assert result.flags["cellar_open"] is True


def test_branch_has_material_consequence(story):
    first = transition(story, "s0", "follow-tracks", {})
    second = transition(story, "s0", "climb-stairs", {})
    assert first.target != second.target
    path1 = transition(story, "s1", "take-key", first.flags)
    path2 = transition(story, "s2", "read-note", second.flags)
    assert "open-cellar" in [c["id"] for c in options(story, "s3", path1.flags)]
    assert "follow-note" in [c["id"] for c in options(story, "s3", path2.flags)]
    assert "follow-note" not in [c["id"] for c in options(story, "s3", path1.flags)]
    assert visible_scene(story, "s3", path1.flags)["memory_notes"]


def test_story_validator_rejects_dangling_target(story):
    broken = copy.deepcopy(story)
    broken["scenes"]["s0"]["choices"][0]["target"] = "nonexistent"
    with pytest.raises(ContentError):
        validate_story(broken)


def test_unlicensed_actions_blocked():
    rights = read_json(ROOT / "content/licenses/demo_license.json")
    for action in ("stream", "tts", "derivative", "offline"):
        assert_permission(rights, action)
    for action in ("voice_clone", "training"):
        with pytest.raises(PermissionError):
            assert_permission(rights, action)
    bad = {**rights, "verified_for_demo": False}
    with pytest.raises(PermissionError):
        assert_permission(bad, "stream")


def test_ai_implementation_is_disabled_by_default():
    assert DemoNarrativeProvider().draft("Đoạn gốc", ["Sự kiện được xác minh"]).provider == "deterministic-demo"
    with pytest.raises(RuntimeError):
        DisabledRemoteProvider().draft("a", [])
