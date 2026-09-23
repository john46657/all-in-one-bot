"""
Zentrale Settings-Verwaltung.

Werte werden primär aus der Datenbank (Tabelle `config`) gelesen. Ist dort nichts
gesetzt, wird der Standardwert aus config.py verwendet. So kann das Web-Dashboard
Channel-/Rollennamen ändern, ohne dass der Bot-Code angepasst oder neu gestartet
werden muss.

WICHTIG: Sowohl der Bot als auch das Dashboard importieren diese Datei und nutzen
dieselbe SQLite-Datenbank (data/bot.db).
"""

import config
from database import get_config, set_config

# key -> (Anzeigename fürs Dashboard, Standardwert aus config.py, Typ)
SETTINGS = {
    "channel_bewerbungen_log": ("Bewerbungen Log-Channel", config.CHANNEL_BEWERBUNGEN_LOG),
    "channel_teamliste": ("Teamliste-Channel", config.CHANNEL_TEAMLISTE),
    "channel_befoerderungen": ("Beförderungen-Channel", config.CHANNEL_BEFOERDERUNGEN),
    "channel_entlassungen": ("Entlassungen-Channel", config.CHANNEL_ENTLASSUNGEN),
    "channel_dienstberichte": ("Dienstberichte-Channel", config.CHANNEL_DIENSTBERICHTE),
    "channel_ausbildungsberichte": ("Ausbildungsberichte-Channel", config.CHANNEL_AUSBILDUNGSBERICHTE),
    "channel_gsg9_log": ("GSG9 Intern-Channel", config.CHANNEL_GSG9_LOG),
    "channel_gefahrenstatus": ("Gefahrenstatus-Channel", config.CHANNEL_GEFAHRENSTATUS),
    "channel_fahndungen": ("Fahndungen-Channel", config.CHANNEL_FAHNDUNGEN),
    "channel_funk_log": ("Funk-Whitelist Log-Channel", config.CHANNEL_FUNK_LOG),
    "channel_ticket_kategorie": ("Ticket-Kategorie", config.CHANNEL_TICKET_KATEGORIE),
    "channel_abmeldungen": ("Abmeldungen-Channel", config.CHANNEL_ABMELDUNGEN),
    "rolle_abgemeldet": ("Abgemeldet-Rolle", config.ROLLE_ABGMELDET),
    "rolle_leitung": ("Leitungs-Rolle", config.ROLLE_LEITUNG),
    "rolle_ausbilder": ("Ausbilder-Rolle", config.ROLLE_AUSBILDER),
    "rolle_gsg9": ("GSG9-Rolle", config.ROLLE_GSG9),
    "rolle_im_dienst": ("Im-Dienst-Rolle", config.ROLLE_IM_DIENST),
    "rolle_funkberechtigt": ("Funkberechtigt-Rolle", config.ROLLE_FUNKBERECHTIGT),
}


def get_setting(key: str) -> str:
    """Liefert den aktuell aktiven Wert (DB-Override falls vorhanden, sonst config.py-Standard)."""
    if key not in SETTINGS:
        raise KeyError(f"Unbekannter Settings-Key: {key}")
    _, standard = SETTINGS[key]
    return get_config(key, standard)


def set_setting(key: str, value: str):
    if key not in SETTINGS:
        raise KeyError(f"Unbekannter Settings-Key: {key}")
    set_config(key, value)


def alle_settings() -> dict:
    """Für das Dashboard: alle Settings mit ihrem aktuell aktiven Wert."""
    return {key: {"label": label, "wert": get_setting(key)} for key, (label, _) in SETTINGS.items()}
