from tabulate import tabulate


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


print_table(jobs_tag("work"))
