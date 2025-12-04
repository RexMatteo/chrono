#!/usr/bin/env python3
import sqlite3
from pathlib import Path
from contextlib import contextmanager


DB_PATH = Path("controller/timesheet.sqlite")

ALLOWED = {
    "clients": {"name", "city", "nation"},
    "projects": {"name", "client_id", "active"},
    "workdays": {"day"},
    "jobs": {"workday_id", "project_id"},
}

SCHEMA_SQL = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS clients (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  city TEXT NOT NULL UNIQUE,
  nation TEXT,
  notes TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  client_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  color TEXT,
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(client_id, name),
  FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,
  start_at TEXT NOT NULL,      -- ISO 8601: 2025-11-02T09:30:00
  end_at   TEXT NOT NULL,
  place TEXT,
  work_type TEXT,
  description TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_jobs_project ON jobs(project_id);
"""


def connect(db_path=DB_PATH, timeout=5.0):
    conn = sqlite3.connect(
        db_path,
        timeout=timeout,
        isolation_level=None,
        detect_types=sqlite3.PARSE_DECLTYPES,
    )
    conn.row_factory = sqlite3.Row

    # PRAGMA da impostare a ogni connessione
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")  # bilancia durabilità/performance
    conn.execute("PRAGMA busy_timeout = 5000;")  # evita Immediate 'database is locked'

    return conn


@contextmanager
def transaction():
    cx = connect()
    try:
        cx.execute("BEGIN")
        yield cx
        cx.execute("COMMIT")
    except:
        cx.execute("ROLLBACK")
        raise
    finally:
        cx.close()


def init_db():
    with connect() as cx:
        cx.executescript(SCHEMA_SQL)


def exist(table: str, column: str, value):
    query = f"SELECT 1 FROM {table} WHERE {column} = ? COLLATE NOCASE LIMIT 1;"
    if table not in ALLOWED or column not in ALLOWED[table]:
        raise ValueError(f"Tabella/colonna non ammessa: {table}.{column}")
    with connect() as cx:
        row = cx.execute(query, (value,)).fetchone()
        return row is not None


def get_one(sql: str, params: tuple | list = ()) -> dict:
    with connect() as cx:
        rows = cx.execute(sql, params).fetchone()
        return dict(rows) if rows else {}


def get_all(sql: str, params: tuple | list = ()) -> list[dict]:
    with connect() as cx:
        return [dict(row) for row in cx.execute(sql, params).fetchall()]


def backup(target_path: Path):
    """Backup 'a caldo' sicuro con .backup di SQLite."""
    import subprocess

    subprocess.run(["sqlite3", str(DB_PATH), f".backup '{target_path}'"], check=True)
