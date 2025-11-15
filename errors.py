class AppError(Exception):
    """base per tutte le eccezioni applicative"""


## CONNECTION


class ConnectionFailed(AppError):
    def __init__(self, name):
        self.name = name
        msg = f"La connessione a '{name}' non è riuscita"
        super().__init__(msg)


## CANT WRITE


class ClientNotSaved(AppError):
    def __init__(self, name):
        self.name = name
        msg = f"Non ho potuto salvare '{name} nella lista clienti'"
        super().__init__(msg)


class ProjectNotSaved(AppError):
    def __init__(self, name):
        self.name = name
        msg = f"Non ho potuto salvare '{name} nella lista dei progetti'"
        super().__init__(msg)


class JobNotSaved(AppError):
    def __init__(self, name):
        self.name = name
        msg = f"Non ho potuto salvare la giornata del '{name}' nel timesheet"
        super().__init__(msg)


## NOT FOUND


class ProjectListNotFound(AppError):
    def __init__(self, name=None):
        self.name = name
        msg = "Lista non trovata"
        super().__init__(msg)


class ClientNotFound(AppError):
    def __init__(self, name, city=None):
        self.name = name
        self.city = city
        msg = f"Non ho trovato '{name}' nei clienti" + (
            f" sotto '{city}'" if city else "."
        )
        super().__init__(msg)


class ProjectNotFound(AppError):
    def __init__(self, name):
        self.name = name
        msg = f"Non ho trovato '{name} nei progetti'"
        super().__init__(msg)


class JobNotFound(AppError):
    def __init__(self, name):
        self.name = name
        msg = f"Non ho trovato la data '{name}' tra le giornate lavorate"
        super().__init__(msg)


class PlantNotFound(AppError):
    def __init__(self, customer, city) -> None:
        self.customer = customer
        self.city = city
        msg = f"Non ho trovato un plant di {customer} in {city} in archivio"
        super().__init__(msg)


class MultiPlantFound(AppError):
    def __init__(self, name, cities) -> None:
        self.name = name
        self.cities = cities
        msg = f"Ho trovato più città in cui {name} ha dei plant"
        super().__init__(msg)
