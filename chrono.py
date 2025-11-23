import controller.db_connector as ts
from controller.errors import (
    ClientNotFound,
    MultiPlantFound,
    PlantNotFound,
    ProjectNotFound,
)
import model.projects as project
import model.clients as client
import model.jobs as job
import typer
from datetime import datetime

oggi = datetime.now().date().isoformat()
app = typer.Typer()


# --------------------------------------------------------------------------------------------------------------

# ECCEZIONI

# --------------------------------------------------------------------------------------------------------------


def stabilimento_non_trovato(nome_cliente, citta_cliente, progetto):
    if typer.confirm("Non ho trovato il plant in archivio, vuoi aggiungerlo? "):
        aggiungi_cliente(nome=nome_cliente, citta=citta_cliente)
        project.add_project(
            client_name=nome_cliente,
            project_name=progetto,
            city=citta_cliente,
        )
        typer.echo(
            f"Ho creato il progetto {progetto} e l'ho assegnato allo stabilimento {nome_cliente} {citta_cliente}"
        )
    else:
        typer.echo("Ok torna quando vuoi!")


def progetto_non_trovato(progetto, inizio, fine):
    if typer.confirm("Vuoi creare un nuovo progetto con questo nome?"):
        nome_cliente = typer.prompt("A quale cliente associ questo progetto")
        citta_cliente = typer.prompt("In quale città risiede il cliente")
        try:
            aggiungi_progetto(
                progetto=progetto,
                nome_cliente=nome_cliente,
                citta_cliente=citta_cliente,
            )
            job.add_job(oggi, progetto, inizio, fine)
            typer.echo(f"Ho segnato la lavorazione sulla commessa {progetto}!")

        except PlantNotFound as e:
            print(e)
            stabilimento_non_trovato(nome_cliente, citta_cliente, progetto)
    else:
        return


def validazione_input(prompt, validazione):
    while True:
        value = input(prompt).strip()
        if validazione(value):
            return value
        print("⚠️  Input non valido. Riprova.\n")


# --------------------------------------------------------------------------------------------------------------

## AGGIUNTA DATI

# --------------------------------------------------------------------------------------------------------------

# Clienti


@app.command()
def lista_clienti():
    rows = client.list_clients()
    for c in rows:
        print(f"{c['name']} - {c['city']} - {c['nation']}")


@app.command()
def aggiungi_cliente(
    nome: str = typer.Option(None, "--nome", "-n", prompt="Nome"),
    citta: str = typer.Option(None, "--città", "-c", prompt="Città"),
    nazione: str = typer.Option(None, "--nazione", "-s", prompt="Nazione"),
) -> None:
    cl = client.Client(nome, citta, nazione)
    client.add_client(cl)
    if ts.exist("clients", "name", nome):
        typer.echo(f"Il cliente {nome} con lo stablimento in {citta} è stato creato!")
    else:
        typer.echo("❌ Annullato")


@app.command()
def aggiorna_cliente():
    scelte = {}
    new = client.Client()
    old = client.Client()
    rows = client.list_clients()

    for c in range(1, len(rows) + 1):
        s = c - 1
        scelte[c] = f"{c} - {rows[s]['name']}, {rows[s]['city']}, {rows[s]['nation']}"
        typer.echo(scelte[c])

    index = typer.prompt("Quale cliente cambi? ")
    old.name = rows[int(index) - 1]["name"]
    old.city = rows[int(index) - 1]["city"]
    typer.echo("inserisci i nuovi parametri.")
    new.name = typer.prompt("    nuovo nome? ")
    new.city = typer.prompt("    nuova città? ")
    new.nation = typer.prompt("    nuova nazione? ")
    delete = typer.confirm("Sicuto di voler modificafe il cliente?")
    if not delete:
        return
    client.update_client(new, old)
    return


@app.command()
def cancella_cliente():
    typer.echo(lista_clienti())
    nome: str = typer.prompt("Nome")
    citta: str = typer.prompt("Città")
    delete = typer.confirm("Vuoi cancellare davvero i cliente e i progetti relativi?")
    if not delete:
        print("❌ Annullato")
        return
    cl = client.Client(nome, citta)
    client.delete_client(cl)
    if ts.exist("clients", "name", nome):
        typer.echo("Cancellazione non andata a buon fine")
    else:
        typer.echo("✅ Cancellato")


# Progetti


@app.command()
def aggiorna_stato_progetto(
    stato: bool = typer.Option(None, "--stato", "-s", prompt="Stato progetto"),
    progetto: str = typer.Option(None, "--progetto", "-p", prompt="Codice progetto"),
):
    project.update_project_state(stato, progetto)


@app.command()
def aggiungi_progetto(
    progetto: str = typer.Option(None, "--progetto", "-p", prompt="Codice progetto"),
    nome_cliente: str = typer.Option(None, "--cliente", "-c", prompt="Cliente"),
    citta_cliente: str = typer.Option(
        None, "--citta", "-C", prompt="Stabilimento (città)"
    ),
) -> None:
    try:
        project.add_project(
            client_name=nome_cliente, project_name=progetto, city=citta_cliente
        )
        typer.echo(
            f"Ho creato il progetto {progetto} e l'ho assegnato allo stabilimento {nome_cliente} {citta_cliente}"
        )

    except ClientNotFound as e:
        typer.echo(e)
        stabilimento_non_trovato(nome_cliente, citta_cliente, progetto)

    except MultiPlantFound as e:
        print(
            "Non hai scelto il plant, se ti serve un suggerimento te li elenco qua sotto: "
        )
        print(e.cities)
        citta_cliente = input(f"A quale plant vuoi associare a {progetto}: ")
        if not citta_cliente:
            print("Ritorna quando avrai scelto!")
            return

        project.add_project(
            client_name=nome_cliente, project_name=progetto, city=citta_cliente
        )
        print(
            f"Ho creato il progetto {progetto} e l'ho assegnato allo stabilimento {nome_cliente} {citta_cliente}"
        )


@app.command()
def cambia_nome_progetto() -> None:
    lista_progetti()
    vecchio = validazione_input(
        "Quale progetto vuoi modificare? ",
        lambda v: ts.exist("projects", "name", v),
    )
    nuovo = validazione_input(
        "Che nome diamo al progetto? ",
        lambda v: len(v) > 0,
    )
    project.change_project_name(nuovo, vecchio)
    print(f"Ho cambiat nome al progetto da {vecchio} a {nuovo}.")


@app.command()
def cancella_progetto(
    progetto: str = typer.Option(None, "--progetto", "-p", prompt="Codice progetto"),
):
    project.delete_project(progetto)


# Jobs


@app.command()
def controlla_stato_progetti():
    stato = project.check_project_state()
    print(*(f"{i}. {d['name']}" for i, d in enumerate(stato, start=1)), sep="\n")


def aggiungi_job(at_start, at_end):
    oggi = datetime.now().date().isoformat()
    inizio = f"{oggi} {at_start}:00"
    fine = f"{oggi} {at_end}:00"

    try:
        # codice che può generare un errore
        progetti_attivi = project.check_project_state()
        if len(progetti_attivi) > 1:
            for p in progetti_attivi:
                typer.echo(p["name"])
            progetto = input("Cisono più progetti attivi, quale scegli?")
        else:
            progetto = progetti_attivi[0]["name"]
        job.add_job(oggi, progetto, inizio, fine)
        typer.echo(f"Ho segnato la lavorazione sulla commessa {progetto}!")

    # non ho trovato il progetto in archivio
    except ProjectNotFound as e:
        typer.echo(e)
        progetto_non_trovato(progetto, inizio, fine)


@app.command()
def aggiungi_job_cli(
    #    progetto: str = typer.Option(None, "--progetto", "-p", prompt="Codice progetto"),
    at_start: str = typer.Option(None, "--inizio", "-i", prompt="Ora inizio"),
    at_end: str = typer.Option(None, "--fine", "-f", prompt="Ora fine"),
):
    aggiungi_job(at_start, at_end)


@app.command()
def cancella_job():
    return


##RECUPERO DATI


@app.command()
def lista_progetti():
    projects = project.list_project()
    if not projects:
        print("non ho trovato progetti in tabella")
        return
    for p in projects:
        print(f"Progetto: {p['project']} - {p['client']}")


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
