#!/usr/bin/env python3
from controller import db_connector as db
from model.clients import Client
from typing import Optional


class Project:
    name: Optional[str] = None
    color: Optional[str] = None
    active: Optional[int] = None


def add_project(p_params: Project, c_params: Client):
    with db.transaction() as cx:
        sql_id = "SELECT id FROM clients WHERE name = ? AND city = ?"
        sql_add = (
            "INSERT OR IGNORE INTO projects(client_id, name, color) VALUES (?, ?, ?)"
        )
        row = cx.execute(
            sql_id,
            (
                c_params.name,
                c_params.city,
            ),
        ).fetchone()
        client_id = row[0]
        cx.execute(
            sql_add,
            (client_id, p_params.name, p_params.color),
        )
    return


def update_project_state(params: Project):
    with db.transaction() as cx:
        cx.execute(
            "UPDATE projects SET active = ? WHERE name = ? COLLATE NOCASE;",
            (params.active, params.name),
        )
        return


def check_project_state():
    query = "SELECT name FROM projects WHERE active=1"
    return [dict(r) for r in db.get_all(query)]


def change_project_name(new_params: Project, old_params: Project):
    with db.transaction() as cx:
        cx.execute(
            """
            UPDATE projects SET name = ? WHERE name= ? COLLATE NOCASE;
            """,
            (new_params.name, old_params.name),
        )


def list_project():
    query = "SELECT p.name AS project, c.name AS client, active FROM projects p JOIN clients c ON c.id = p.client_id ORDER BY client, project"
    return [dict(r) for r in db.get_all(query)]


def list_active_project():
    query = "SELECT p.name AS project, c.name AS client, active FROM projects p JOIN clients c ON c.id = p.client_id WHERE p.active = 1 ORDER BY client, project"
    return [dict(r) for r in db.get_all(query)]


def delete_project(params: Project):
    with db.transaction() as cx:
        cx.execute(
            "DELETE FROM projects WHERE name = ? COLLATE NOCASE",
            (params.name,),
        )
