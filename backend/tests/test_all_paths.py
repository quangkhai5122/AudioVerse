from audioverse.content import read_json, validate_story
from audioverse.engine import options, transition
from audioverse.settings import ROOT


def test_all_authored_branches_reachable_and_terminal():
    story = read_json(ROOT / 'content/demo_story/story.json')
    validate_story(story)
    frontier = [(story['start_scene'], {})]
    reached = set()
    terminal = set()
    while frontier:
        scene, flags = frontier.pop()
        reached.add(scene)
        opts = options(story, scene, flags)
        if not opts:
            terminal.add(scene)
            continue
        for choice in opts:
            next_state = transition(story, scene, choice['id'], flags)
            frontier.append((next_state.target, next_state.flags))
    assert reached == set(story['scenes'])
    assert terminal == {'s8','s9','s10'}
