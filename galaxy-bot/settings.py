"""
Settings-Verwaltung für GalaxyBot.

Werte werden primär aus der Datenbank (Tabelle `config`) gelesen. Ist dort nichts
gesetzt, wird der Standardwert aus config.py verwendet. So können Channel- und
Rollen-Namen angepasst werden, ohne den Code anzufassen oder den Bot neu zu
starten.
"""

import config
from database import get_config, set_config

# key -> (Anzeigename, Standardwert aus config.py)
SETTINGS = {
    # Rollen
    "rolle_abwesend": ("Abwesenheits-Rolle", config.ROLLE_ABWESEND),
    "rolle_neuer_buerger": ("Neuer-Bürger-Rolle", config.ROLLE_NEUER_BUEGER),
    "rolle_mitglied": ("Mitglied-Rolle", config.ROLLE_MITGLIED),
    "rolle_serverleitung": ("Serverleitung-Rolle", config.TEAM_ROLLEN[config.IDX_SERVERLEITUNG]),
    "rolle_support": ("Support-Rolle", config.TEAM_ROLLEN[config.IDX_SUPPORT]),
    "rolle_moderation": ("Moderation-Rolle", config.TEAM_ROLLEN[config.IDX_MODERATION]),
    "rolle_administration": ("Administration-Rolle", config.TEAM_ROLLEN[config.IDX_ADMINISTRATION]),
    # Channel
    "channel_willkommen": ("Willkommens-Channel", config.CHANNEL_WILLKOMMEN),
    "channel_ankuendigungen": ("Ankündigungs-Channel", config.CHANNEL_ANKUENDIGUNGEN),
    "channel_ticket_erstellen": ("Ticket-Erstellen-Channel", config.CHANNEL_TICKET_ERSTELLEN),
    "channel_vorschlaege": ("Vorschläge-Channel", config.CHANNEL_VORSCHLAEGE),
    "channel_umfragen": ("Umfragen-Channel", config.CHANNEL_UMFRAGEN),
    "channel_team_abwesenheit": ("Team-Abwesenheit-Channel", config.CHANNEL_TEAM_ABWESENHEIT),
    "channel_abwesenheitsuebersicht": ("Abwesenheitsübersicht-Channel", config.CHANNEL_ABWESENHEITSUEBERSICHT),
    # Logs
    "channel_mod_logs": ("Mod-Logs", config.CHANNEL_MOD_LOGS),
    "channel_member_logs": ("Member-Logs", config.CHANNEL_MEMBER_LOGS),
    "channel_punishment_logs": ("Punishment-Logs", config.CHANNEL_PUNISHMENT_LOGS),
    "channel_role_logs": ("Role-Logs", config.CHANNEL_ROLE_LOGS),
    "channel_message_logs": ("Message-Logs", config.CHANNEL_MESSAGE_LOGS),
    "channel_voice_logs": ("Voice-Logs", config.CHANNEL_VOICE_LOGS),
    "channel_bot_logs": ("Bot-Logs", config.CHANNEL_BOT_LOGS),
    "channel_abwesenheits_logs": ("Abwesenheits-Logs", config.CHANNEL_ABWESENHEITS_LOGS),
    # Kategorien
    "kategorie_tickets": ("Ticket-Kategorie", config.KATEGORIE_TICKETS),
    # AutoMod
    "automod_spam_nachrichten": ("AutoMod: max. Nachrichten im Zeitfenster", str(config.AUTOMOD["spam_nachrichten"])),
    "automod_spam_zeitfenster": ("AutoMod: Spam-Zeitfenster (Sekunden)", str(config.AUTOMOD["spam_zeitfenster"])),
    "automod_spam_timeout_ab": ("AutoMod: Spam-Verstöße bis Timeout", str(config.AUTOMOD["spam_timeout_ab"])),
    "automod_mention_max": ("AutoMod: max. Erwähnungen pro Nachricht", str(config.AUTOMOD["mention_max"])),
    "automod_link_blocken": ("AutoMod: Discord-Einladungen blocken", "1" if config.AUTOMOD["link_blocken"] else "0"),
    # Abwesenheit
    "abwesenheit_meldepflicht_ab_tagen": ("Abwesenheit: Meldepflicht ab Tagen", str(config.ABWESENHEIT["meldepflicht_ab_tagen"])),
    "abwesenheit_erinnerung_vor_tagen": ("Abwesenheit: Erinnerung X Tage vor Ende", str(config.ABWESENHEIT["erinnerung_vor_tagen"])),
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
    """Für Übersichten/Dashboards: alle Settings mit ihrem aktuell aktiven Wert."""
    return {key: {"label": label, "wert": get_setting(key)} for key, (label, _) in SETTINGS.items()}
