#!/usr/bin/env python3
import sqlite3
from controller import db_connector as db
from controller import errors as er
from datetime import datetime


def ensure_workday(day_str):
    with db.connect() as cx:
        cx.execute("INSERT OR IGNORE INTO workdays(day) VALUES (?)", (day_str,))
        row = cx.execute("SELECT id FROM workdays WHERE day=?", (day_str,)).fetchone()
        return row["id"]


def get_client_and_place_by_project(project_name):
    with db.connect() as cx:
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
            raise er.ProjectNotFound(project_name)


def add_job(
    day_str,
    project_name,
    start_at_iso,
    end_at_iso,
    place=None,
    work_type=None,
    description=None,
):
    with db.connect() as cx:
        # Trova project_id
        p = cx.execute(
            "SELECT id FROM projects WHERE name=? COLLATE NOCASE", (project_name,)
        ).fetchone()
        if not p:
            #            raise ValueError(f"Progetto '{project_name}' non trovato")
            raise er.ProjectNotFound(project_name)
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
    with db.connect() as cx:
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
