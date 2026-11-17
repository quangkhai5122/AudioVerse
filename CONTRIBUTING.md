# Contributing to AudioVerse

1. Read AGENTS.md and PROJECT_STATE.md; identify and claim a READY task.
2. Use a descriptive working branch (`codex/T00x-scope`); verify remote history/access and preserve others' changes. Never force-push, rewrite shared history or merge into a protected branch.
3. Run `python scripts/check_repo.py` and `python -m pytest` baseline.
4. Make minimal scoped changes with tests; update API/data/ADR and requirement status accurately.
5. Prevent copyrighted media, voice samples, private data and credentials from entering commits.
6. Run relevant checks and annotate any native/toolchain limitations.
7. Update `SESSION_LOG.md`, `CURRENT_TASK.md`, `PROJECT_STATE.md` before presenting completion.
8. The owner granted standing permission on 2026-11-17 for ordinary scoped AudioVerse commits/pushes after review and suitable tests; see AGENTS.md for limits. Production/content publication, purchases and other external actions remain separately gated. Check actual Git configuration; the unpacked starter's lack of history is not evidence that the working repository has no remote.
