#!/usr/bin/env python3
import sqlite3
from errors import (
    ClientNotFound,
    ConnectionFailed,
    MultiPlantFound,
    PlantNotFound,
    ProjectNotFound,
)
from pathlib import Path
from datetime import datetime

DB_PATH = Path("timesheet.sqlite")

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

CREATE TABLE IF NOT EXISTS workdays (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  day TEXT NOT NULL,           -- YYYY-MM-DD
  notes TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(day)
);

CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  workday_id INTEGER NOT NULL,
  project_id INTEGER NOT NULL,
  start_at TEXT NOT NULL,      -- ISO 8601: 2025-11-02T09:30:00
  end_at   TEXT NOT NULL,
  place TEXT,
  work_type TEXT,
  description TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(workday_id) REFERENCES workdays(id) ON DELETE CASCADE,
  FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_jobs_workday ON jobs(workday_id);
CREATE INDEX IF NOT EXISTS idx_jobs_project ON jobs(project_id);
"""


# ---------------------------------------------------------------------------------------------

## DB UTILITY

# ---------------------------------------------------------------------------------------------


def connect(db_path=DB_PATH):
    try:
        conn = sqlite3.connect(db_path)
        # Restituisce dict-like rows: row["col"]
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        raise ConnectionFailed(f"Connessione a {db_path} non è riuscita: {e}")


def init_db():
    with connect() as cx:
        cx.executescript(SCHEMA_SQL)


def exist(table: str, column:str, value):
    query = f"SELECT 1 FROM {table} WHERE {column} = ? COLLATE NOCASE LIMIT 1;"
    with connect() as cx:
        row = cx.execute(query, (value,)).fetchone()
        return row is not None


# ---------------------------------------------------------------------------------------------

## CLIENTS

# ---------------------------------------------------------------------------------------------


def add_client(name, city, nation, notes=None):
    with connect() as cx:
        cx.execute(
            "INSERT OR IGNORE INTO clients(name, city, nation, notes) VALUES (?,?,?,?)",
            (name, city, nation, notes),
        )


def list_clients():
    return


def update_client():
    return


def delete_client(client_name):
    with connect() as cx:
        cx.execute("PRAGMA foreign_keys = ON")
        projects_count = cx.execute(
            """SELECT COUNT(*)
                FROM projects p
                JOIN clients c ON c.id = p.client_id
                WHERE c.name = ? COLLATE NOCASE;""",
            (client_name,),
        ).fetchone()[0]

        if (
            input(
                f"Elimino il progetto selezionato {client_name}"
                f" e i relativi jobs ({projects_count}) (s/N)"
            ).lower()
            != "s"
        ):
            print("❌ Annullato")
            return

        cx.execute(
            "DELETE FROM clients WHERE name = ? COLLATE NOCASE",
            (client_name,),
        )

        print(f"✅ Cliente '{client_name}' e {projects_count} progetti eliminati")


# ---------------------------------------------------------------------------------------------

## PROJECTS

# ---------------------------------------------------------------------------------------------


def add_project(client_name, project_name, color=None, city=None):
    with connect() as cx:
        try:
            if city:
                row = cx.execute(
                    """SELECT id FROM clients WHERE 
                    name=? COLLATE NOCASE AND 
                    city=? COLLATE NOCASE""",
                    (client_name, city),
                ).fetchone()
                if not row:
                    # Mostra suggerimenti con le città esistenti per quel nome
                    opts = cx.execute(
                        "SELECT id, city FROM clients WHERE name=? COLLATE NOCASE",
                        (client_name,),
                    ).fetchall()
                    if opts:
                        cities = ", ".join(sorted({r["city"] or "—" for r in opts}))
                        raise MultiPlantFound(client_name, cities)
                    else:
                        raise PlantNotFound(client_name, city)
                client_id = row["id"]

            else:
                rows = cx.execute(
                    "SELECT id, city FROM clients WHERE name=? COLLATE NOCASE",
                    (client_name,),
                ).fetchall()
                if not rows:
                    raise ClientNotFound(client_name)
                if len(rows) > 1:
                    cities = ", ".join(sorted({r["city"] or "—" for r in rows}))
                    raise MultiPlantFound(client_name, cities)
                client_id = rows[0]["id"]
        except ClientNotFound:
            return

        cx.execute(
            "INSERT OR IGNORE INTO projects(client_id, name, color) VALUES (?,?,?)",
            (client_id, project_name, color),
        )


def update_project_state(set_value, project_name):
    with connect() as cx:
        cx.execute(
            "UPDATE projects SET active = ? WHERE name = ? COLLATE NOCASE;",
            (set_value, project_name),
        )


def check_project_state():
    with connect() as cx:
        rows = cx.execute(
            """
            SELECT name FROM projects WHERE active=1;
            """
        )
        return [dict(row) for row in rows]


def change_project_name(new_name, old_name):
    with connect() as cx:
        cx.execute(
            """
            UPDATE projects SET name = ? WHERE name= ? COLLATE NOCASE;
            """,
            (new_name, old_name),
        )
        cx.commit()


def list_project():
    with connect() as cx:
        try:
            rows = cx.execute(
                """
                    SELECT p.name AS project, c.name AS client
                    FROM projects p
                    JOIN clients c ON c.id = p.client_id
                    ORDER BY client, project
                """
            ).fetchall()
            return [dict(row) for row in rows]
        except sqlite3.OperationalError:
            init_db()
            return


def delete_project(project_name):
    with connect() as cx:
        jobs_count = cx.execute(
            """SELECT COUNT(*) FROM jobs j JOIN projects p ON p.id = j.project_id WHERE p.name = ? COLLATE NOCASE""",
            (project_name,),
        ).fetchone()[0]

        if (
            input(
                f"Elimino il progetto selezionato {project_name}"
                f" e i relativi jobs ({jobs_count}) (s/N)"
            ).lower()
            != "s"
        ):
            print("❌ Annullato")
            return

        cx.execute(
            "DELETE FROM projects WHERE name = ? COLLATE NOCASE",
            (project_name,),
        )

        print(f"✅ Progetto '{project_name}' e {jobs_count} job eliminati")


# ---------------------------------------------------------------------------------------------

## JOBS


def add_job(
    day_str,
    project_name,
    start_at_iso,
    end_at_iso,
    place=None,
    work_type=None,
    description=None,
):
    with connect() as cx:
        # Trova project_id
        p = cx.execute(
            "SELECT id FROM projects WHERE name=? COLLATE NOCASE", (project_name,)
        ).fetchone()
        if not p:
            #            raise ValueError(f"Progetto '{project_name}' non trovato")
            raise ProjectNotFound(project_name)
        project_id = p["id"]
        workday_id = ensure_workday(day_str)

        # Validazione semplice orari
        if datetime.fromisoformat(end_at_iso) <= datetime.fromisoformat(start_at_iso):
            raise ValueError("end_at deve essere > start_at")

        client, place = get_client_and_place_by_project(project_name)

        cx.execute(
            """
            INSERT INTO jobs(workday_id, project_id, start_at, end_at, place, work_type, description)
            VALUES (?,?,?,?,?,?,?)
        """,
            (
                workday_id,
                project_id,
                start_at_iso,
                end_at_iso,
                place,
                work_type,
                description,
            ),
        )


def job_report(day_str):
    """Ritorna elenco lavori e ore totali in quella giornata."""
    with connect() as cx:
        rows = cx.execute(
            """
            SELECT j.id, p.name AS project, j.start_at, j.end_at, j.place, j.work_type, j.description
            FROM jobs j
            JOIN workdays w ON w.id = j.workday_id
            JOIN projects p ON p.id = j.project_id
            WHERE w.day = ?
            ORDER BY j.start_at
        """,
            (day_str,),
        ).fetchall()

        # Calcolo ore totali in Python (portabile tra DB)
        def hours(a, b):
            dt = datetime.fromisoformat(b) - datetime.fromisoformat(a)
            return round(dt.total_seconds() / 3600, 2)

        total = sum(hours(r["start_at"], r["end_at"]) for r in rows)
        return rows, total


def ensure_workday(day_str):
    with connect() as cx:
        cx.execute("INSERT OR IGNORE INTO workdays(day) VALUES (?)", (day_str,))
        row = cx.execute("SELECT id FROM workdays WHERE day=?", (day_str,)).fetchone()
        return row["id"]


def get_client_and_place_by_project(project_name):
    with connect() as cx:
        cx.row_factory = sqlite3.Row
        row = cx.execute(
            """
                SELECT c.name AS client, c.city AS place
                FROM projects p
                JOIN clients  c ON c.id = p.client_id
                WHERE p.name = ? COLLATE NOCASE
                LIMIT 1
            """,
            (project_name,),
        ).fetchone()
        if row is not None:
            return row["client"], row["place"]
        else:
            raise ProjectNotFound(project_name)


def backup(target_path: Path):
    """Backup 'a caldo' sicuro con .backup di SQLite."""
    import subprocess

    subprocess.run(["sqlite3", str(DB_PATH), f".backup '{target_path}'"], check=True)


if __name__ == "__main__":
    # Demo usage
    init_db()
