import controller.db_connector as ts
import controller.utility as util
import model.projects as project
import model.clients as client
import typer
from datetime import datetime

oggi = datetime.now().date().isoformat()
app = typer.Typer()


# --------------------------------------------------------------------------------------------------------------

# ECCEZIONI

# --------------------------------------------------------------------------------------------------------------


def validazione_input(prompt, validazione):
    while True:
        value = input(prompt).strip()
        if validazione(value):
            return value
        print("⚠️  Input non valido. Riprova.\n")


def ask_stop_process():
    delete = typer.confirm("Vuoi procedere?")
    if not delete:
        print("❌ Annullato")
        return


# --------------------------------------------------------------------------------------------------------------

## AGGIUNTA DATI

# --------------------------------------------------------------------------------------------------------------

# Clienti


@app.command()
def lista_clienti():
    rows = client.list_clients()
    util.dict_to_table(rows, title="Lista Clienti")
    return rows


@app.command()
def aggiungi_cliente(
    nome: str = typer.Option(None, "--nome", "-n", prompt="Nome"),
    citta: str = typer.Option(None, "--città", "-c", prompt="Città"),
    nazione: str = typer.Option(None, "--nazione", "-s", prompt="Nazione"),
) -> None:
    cl = client.Client(nome, citta, nazione)
    ask_stop_process()
    client.add_client(cl)
    if ts.exist("clients", "name", nome):
        typer.echo(f"Il cliente {nome} con lo stablimento in {citta} è stato creato!")
    else:
        typer.echo("❌ Annullato")


@app.command()
def aggiorna_cliente():
    new = client.Client()
    old = client.Client()
    rows = lista_clienti()
    index = validazione_input(
        "Quale cliente cambi? ",
        lambda v: v.isdigit() and 1 <= int(v) <= len(rows),
    )
    old.name = rows[int(index) - 1]["name"]
    old.city = rows[int(index) - 1]["city"]
    typer.echo("inserisci i nuovi parametri.")
    new.name = typer.prompt("    nuovo nome? ")
    new.city = typer.prompt("    nuova città? ")
    new.nation = typer.prompt("    nuova nazione? ")
    ask_stop_process()
    client.update_client(new, old)
    return


@app.command()
def cancella_cliente():
    rows = lista_clienti()
    cl = client.Client()
    index = validazione_input(
        "Quale cliente cancelli? ",
        lambda v: v.isdigit() and 1 <= int(v) <= len(rows),
    )
    cl.name = rows[int(index) - 1]["name"]
    cl.city = rows[int(index) - 1]["city"]
    ask_stop_process()
    client.delete_client(cl)
    if ts.exist("clients", "city", cl.city):
        typer.echo("Cancellazione non andata a buon fine")
    else:
        typer.echo("✅ Cancellato")


# Progetti


@app.command()
def lista_progetti():
    rows = project.list_project()
    util.dict_to_table(rows, title="Lista Progetti")
    return rows


@app.command()
def lista_progetti_attivi():
    rows = project.list_active_project()
    util.dict_to_table(rows, title="Lista Progetti Attivi")
    return rows


@app.command()
def aggiorna_stato_progetto():
    rows = lista_progetti()
    p = project.Project()
    index = typer.prompt("Quale progetto vuoi cambiare? ")
    p.name = rows[int(index) - 1]["project"]
    p.active = not rows[int(index) - 1]["active"]
    ask_stop_process()
    project.update_project_state(p)


@app.command()
def aggiungi_progetto():
    rows = lista_clienti()
    pr = project.Project()
    cl = client.Client()
    index = validazione_input(
        "Quale cliente scegli? ",
        lambda v: v.isdigit() and 1 <= int(v) <= len(rows),
    )
    cl.name = rows[int(index) - 1]["name"]
    cl.city = rows[int(index) - 1]["city"]
    pr.name = typer.prompt("Quale nome vuoi usare?")
    ask_stop_process()
    project.add_project(pr, cl)


@app.command()
def cambia_nome_progetto() -> None:
    rows = lista_progetti()
    vp = project.Project()
    np = project.Project()
    index = validazione_input(
        "Quale cliente scegli? ",
        lambda v: v.isdigit() and 1 <= int(v) <= len(rows),
    )
    vp.name = rows[int(index) - 1]["project"]
    np.name = validazione_input(
        "Che nome diamo al progetto? ",
        lambda v: len(v) > 0,
    )
    ask_stop_process()
    project.change_project_name(np, vp)
    print(f"Ho cambiat nome al progetto da {vp.name} a {np.name}.")


@app.command()
def cancella_progetto():
    rows = lista_progetti()
    p = project.Project()
    index = validazione_input(
        "quale progetto vuoi cancellare?",
        lambda v: v.isdigit() and 1 <= int(v) <= len(rows),
    )
    p.name = rows[int(index) - 1]["project"]
    ask_stop_process()
    project.delete_project(p)


@app.command()
def controlla_stato_progetti():
    stato = project.check_project_state()
    print(*(f"{i}. {d['name']}" for i, d in enumerate(stato, start=1)), sep="\n")


# Jobs


@app.command()
def aggiungi_job():
    lista_progetti_attivi()

    data = validazione_input(
        "Inserisci la data (YYYY-MM-DD): ",
        util.is_data_valid,
    )
    typer.echo(data)
    at_start = validazione_input(
        "A che ora hai cominciato? ",
        util.is_time_valid,
    )
    at_end = validazione_input(
        "A che ora hai cominciato? ",
        util.is_time_valid,
    )
    inizio = f"{data} {at_start}:00"
    fine = f"{data} {at_end}:00"
    typer.echo(f"questo giorno {data} hai iniziato alle {inizio} e finito alle {fine}")


@app.command()
def cancella_job():
    return


##RECUPERO DATI


# def report_giornaliero(giorno) -> None:
#    righe, totali = ts.day_report(giorno)
#    print(f"Totale ore: {totali}")


# --------------------------------------------------------------------------------------------------------------


@app.command()
def init_database():
    ts.init_db()
    typer.echo(f"Database creato in:{ts.DB_PATH}")


if __name__ == "__main__":
    app()
