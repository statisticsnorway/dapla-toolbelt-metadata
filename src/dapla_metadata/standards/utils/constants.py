"""Constants used in validate ssb name standard."""

SUCCESS = "Suksess"

NAME_STANDARD_SUCSESS = "Filene dine er i samsvar med SSB-navnestandarden"

NAME_STANDARD_VIOLATION = "Det er oppdaget brudd på SSB-navnestandard:"

MISSING_BUCKET_NAME = "Filnavn mangler bøttenavn ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#obligatoriske-mapper"
MISSING_VERSION = "Filnavn mangler versjon ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#filnavn"
MISSING_PERIOD = "Filnavn mangler gyldighetsperiode ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#filnavn"
MISSING_SHORT_NAME = "Kortnavn for statistikk mangler ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#obligatoriske-mapper"
MISSING_DATA_STATE = "Mappe for datatilstand mangler ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#obligatoriske-mapper"
MISSING_DATASET_SHORT_NAME = "Filnavn mangler datasett kortnavn ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#filnavn"

INVALID_SYMBOLS = "Filnavn inneholder ulovlige tegn ref: https://manual.dapla.ssb.no/statistikkere/navnestandard.html#filnavn"

PATH_IGNORED = "Mappen er ikke underlagt krav til navnestandard"

FILE_PATH_NOT_CONFIRMED = "Det var ikke mulig å bekrefte at filstien eksisterer. Validering ble utført uten å kunne bekrefte filens eksistens."

BUCKET_NAME_UNKNOWN = "Kan ikke validere bøttenavn"

IGNORED_FOLDERS = [
    "temp",
    "oppdrag",
    "konfigurasjon",
    "logg",
    "tidsserier",
    "migrert",
]
