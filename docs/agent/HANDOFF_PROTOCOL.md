# Agent continuity / memory protocol

## Problem
Large conversations are truncated; agent sessions and user accounts change. Chat transcripts are not a reliable durable project state. Everything material must be reflected in version-controlled repository artifacts.

## Canonical documents and purposes
- `AGENTS.md`: core working rules, updated only under owner direction; standing routine commit/push permission dated 2026-11-17 is recorded there.
- `PROJECT_STATE.md`: verified shipped/partial/planned/blockers (snapshot; not aspirational).
- `CURRENT_TASK.md`: exactly ONE active task and first command.
- `BACKLOG.md`: dependency ordering, priority, release gates.
- `SESSION_LOG.md`: append-only work audit and unexecuted verification.
- `OWNER_DECISIONS.md`: owner-approved product decisions vs inferred hypotheses.
- `docs/adr/*`: why architecture was chosen, options rejected, reversibility.
- `docs/tasks/Txxx...`: testable work packets and acceptance criteria.

## Session-close checklist
1. Re-run tests after final change. Collect exact output.
2. Update state using VERIFIED evidence; downgrade tasks when regressions found.
3. Update current task and task board dependencies; avoid simultaneous unrelated work.
4. Append session log referencing files, status and exact verification. Review candidate files, commit/push ordinary scoped changes under standing permission, and record the real outcome. Preserve the restrictions in AGENTS.md.
5. Save API/schema/story world choices in docs, not prose hidden in chat.
6. Report `next first command` so the next agent can resume without guessing.
7. Report in Vietnamese with objective/task ID, completion, files, tests, risks, Git, roadmap and one next task/acceptance criteria. A missing toolchain or failed gate must remain PARTIAL/BLOCKED, never DONE by inference.

## Recovery from interruption
1. Run `git status --short && git log -3 --oneline` (if repo initialized).
2. Read `SESSION_LOG` latest and `CURRENT_TASK`.
3. Diff files since most recent verified work; assume partial changes untested.
4. Run test baseline; repair to green before implementing another task.
5. Preserve unfinished data migrations, do not reset database without backup.

## Conflict resolution
Actual executable code + tests determine current behavior; owner decisions determine desired product; ADR explains tradeoffs; session logs capture work history. If docs conflict with code, mark the discrepancy and create a task, rather than falsely claiming completion.

## Context compaction summary template
"AudioVerse stage [R], current task [T], verified tests [commands/results], current modules [paths], blocked gates [IDs], last decisions [ADR], next command [exact]." Commit this summary in `PROJECT_STATE`, not a private conversation.
