"""Versioned database schema migrations, append-only immutability triggers, and Postgres DDL/RLS.

Implements T003 data architecture:
- Tracks applied migrations with SHA-256 checksums in `schema_migrations`.
- Enforces append-only immutability on `events` and `security_audit_log` via DB triggers.
- Pins `runs` to immutable `editions` (`INT-08`) and stores `story_snapshots` (`INT-18`).
- Provides target PostgreSQL DDL + Row-Level Security (RLS) policy definitions.
"""
from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    up_sql: str


MIGRATIONS: tuple[Migration, ...] = (
    Migration(
        version=1,
        name="001_initial_runs_and_events",
        up_sql="""
        CREATE TABLE IF NOT EXISTS runs (
            id TEXT PRIMARY KEY,
            story_id TEXT NOT NULL,
            edition_id TEXT NOT NULL DEFAULT 'ben-kia-canh-cua-ed1',
            demo_actor TEXT NOT NULL,
            scene_id TEXT NOT NULL,
            flags_json TEXT NOT NULL,
            version INTEGER NOT NULL DEFAULT 0,
            state_checksum TEXT NOT NULL DEFAULT '',
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
            event_hash TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(run_id, idem_key)
        );
        """,
    ),
    Migration(
        version=2,
        name="002_auth_rbac_editions_snapshots_and_immutability",
        up_sql="""
        CREATE TABLE IF NOT EXISTS editions (
            id TEXT PRIMARY KEY,
            work_id TEXT NOT NULL,
            version INTEGER NOT NULL DEFAULT 1,
            content_sha256 TEXT NOT NULL,
            story_json TEXT NOT NULL,
            published_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS story_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL REFERENCES runs(id),
            edition_id TEXT NOT NULL,
            version INTEGER NOT NULL,
            scene_id TEXT NOT NULL,
            flags_json TEXT NOT NULL,
            state_checksum TEXT NOT NULL,
            last_event_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(run_id, version)
        );

        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'listener',
            display_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            deleted_at TEXT
        );

        CREATE TABLE IF NOT EXISTS device_sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id),
            device_name TEXT NOT NULL,
            refresh_token_hash TEXT NOT NULL,
            access_jti TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            revoked_at TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS guest_migrations (
            guest_actor TEXT PRIMARY KEY,
            target_user_id TEXT NOT NULL REFERENCES users(id),
            migrated_runs INTEGER NOT NULL,
            migrated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS security_audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actor_id TEXT NOT NULL,
            actor_role TEXT NOT NULL,
            action TEXT NOT NULL,
            target_id TEXT,
            decision TEXT NOT NULL,
            detail TEXT NOT NULL,
            prev_hash TEXT NOT NULL,
            entry_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TRIGGER IF NOT EXISTS trg_events_no_update
        BEFORE UPDATE ON events
        BEGIN
            SELECT RAISE(ABORT, 'events table is append-only and immutable');
        END;

        CREATE TRIGGER IF NOT EXISTS trg_events_no_delete
        BEFORE DELETE ON events
        BEGIN
            SELECT RAISE(ABORT, 'events table is append-only and immutable');
        END;

        CREATE TRIGGER IF NOT EXISTS trg_security_audit_no_update
        BEFORE UPDATE ON security_audit_log
        BEGIN
            SELECT RAISE(ABORT, 'security_audit_log table is append-only and immutable');
        END;

        CREATE TRIGGER IF NOT EXISTS trg_security_audit_no_delete
        BEFORE DELETE ON security_audit_log
        BEGIN
            SELECT RAISE(ABORT, 'security_audit_log table is append-only and immutable');
        END;
        """,
    ),
    Migration(
        version=3,
        name="003_private_media_registry_entitlements_and_delivery_logs",
        up_sql="""
        CREATE TABLE IF NOT EXISTS media_objects (
            asset_id TEXT PRIMARY KEY,
            work_id TEXT NOT NULL,
            edition_id TEXT NOT NULL,
            scene_id TEXT NOT NULL,
            storage_relpath TEXT NOT NULL,
            sha256 TEXT NOT NULL,
            byte_size INTEGER NOT NULL,
            content_type TEXT NOT NULL DEFAULT 'audio/mpeg',
            rights_grant_id TEXT NOT NULL,
            rights_grant_version INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'published',
            cache_epoch INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS user_entitlements (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            work_id TEXT NOT NULL,
            allow_stream INTEGER NOT NULL DEFAULT 1,
            allow_offline INTEGER NOT NULL DEFAULT 0,
            expires_at TEXT NOT NULL,
            revoked_at TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS media_delivery_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actor_id TEXT NOT NULL,
            asset_id TEXT NOT NULL,
            action TEXT NOT NULL,
            status_code INTEGER NOT NULL,
            bytes_served INTEGER NOT NULL DEFAULT 0,
            detail TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """,
    ),
)


def _migration_checksum(sql: str) -> str:
    normalized = "\n".join(line.strip() for line in sql.strip().splitlines() if line.strip())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _ensure_column(con: sqlite3.Connection, table: str, column: str, ddl_type: str) -> None:
    cols = {row[1] for row in con.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in cols:
        con.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl_type}")


def apply_migrations(con: sqlite3.Connection) -> list[int]:
    """Apply pending migrations idempotently and verify applied migration checksums."""
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            checksum TEXT NOT NULL,
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    applied_rows = con.execute(
        "SELECT version, name, checksum FROM schema_migrations ORDER BY version"
    ).fetchall()
    applied = {row[0]: (row[1], row[2]) for row in applied_rows}
    newly_applied: list[int] = []

    for m in MIGRATIONS:
        csum = _migration_checksum(m.up_sql)
        if m.version in applied:
            existing_name, existing_csum = applied[m.version]
            if existing_name != m.name or existing_csum != csum:
                raise RuntimeError(
                    f"Migration {m.version} ({m.name}) checksum mismatch against applied DB"
                )
            continue
        con.executescript(m.up_sql)
        # Ensure columns exist when upgrading a legacy pre-T003 SQLite file
        if m.version == 1:
            _ensure_column(
                con,
                "runs",
                "edition_id",
                "TEXT NOT NULL DEFAULT 'ben-kia-canh-cua-ed1'",
            )
            _ensure_column(con, "runs", "state_checksum", "TEXT NOT NULL DEFAULT ''")
            _ensure_column(con, "events", "event_hash", "TEXT NOT NULL DEFAULT ''")
        con.execute(
            "INSERT INTO schema_migrations(version, name, checksum) VALUES(?, ?, ?)",
            (m.version, m.name, csum),
        )
        newly_applied.append(m.version)

    return newly_applied


def postgres_target_ddl() -> str:
    """Return the canonical PostgreSQL production DDL with Row-Level Security (RLS) policies."""
    return """
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'listener',
    display_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS device_sessions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    device_name TEXT NOT NULL,
    refresh_token_hash TEXT NOT NULL,
    access_jti TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS editions (
    id TEXT PRIMARY KEY,
    work_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    content_sha256 CHAR(64) NOT NULL,
    story_json JSONB NOT NULL,
    published_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS runs (
    id UUID PRIMARY KEY,
    story_id TEXT NOT NULL,
    edition_id TEXT NOT NULL REFERENCES editions(id),
    user_id TEXT NOT NULL,
    scene_id TEXT NOT NULL,
    flags_json JSONB NOT NULL,
    version INTEGER NOT NULL DEFAULT 0,
    state_checksum CHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS events (
    id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES runs(id),
    idem_key TEXT NOT NULL,
    from_scene TEXT NOT NULL,
    to_scene TEXT NOT NULL,
    choice_id TEXT NOT NULL,
    response_json JSONB NOT NULL,
    event_hash CHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(run_id, idem_key)
);

ALTER TABLE runs ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_runs ON runs
    USING (user_id = current_setting('app.current_user_id', true));

ALTER TABLE events ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_events ON events
    USING (
        run_id IN (
            SELECT id FROM runs WHERE user_id = current_setting('app.current_user_id', true)
        )
    );
""".strip()
