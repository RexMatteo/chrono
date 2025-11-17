import db_connector as ts
import typer
from datetime import datetime
from errors import ClientNotFound, MultiPlantFound, PlantNotFound, ProjectNotFound

oggi = datetime.now().date().isoformat()
app = typer.Typer()


# --------------------------------------------------------------------------------------------------------------

# ECCEZIONI

# --------------------------------------------------------------------------------------------------------------


def stabilimento_non_trovato(nome_cliente, citta_cliente, progetto):
    if typer.confirm("Non ho trovato il plant in archivio, vuoi aggiungerlo? "):
        aggiungi_cliente(nome=nome_cliente, citta=citta_cliente)
        ts.add_project(
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
            ts.add_job(oggi, progetto, inizio, fine)
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
def lista_clienti_cli():
    for c in ts.list_clients():
        print(f"{c['name']} - {c['city']}")


@app.command()
def aggiungi_cliente_cli(
    nome: str = typer.Option(None, "--nome", "-n", prompt="Nome"),
    citta: str = typer.Option(None, "--città", "-c", prompt="Città"),
    nazione: str = typer.Option(None, "--nazione", "-s", prompt="Nazione"),
) -> None:

    ts.add_client(nome, citta, nazione)
    if ts.exist("clients", "name", nome):
        typer.echo(f"Il cliente {nome} con lo stablimento in {citta} è stato creato!")
    else:
        typer.echo(f"il cliente {nome} non è stato salvato correttamente")


@app.command()
def cancella_cliente_cli(
    nome: str = typer.Option(None, "--nome", "-n", prompt="Nome"),
):
    ts.delete_client(nome)
    if ts.exist("clients", "name", nome):
        typer.echo(f"Cancellazione non andata a buon fine")
    else:
        typer.echo(f"Cancellato!")


@app.command()
def aggiorna_cliente_cli():
    return


# Progetti


@app.command()
def aggiorna_stato_progetto_cli(
    stato: bool = typer.Option(None, "--stato", "-s", prompt="Stato progetto"),
    progetto: str = typer.Option(None, "--progetto", "-p", prompt="Codice progetto"),
):
    ts.update_project_state(stato, progetto)


def aggiungi_progetto(progetto, nome_cliente, citta_cliente):
    try:
        ts.add_project(
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

        ts.add_project(
            client_name=nome_cliente, project_name=progetto, city=citta_cliente
        )
        print(
            f"Ho creato il progetto {progetto} e l'ho assegnato allo stabilimento {nome_cliente} {citta_cliente}"
        )


@app.command()
def aggiungi_progetto_cli(
    progetto: str = typer.Option(None, "--progetto", "-p", prompt="Codice progetto"),
    nome_cliente: str = typer.Option(None, "--cliente", "-c", prompt="Cliente"),
    citta_cliente: str = typer.Option(
        None, "--citta", "-C", prompt="Stabilimento (città)"
    ),
) -> None:
    aggiungi_progetto(progetto, nome_cliente, citta_cliente)


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
    ts.change_project_name(nuovo, vecchio)
    print(f"Ho cambiat nome al progetto da {vecchio} a {nuovo}.")


@app.command()
def cancella_progetto(
    progetto: str = typer.Option(None, "--progetto", "-p", prompt="Codice progetto"),
):
    ts.delete_project(progetto)


# Jobs


@app.command()
def controlla_stato_progetti():
    stato = ts.check_project_state()
    print(*(f"{i}. {d['name']}" for i, d in enumerate(stato, start=1)), sep="\n")


def aggiungi_job(at_start, at_end):
    oggi = datetime.now().date().isoformat()
    inizio = f"{oggi} {at_start}:00"
    fine = f"{oggi} {at_end}:00"

    try:
        # codice che può generare un errore
        progetti_attivi = ts.check_project_state()
        if len(progetti_attivi) > 1:
            for project in progetti_attivi:
                typer.echo(project["name"])
            progetto = input("Cisono più progetti attivi, quale scegli?")
        else:
            progetto = progetti_attivi[0]["name"]
        ts.add_job(oggi, progetto, inizio, fine)
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
    projects = ts.list_project()
    if not projects:
        print("non ho trovato progetti in tabella")
        return
    for project in projects:
        print(f"Progetto: {project['project']} - {project['client']}")


# def report_giornaliero(giorno) -> None:
#    righe, totali = ts.day_report(giorno)
#    print(f"Totale ore: {totali}")


# --------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    app()
