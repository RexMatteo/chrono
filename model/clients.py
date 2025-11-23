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
    return [r for r in db.get_all("SELECT name, city FROM clients ORDER BY name, city")]


def add_client(params: Client):
    with db.transaction() as cx:
        cx.execute(
            "INSERT OR IGNORE INTO clients(name, city, nation, notes) VALUES (?,?,?,?)",
            (params.name, params.city, params.nation, params.notes),
        )


def update_client(params: Client):
    sql = "UPDATE clients SET name = ?, city = ? nation = ? WHERE name = ?"
    with db.transaction() as cx:
        cx.execute(
            sql,
            (params.name, params.city, params.nation),
        )
    return


def delete_client(params: Client):
    q_project_count = "SELECT COUNT(*) FROM projects p JOIN clients c ON c.id = p.client_id WHERE c.name = ? COLLATE NOCASE;"
    with db.transaction() as cx:
        pc = cx.execute(
            q_project_count,
            (params.name,),
        ).fetchone()[0]
        if (
            input(f"Elimino il cliente selezionato e i {pc} progetti relativi?").lower()
            == "s"
        ):
            cx.execute(
                "DELETE FROM clients WHERE name = ? COLLATE NOCASE",
                (params.name,),
            )
        else:
            print("❌ Annullato")
            return
