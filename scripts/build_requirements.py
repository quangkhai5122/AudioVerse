"""Rebuild functional spec markdown from source table; run after editing requirements.psv."""
import csv
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'docs/product/requirements.psv'
dest=ROOT/'docs/product/FUNCTIONAL_SPEC.md'
with source.open(encoding='utf-8') as handle:
    rows=list(csv.DictReader(handle,delimiter='|'))
ids=[r['ID'] for r in rows]
if len(ids)!=len(set(ids)):
    raise SystemExit('Duplicate functional requirement ID')
valid={'P0','P1','P2','P3'}
statuses={'DEMO','SOURCE','PLANNED','BLOCKED','DONE-PROD'}
for r in rows:
    if not r['ID'] or not r['Requirement'] or not r['Acceptance criterion'] or r['Priority'] not in valid or r['Status'] not in statuses:
        raise SystemExit(f'Bad requirement row: {r}')
lines=["# AudioVerse — Complete functional requirements register",
       "",f"**Version:** 2026-11-17 · **Total:** {len(rows)} requirements · **Single source of truth:** `requirements.psv`",
       "","## Status legend", "`DEMO`: executed locally with non-production security; `SOURCE`: code present but build validation pending; `PLANNED`: not implemented; `BLOCKED`: compliance/expert gate; `DONE-PROD`: would require release evidence. No feature is DONE-PROD at present.",
       "", "Priority P0 means critical to core architecture, not release-ready. P1 commercial MVP after gates, P2 expansion, P3 research. Each acceptance criterion is a minimum; associated task packet must add failure, edge, security and usability tests.",
       "", "## Coverage summary", "", "| Area | Number |", "|---|---:|"]
for area,count in Counter(r['Area'] for r in rows).items():
    lines.append(f'| {area} | {count} |')
for area in dict.fromkeys(r['Area'] for r in rows):
    lines += ['',f'## {area}','', '| ID | Priority | Status | Behavior | Acceptance criterion |','|---|---|---|---|---|']
    for r in rows:
        if r['Area']==area:
            lines.append(f"| `{r['ID']}` | {r['Priority']} | {r['Status']} | {r['Requirement']} | {r['Acceptance criterion']} |")
lines += ['', '## Definition of done for any item', '',
 '1. Product owner accepts behavior and content rights; risk classification recorded.',
 '2. API/client behavior and schema written in versioned documents or OpenAPI.',
 '3. Unit and integration tests cover positive, failure, concurrency and access cases.',
 '4. Agent updates task packet, ADR if needed, PROJECT_STATE, CURRENT_TASK, SESSION_LOG and this register.',
 '5. Verified execution evidence attached; unrun Flutter/browser/device tests remain pending.',
 '6. Production designation requires compliance, security and release gates in addition to feature tests.', '']
dest.write_text('\n'.join(lines),encoding='utf-8')
print(f'Wrote {dest} with {len(rows)} requirements')
