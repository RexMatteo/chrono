from datetime import datetime
from tabulate import tabulate
from rich.console import Console
from rich.table import Table


def jobs_tag(type: str, value: str | None = None):
    work_tag = {
        "1": "Fitting & Setting",
        "2": "Start Up",
        "3": "Commissioning",
        "4": "Warranty Work",
        "5": "Tech Assistance",
        "6": "Training - Demo",
        "7": "Test",
        "8": "Site Survey",
        "9": "Diagnostic Visit",
        "10": "Refurbishment",
        "11": "Option - Upgrade",
        "12": "Invoiced Work",
        "13": "Day Off On Job",
        "14": "Day Off At Home",
        "15": "Not Chargeable",
        "16": "Others",
        "T": "Travel",
    }

    wait_tag = {
        "A": "Waiting For End User",
        "B": "Waiting For Supplier",
        "C": "Waiting For Customer",
    }

    out_of_range_tags = {
        "D": "Adjustaments",
        "E": "Repair",
        "F": "Problem Research",
        "G": "Customer Request",
        "H": "On Site Final Touch",
        "I": "Work On Ancillary",
        "J": "MIssing Parts",
        "K": "Others",
    }

    match type:
        case "work":
            tag = work_tag
        case "wait":
            tag = wait_tag
        case "out":
            tag = out_of_range_tags
        case _:
            raise ValueError(f"Tipo non riconosciuto: {type}")

    if value is None:
        return tag

    return tag.get(value)


def print_table(d):
    rows = [(k, v) for k, v in d.items()]
    print(tabulate(rows, headers=["Codice", "Descrizione"], tablefmt="fancy_grid"))


def dict_to_table(rows: list[dict] | None = None, *, title: str):
    """Crea una tabella dinamica in base alle chiavi presenti nei dizionari passati."""
    if not rows:
        print("Nessun cliente trovato.")
        return

    # Usa le chiavi del primo dict come intestazioni
    fieldnames = list(rows[0].keys())
    table = Table(title=title)
    table.add_column("index")

    for field in fieldnames:
        table.add_column(field)

    for idx, row in enumerate(rows, start=1):
        table.add_row(str(idx), *[str(row.get(field, "")) for field in fieldnames])

    Console().print(table)


def is_data_valid(v: str) -> bool:
    try:
        datetime.strptime(v, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_time_valid(v: str) -> bool:
    try:
        datetime.strptime(v, "%H:%M")
        return True
    except ValueError:
        return False
