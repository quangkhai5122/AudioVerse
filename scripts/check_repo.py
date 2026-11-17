"""Non-network repository integrity checks; safe for Coding Agents and CI."""
import csv
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from audioverse.content import assert_permission, validate_story  # noqa: E402


def main():
    story=json.loads((ROOT/'content/demo_story/story.json').read_text(encoding='utf-8'))
    rights=json.loads((ROOT/'content/licenses/demo_license.json').read_text(encoding='utf-8'))
    validate_story(story)
    assert story['license_id']==rights['id']
    assert_permission(rights,'stream')
    assert_permission(rights,'tts')
    assert_permission(rights,'derivative')
    for denied in ('voice_clone','training'):
        try:
            assert_permission(rights,denied)
        except PermissionError:
            pass
        else:
            raise AssertionError(f'Unsafe demo permission: {denied}')
    for scene_id in story['scenes']:
        f=ROOT/'media/demo'/f'{scene_id}.mp3'
        assert f.exists() and f.stat().st_size>100, f'Missing synthetic demo audio {f}'
    psv=ROOT/'docs/product/requirements.psv'
    with psv.open(encoding='utf-8') as handle:
        rows=list(csv.DictReader(handle,delimiter='|'))
    ids=[r['ID'] for r in rows]
    assert len(ids)==len(set(ids)) and len(ids)>=120
    for r in rows:
        assert r['Priority'] in {'P0','P1','P2','P3'}
        assert r['Status'] in {'DEMO','SOURCE','PLANNED','BLOCKED','DONE-PROD'}
    table=(ROOT/'docs/product/FUNCTIONAL_SPEC.md').read_text(encoding='utf-8')
    for rid in ids:
        assert f'`{rid}`' in table, f'Spec missing {rid}'
    for p in ['AGENTS.md','docs/agent/PROJECT_STATE.md','docs/agent/CURRENT_TASK.md',
              'docs/agent/BACKLOG.md','docs/agent/SESSION_LOG.md',
              'docs/operations/LEGAL_RIGHTS_RELEASE_GATES.md',
              'docs/engineering/NARRATIVE_ENGINE.md','mobile/lib/main.dart']:
        assert (ROOT/p).is_file(), f'Missing {p}'
    print(f'Integrity PASS: {len(story["scenes"])} scenes, {len(rows)} requirements, assets and agent docs')


if __name__=='__main__':
    main()
