"""
GalaxyBot - Konfigurations-Konstanten.

Diese Datei ist eine Dünnschicht über `server_config.json`: alle Werte werden
daraus abgeleitet. Echte Anpassungen bitte über `server_config.json` oder die
`/einstellungen`-Befehle vornehmen – nicht hier im Code!

Für live anpassbare Werte in Cogs: `server_config.wert(...)` nutzen (nicht die
Konstanten hier, die nur den Stand beim Starten widerspiegeln).
"""

import os

from dotenv import load_dotenv

load_dotenv()

# Discord Bot Token (aus .env, NIEMALS direkt hier eintragen)
TOKEN = os.getenv("DISCORD_TOKEN")

import server_config as sc  # noqa: E402

# --- Team-Rollen-Hierarchie (Index 0 = höchste Rechte) ---
TEAM_ROLLEN = sc.hierarchie()

IDX_SERVERLEITUNG = 0
IDX_STELV_LEITUNG = 1
IDX_MANAGEMENT = 2
IDX_ADMINISTRATION = 3
IDX_MODERATION = 4
IDX_SUPPORT = 5
IDX_BEWERBUNGSTEAM = 6

# --- Community-/System-Rollen ---
ROLLE_ABWESEND = sc.rolle("abwesend")
ROLLE_NEUER_BUEGER = sc.rolle("neuer_buerger")
ROLLE_MITGLIED = sc.rolle("mitglied")
ROLLE_BOTS = sc.rolle("bots")

# --- Channel ---
CHANNEL_WILLKOMMEN = sc.channel("willkommen")
CHANNEL_ANKUENDIGUNGEN = sc.channel("ankuendigungen")
CHANNEL_TICKET_ERSTELLEN = sc.channel("ticket_erstellen")
CHANNEL_VORSCHLAEGE = sc.channel("vorschlaege")
CHANNEL_UMFRAGEN = sc.channel("umfragen")
CHANNEL_TEAM_ABWESENHEIT = sc.channel("team_abwesenheit")
CHANNEL_ABWESENHEITSUEBERSICHT = sc.channel("abwesenheitsuebersicht")
CHANNEL_TEAM_CHAT = sc.channel("team_chat") or "💬・team-chat"
CHANNEL_TICKET_ARCHIV = sc.channel("ticket_archiv") or sc.wert("transkripte", "channel") or ""

# --- Kategorien ---
KATEGORIE_TICKETS = sc.channel("kategorie_tickets")

# --- Log-Channels ---
CHANNEL_MOD_LOGS = sc.channel("mod_logs")
CHANNEL_MEMBER_LOGS = sc.channel("member_logs")
CHANNEL_PUNISHMENT_LOGS = sc.channel("punishment_logs")
CHANNEL_ROLE_LOGS = sc.channel("role_logs")
CHANNEL_MESSAGE_LOGS = sc.channel("message_logs")
CHANNEL_VOICE_LOGS = sc.channel("voice_logs")
CHANNEL_BOT_LOGS = sc.channel("bot_logs")
CHANNEL_ABWESENHEITS_LOGS = sc.channel("abwesenheits_logs")

# --- Farben ---
FARBE_INFO = sc.farbe("info")
FARBE_ERFOLG = sc.farbe("erfolg")
FARBE_WARNUNG = sc.farbe("warnung")
FARBE_FEHLER = sc.farbe("fehler")
FARBE_NEUTRAL = sc.farbe("neutral")

STATUS_FARBEN = {
    "🟡": sc.status_farbe("gelb"),
    "🔵": sc.status_farbe("blau"),
    "🟠": sc.status_farbe("orange"),
    "🟢": sc.status_farbe("gruen"),
    "🔴": sc.status_farbe("rot"),
    "⚫": sc.status_farbe("grau"),
    "🟣": sc.status_farbe("lila"),
}

# --- Welcome-System ---
WILLKOMMENS_TEXT = sc.wert("willkommen", "text") or ""

# --- AutoMod ---
AUTOMOD = {
    "spam_nachrichten": sc.wert("automod", "spam_nachrichten"),
    "spam_zeitfenster": sc.wert("automod", "spam_zeitfenster"),
    "spam_timeout_ab": sc.wert("automod", "spam_timeout_ab"),
    "mention_max": sc.wert("automod", "mention_max"),
    "link_blocken": sc.wert("automod", "link_blocken"),
}

# --- Team-Abwesenheit ---
ABWESENHEIT = {
    "meldepflicht_ab_tagen": sc.wert("abwesenheit", "meldepflicht_ab_tagen"),
    "erinnerung_vor_tagen": sc.wert("abwesenheit", "erinnerung_vor_tagen"),
    "min_woerter": sc.wert("abwesenheit", "min_woerter"),
    "max_woerter": sc.wert("abwesenheit", "max_woerter"),
}
