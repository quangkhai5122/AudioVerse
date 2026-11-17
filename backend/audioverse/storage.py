"""Demo transactional persistence: SQLite single-writer; replace with Postgres for production."""
import json
import sqlite3
from pathlib import Path
from uuid import uuid4

from audioverse.engine import transition, visible_scene


class RunNotFound(Exception):
    pass


class VersionConflict(Exception):
    pass


class ReplayConflict(Exception):
    pass


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, timeout=8, isolation_level=None)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA busy_timeout=8000")
    con.execute("PRAGMA foreign_keys=ON")
    return con


def init_db(path: Path) -> None:
    with _connect(path) as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS runs (
            id TEXT PRIMARY KEY,
            story_id TEXT NOT NULL,
            demo_actor TEXT NOT NULL,
            scene_id TEXT NOT NULL,
            flags_json TEXT NOT NULL,
            version INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL REFERENCES runs(id),
            idem_key TEXT NOT NULL,
            from_scene TEXT NOT NULL,
            to_scene TEXT NOT NULL,
            choice_id TEXT NOT NULL,
            response_json TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(run_id, idem_key)
        );
        """)


def _run_output(row: sqlite3.Row, story: dict) -> dict:
    flags = json.loads(row["flags_json"])
    return {
        "run_id": row["id"], "story_id": row["story_id"],
        "version": row["version"], "flags": flags,
        "scene": visible_scene(story, row["scene_id"], flags),
    }


def create_run(path: Path, story: dict, actor: str) -> dict:
    rid = str(uuid4())
    with _connect(path) as con:
        con.execute("INSERT INTO runs(id, story_id, demo_actor, scene_id, flags_json) "
                    "VALUES(?, ?, ?, ?, ?)",
                    (rid, story["id"], actor, story["start_scene"], "{}"))
        row = con.execute("SELECT * FROM runs WHERE id=?", (rid,)).fetchone()
    return _run_output(row, story)


def get_run(path: Path, story: dict, actor: str, rid: str) -> dict:
    with _connect(path) as con:
        row = con.execute("SELECT * FROM runs WHERE id=? AND demo_actor=?", (rid, actor)).fetchone()
    if row is None or row["story_id"] != story["id"]:
        raise RunNotFound()
    return _run_output(row, story)


def choose(path: Path, story: dict, actor: str, rid: str, choice_id: str,
           expected_version: int, idem_key: str) -> dict:
    con = _connect(path)
    try:
        con.execute("BEGIN IMMEDIATE")
        row = con.execute("SELECT * FROM runs WHERE id=? AND demo_actor=?", (rid, actor)).fetchone()
        if row is None or row["story_id"] != story["id"]:
            raise RunNotFound()
        replay = con.execute("SELECT response_json, choice_id FROM events WHERE run_id=? AND idem_key=?",
                             (rid, idem_key)).fetchone()
        if replay is not None:
            if replay["choice_id"] != choice_id:
                raise ReplayConflict("Idempotency key reused for a different action")
            con.execute("COMMIT")
            return json.loads(replay["response_json"])
        if row["version"] != expected_version:
            raise VersionConflict("Run was changed; reload the latest state")
        flags = json.loads(row["flags_json"])
        t = transition(story, row["scene_id"], choice_id, flags)
        con.execute("UPDATE runs SET scene_id=?,flags_json=?,version=version+1,"
                    "updated_at=CURRENT_TIMESTAMP WHERE id=?",
                    (t.target, json.dumps(t.flags, ensure_ascii=False, sort_keys=True), rid))
        updated = con.execute("SELECT * FROM runs WHERE id=?", (rid,)).fetchone()
        response = _run_output(updated, story)
        con.execute("INSERT INTO events(run_id,idem_key,from_scene,to_scene,choice_id,response_json) "
                    "VALUES(?,?,?,?,?,?)",
                    (rid, idem_key, row["scene_id"], t.target, choice_id,
                     json.dumps(response, ensure_ascii=False)))
        con.execute("COMMIT")
        return response
    except Exception:
        con.execute("ROLLBACK")
        raise
    finally:
        con.close()


def event_history(path: Path, actor: str, rid: str) -> list[dict]:
    with _connect(path) as con:
        row = con.execute("SELECT id FROM runs WHERE id=? AND demo_actor=?", (rid, actor)).fetchone()
        if row is None:
            raise RunNotFound()
        events = con.execute("SELECT choice_id,from_scene,to_scene,created_at FROM events "
                             "WHERE run_id=? ORDER BY id", (rid,)).fetchall()
    return [dict(e) for e in events]
