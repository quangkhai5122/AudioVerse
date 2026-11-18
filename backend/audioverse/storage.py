"""Transactional persistence, edition pinning, tamper-evident event chain, and replay recovery.

Implements T003 storage invariants (`INT-08`, `INT-18`, `SEC-02`, `SEC-12`, `SEC-14`):
- Applies versioned migrations (`audioverse.migrations.apply_migrations`).
- Pins each story run to an immutable `edition_id` stored in `editions` (`INT-08`).
- Chains `events` with SHA-256 `event_hash` and DB-level `BEFORE UPDATE/DELETE` immutability triggers.
- Saves `story_snapshots` and supports deterministic replay recovery (`restore_run_from_events`, `INT-18`).
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any
from uuid import uuid4

from audioverse.engine import transition, visible_scene
from audioverse.migrations import apply_migrations


class RunNotFound(Exception):
    pass


class VersionConflict(Exception):
    pass


class ReplayConflict(Exception):
    pass


class TamperDetectedError(RuntimeError):
    """Event chain or state checksum verification failed during replay recovery."""


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, timeout=8, isolation_level=None)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA busy_timeout=8000")
    con.execute("PRAGMA foreign_keys=ON")
    return con


def compute_state_checksum(
    edition_id: str,
    scene_id: str,
    version: int,
    flags: dict[str, bool],
) -> str:
    canonical_flags = json.dumps(flags, ensure_ascii=False, sort_keys=True)
    payload = f"{edition_id}|{scene_id}|{version}|{canonical_flags}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def compute_event_hash(
    prev_hash: str,
    run_id: str,
    from_scene: str,
    to_scene: str,
    choice_id: str,
    version: int,
    flags: dict[str, bool],
) -> str:
    canonical_flags = json.dumps(flags, ensure_ascii=False, sort_keys=True)
    payload = f"{prev_hash}|{run_id}|{from_scene}|{to_scene}|{choice_id}|{version}|{canonical_flags}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _default_edition_id(story: dict[str, Any]) -> str:
    return str(story.get("edition_id") or f"{story['id']}-ed1")


def register_edition(
    path: Path,
    story: dict[str, Any],
    edition_id: str | None = None,
    version: int = 1,
) -> str:
    ed_id = edition_id or _default_edition_id(story)
    serialized = json.dumps(story, ensure_ascii=False, sort_keys=True)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    with _connect(path) as con:
        con.execute(
            """
            INSERT INTO editions(id, work_id, version, content_sha256, story_json)
            VALUES(?, ?, ?, ?, ?)
            ON CONFLICT(id) DO NOTHING
            """,
            (ed_id, story["id"], version, digest, serialized),
        )
    return ed_id


def _resolve_edition_story(
    con: sqlite3.Connection,
    edition_id: str,
    fallback_story: dict[str, Any],
) -> dict[str, Any]:
    row = con.execute(
        "SELECT story_json FROM editions WHERE id=?", (edition_id,)
    ).fetchone()
    if row is not None:
        return json.loads(row["story_json"])
    return fallback_story


def init_db(path: Path, initial_story: dict[str, Any] | None = None) -> list[int]:
    with _connect(path) as con:
        applied = apply_migrations(con)
    if initial_story is not None:
        register_edition(path, initial_story)
    return applied


def _run_output(row: sqlite3.Row, story: dict[str, Any]) -> dict[str, Any]:
    flags = json.loads(row["flags_json"])
    keys = row.keys()
    edition_id = row["edition_id"] if "edition_id" in keys else _default_edition_id(story)
    pos_ms = int(row["position_ms"]) if "position_ms" in keys else 0
    speed = float(row["playback_speed"]) if "playback_speed" in keys else 1.0
    return {
        "run_id": row["id"],
        "story_id": row["story_id"],
        "edition_id": edition_id,
        "version": row["version"],
        "position_ms": pos_ms,
        "playback_speed": speed,
        "flags": flags,
        "scene": visible_scene(story, row["scene_id"], flags),
    }


def create_run(
    path: Path,
    story: dict[str, Any],
    actor: str,
    edition_id: str | None = None,
) -> dict[str, Any]:
    rid = str(uuid4())
    ed_id = register_edition(path, story, edition_id=edition_id)
    start_scene = story["start_scene"]
    state_csum = compute_state_checksum(ed_id, start_scene, 0, {})
    genesis_hash = "0" * 64
    with _connect(path) as con:
        con.execute("BEGIN IMMEDIATE")
        try:
            pinned_story = _resolve_edition_story(con, ed_id, story)
            start_scene = pinned_story["start_scene"]
            state_csum = compute_state_checksum(ed_id, start_scene, 0, {})
            con.execute(
                """
                INSERT INTO runs(
                    id, story_id, edition_id, demo_actor, scene_id, flags_json, version, state_checksum
                ) VALUES(?, ?, ?, ?, ?, ?, 0, ?)
                """,
                (rid, pinned_story["id"], ed_id, actor, start_scene, "{}", state_csum),
            )
            con.execute(
                """
                INSERT INTO story_snapshots(
                    run_id, edition_id, version, scene_id, flags_json, state_checksum, last_event_hash
                ) VALUES(?, ?, 0, ?, ?, ?, ?)
                """,
                (rid, ed_id, start_scene, "{}", state_csum, genesis_hash),
            )
            row = con.execute("SELECT * FROM runs WHERE id=?", (rid,)).fetchone()
            con.execute("COMMIT")
        except Exception:
            con.execute("ROLLBACK")
            raise
    return _run_output(row, pinned_story)


def get_run(path: Path, story: dict[str, Any], actor: str, rid: str) -> dict[str, Any]:
    with _connect(path) as con:
        row = con.execute(
            "SELECT * FROM runs WHERE id=? AND demo_actor=?", (rid, actor)
        ).fetchone()
        if row is None or row["story_id"] != story["id"]:
            raise RunNotFound()
        pinned_story = _resolve_edition_story(con, row["edition_id"], story)
    return _run_output(row, pinned_story)


def choose(
    path: Path,
    story: dict[str, Any],
    actor: str,
    rid: str,
    choice_id: str,
    expected_version: int,
    idem_key: str,
) -> dict[str, Any]:
    con = _connect(path)
    try:
        con.execute("BEGIN IMMEDIATE")
        row = con.execute(
            "SELECT * FROM runs WHERE id=? AND demo_actor=?", (rid, actor)
        ).fetchone()
        if row is None or row["story_id"] != story["id"]:
            raise RunNotFound()
        replay = con.execute(
            "SELECT response_json, choice_id FROM events WHERE run_id=? AND idem_key=?",
            (rid, idem_key),
        ).fetchone()
        if replay is not None:
            if replay["choice_id"] != choice_id:
                raise ReplayConflict("Idempotency key reused for a different action")
            con.execute("COMMIT")
            return json.loads(replay["response_json"])
        if row["version"] != expected_version:
            raise VersionConflict("Run was changed; reload the latest state")

        ed_id = row["edition_id"]
        pinned_story = _resolve_edition_story(con, ed_id, story)
        flags = json.loads(row["flags_json"])
        t = transition(pinned_story, row["scene_id"], choice_id, flags)
        next_version = row["version"] + 1
        flags_serialized = json.dumps(t.flags, ensure_ascii=False, sort_keys=True)
        state_csum = compute_state_checksum(ed_id, t.target, next_version, t.flags)

        last_ev = con.execute(
            "SELECT event_hash FROM events WHERE run_id=? ORDER BY id DESC LIMIT 1",
            (rid,),
        ).fetchone()
        prev_hash = last_ev["event_hash"] if last_ev and last_ev["event_hash"] else "0" * 64
        ev_hash = compute_event_hash(
            prev_hash,
            rid,
            row["scene_id"],
            t.target,
            choice_id,
            next_version,
            t.flags,
        )

        con.execute(
            """
            UPDATE runs
            SET scene_id=?, flags_json=?, version=?, position_ms=0, state_checksum=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=?
            """,
            (t.target, flags_serialized, next_version, state_csum, rid),
        )
        updated = con.execute("SELECT * FROM runs WHERE id=?", (rid,)).fetchone()
        response = _run_output(updated, pinned_story)
        con.execute(
            """
            INSERT INTO events(
                run_id, idem_key, from_scene, to_scene, choice_id, response_json, event_hash
            ) VALUES(?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rid,
                idem_key,
                row["scene_id"],
                t.target,
                choice_id,
                json.dumps(response, ensure_ascii=False),
                ev_hash,
            ),
        )
        con.execute(
            """
            INSERT INTO story_snapshots(
                run_id, edition_id, version, scene_id, flags_json, state_checksum, last_event_hash
            ) VALUES(?, ?, ?, ?, ?, ?, ?)
            """,
            (rid, ed_id, next_version, t.target, flags_serialized, state_csum, ev_hash),
        )
        con.execute("COMMIT")
        return response
    except Exception:
        if con.in_transaction:
            con.execute("ROLLBACK")
        raise
    finally:
        con.close()


def event_history(path: Path, actor: str, rid: str) -> list[dict[str, Any]]:
    with _connect(path) as con:
        row = con.execute(
            "SELECT id FROM runs WHERE id=? AND demo_actor=?", (rid, actor)
        ).fetchone()
        if row is None:
            raise RunNotFound()
        events = con.execute(
            "SELECT choice_id, from_scene, to_scene, event_hash, created_at "
            "FROM events WHERE run_id=? ORDER BY id",
            (rid,),
        ).fetchall()
    return [dict(e) for e in events]


def restore_run_from_events(
    path: Path,
    story: dict[str, Any],
    actor: str,
    rid: str,
) -> dict[str, Any]:
    """Deterministically replay event ledger against pinned edition and verify integrity (`INT-18`)."""
    with _connect(path) as con:
        run_row = con.execute(
            "SELECT * FROM runs WHERE id=? AND demo_actor=?", (rid, actor)
        ).fetchone()
        if run_row is None:
            raise RunNotFound()
        ed_id = run_row["edition_id"]
        pinned_story = _resolve_edition_story(con, ed_id, story)
        events = con.execute(
            "SELECT * FROM events WHERE run_id=? ORDER BY id ASC", (rid,)
        ).fetchall()

        scene_id = pinned_story["start_scene"]
        flags: dict[str, bool] = {}
        version = 0
        prev_hash = "0" * 64

        for ev in events:
            if ev["from_scene"] != scene_id:
                raise TamperDetectedError(
                    f"Event from_scene '{ev['from_scene']}' != expected '{scene_id}'"
                )
            t = transition(pinned_story, scene_id, ev["choice_id"], flags)
            if t.target != ev["to_scene"]:
                raise TamperDetectedError(
                    f"Event to_scene '{ev['to_scene']}' != deterministic target '{t.target}'"
                )
            version += 1
            flags = t.flags
            expected_ev_hash = compute_event_hash(
                prev_hash,
                rid,
                scene_id,
                t.target,
                ev["choice_id"],
                version,
                flags,
            )
            if ev["event_hash"] and ev["event_hash"] != expected_ev_hash:
                raise TamperDetectedError("Event hash chain mismatch detected")
            prev_hash = expected_ev_hash
            scene_id = t.target

        expected_state_csum = compute_state_checksum(ed_id, scene_id, version, flags)
        if run_row["state_checksum"] and run_row["state_checksum"] != expected_state_csum:
            raise TamperDetectedError("Run state_checksum does not match replayed event ledger")

        flags_serialized = json.dumps(flags, ensure_ascii=False, sort_keys=True)
        con.execute(
            """
            UPDATE runs
            SET scene_id=?, flags_json=?, version=?, state_checksum=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
            """,
            (scene_id, flags_serialized, version, expected_state_csum, rid),
        )
        restored_row = con.execute("SELECT * FROM runs WHERE id=?", (rid,)).fetchone()
    return _run_output(restored_row, pinned_story)


def update_playback_progress(
    path: Path,
    story: dict[str, Any],
    actor: str,
    rid: str,
    *,
    scene_id: str,
    position_ms: int,
    playback_speed: float = 1.0,
) -> dict[str, Any]:
    """Persist playback position (`position_ms`) and `playback_speed` for `rid` (`PLY-05`, `PLY-08`)."""
    if position_ms < 0:
        raise ValueError("position_ms must be non-negative")
    if playback_speed < 0.8 or playback_speed > 2.0:
        raise ValueError("playback_speed must be between 0.8 and 2.0")
    with _connect(path) as con:
        con.execute("BEGIN IMMEDIATE")
        try:
            row = con.execute(
                "SELECT * FROM runs WHERE id=? AND demo_actor=?", (rid, actor)
            ).fetchone()
            if row is None or row["story_id"] != story["id"]:
                raise RunNotFound()
            if row["scene_id"] != scene_id:
                raise VersionConflict(
                    f"Run is on scene '{row['scene_id']}', cannot save progress for '{scene_id}'"
                )
            con.execute(
                """
                UPDATE runs
                SET position_ms=?, playback_speed=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
                """,
                (position_ms, round(playback_speed, 2), rid),
            )
            updated = con.execute("SELECT * FROM runs WHERE id=?", (rid,)).fetchone()
            pinned_story = _resolve_edition_story(con, updated["edition_id"], story)
            con.execute("COMMIT")
        except Exception:
            if con.in_transaction:
                con.execute("ROLLBACK")
            raise
    return _run_output(updated, pinned_story)


def list_continue_listening(
    path: Path,
    story: dict[str, Any],
    actor: str,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Return recent runs with saved scene & playback position (`LIB-02`, `INT-12`)."""
    with _connect(path) as con:
        rows = con.execute(
            """
            SELECT * FROM runs
            WHERE demo_actor=?
            ORDER BY updated_at DESC, rowid DESC
            LIMIT ?
            """,
            (actor, limit),
        ).fetchall()
        items: list[dict[str, Any]] = []
        for r in rows:
            pinned_story = _resolve_edition_story(con, r["edition_id"], story)
            out = _run_output(r, pinned_story)
            out["updated_at"] = r["updated_at"]
            items.append(out)
    return items


def set_library_follow(
    path: Path,
    actor: str,
    work_id: str,
    followed: bool,
) -> dict[str, Any]:
    """Deterministically set follow state for `(actor, work_id)` (`LIB-01`)."""
    with _connect(path) as con:
        con.execute(
            """
            INSERT INTO user_library(user_id, work_id, followed, updated_at)
            VALUES(?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, work_id) DO UPDATE SET
                followed=excluded.followed,
                updated_at=CURRENT_TIMESTAMP
            """,
            (actor, work_id, int(followed)),
        )
        row = con.execute(
            "SELECT * FROM user_library WHERE user_id=? AND work_id=?",
            (actor, work_id),
        ).fetchone()
    return {
        "user_id": row["user_id"],
        "work_id": row["work_id"],
        "followed": bool(row["followed"]),
        "updated_at": row["updated_at"],
    }


def get_library_items(path: Path, actor: str) -> list[dict[str, Any]]:
    with _connect(path) as con:
        rows = con.execute(
            "SELECT * FROM user_library WHERE user_id=? AND followed=1 ORDER BY updated_at DESC",
            (actor,),
        ).fetchall()
    return [
        {
            "user_id": r["user_id"],
            "work_id": r["work_id"],
            "followed": bool(r["followed"]),
            "updated_at": r["updated_at"],
        }
        for r in rows
    ]

