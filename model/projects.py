#!/usr/bin/env python3
from controller import db_connector as db
from controller import errors as er


def add_project_new(client_name, project_name, color=None, city=None):
    query_city = (
        "SELECT id FROM clients WHERE name=? COLLATE NOCASE AND city=? COLLATE NOCASE"
    )
    query_city_list = "SELECT id, city FROM clients WHERE name=? COLLATE NOCASE"
    query_no_city = (
        "SELECT id, city FROM clients WHERE name=? COLLATE NOCASE",
        (client_name,),
    )
    if city:
        row = db.get_one(
            query_city,
            (client_name, city),
        )
        if not row:
            options = db.get_all(query_city_list, (client_name))
            if options:
                cities = ", ".join(sorted({r["city"] or "—" for r in options}))
                return cities
        client_id = row["id"]
    else:
        rows = db.get_all(
            query_city_list,
            (client_name),
        )
        if rows:
            client_id = rows

    return


def add_project(client_name, project_name, color=None, city=None):
    with db.connect() as cx:
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
                        raise er.MultiPlantFound(client_name, cities)
                    else:
                        raise er.PlantNotFound(client_name, city)
                client_id = row["id"]

            else:
                rows = cx.execute(
                    "SELECT id, city FROM clients WHERE name=? COLLATE NOCASE",
                    (client_name,),
                ).fetchall()
                if not rows:
                    raise er.ClientNotFound(client_name)
                if len(rows) > 1:
                    cities = ", ".join(sorted({r["city"] or "—" for r in rows}))
                    raise er.MultiPlantFound(client_name, cities)
                client_id = rows[0]["id"]
        except er.ClientNotFound:
            return

        cx.execute(
            "INSERT OR IGNORE INTO projects(client_id, name, color) VALUES (?,?,?)",
            (client_id, project_name, color),
        )


def update_project_state(set_value, project_name):
    with db.connect() as cx:
        cx.execute(
            "UPDATE projects SET active = ? WHERE name = ? COLLATE NOCASE;",
            (set_value, project_name),
        )


def check_project_state():
    query = "SELECT name FROM projects WHERE active=1"
    return [dict(r) for r in db.get_all(query)]


def change_project_name(new_name, old_name):
    with db.connect() as cx:
        cx.execute(
            """
            UPDATE projects SET name = ? WHERE name= ? COLLATE NOCASE;
            """,
            (new_name, old_name),
        )
        cx.commit()


def list_project():
    query = "SELECT p.name AS project, c.name AS client FROM projects p JOIN clients c ON c.id = p.client_id ORDER BY client, project"
    return [dict(r) for r in db.get_all(query)]


def delete_project(project_name):
    with db.connect() as cx:
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
