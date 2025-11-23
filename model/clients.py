#!/usr/bin/env python3
from controller import db_connector as db
from dataclasses import dataclass
from typing import Optional


@dataclass
class Client:
    name: Optional[str] = None
    city: Optional[str] = None
    nation: Optional[str] = None
    notes: Optional[str] = None


def list_clients():
    return [
        r
        for r in db.get_all(
            "SELECT name, city, nation FROM clients ORDER BY name, city, nation"
        )
    ]


def add_client(params: Client):
    with db.transaction() as cx:
        cx.execute(
            "INSERT OR IGNORE INTO clients(name, city, nation, notes) VALUES (?,?,?,?)",
            (params.name, params.city, params.nation, params.notes),
        )
        return


def update_client(new_params: Client, old_params: Client):
    sql = (
        "UPDATE clients SET name = ?, city = ?, nation = ? WHERE name = ? AND city = ?"
    )
    with db.transaction() as cx:
        cx.execute(
            sql,
            (
                new_params.name,
                new_params.city,
                new_params.nation,
                old_params.name,
                old_params.city,
            ),
        )
        return


def delete_client(params: Client):
    q_project_count = "SELECT COUNT(*) FROM projects p JOIN clients c ON c.id = p.client_id WHERE c.name = ? COLLATE NOCASE;"
    with db.transaction() as cx:
        cx.execute(
            "DELETE FROM clients WHERE name = ? COLLATE NOCASE",
            (params.name,),
        )
        return
