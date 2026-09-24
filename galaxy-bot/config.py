"""
GalaxyBot - zentrale Server-Konfiguration.

Alle Channel-/Rollen-Namen stehen hier zentral. Der Bot löst sie zur Laufzeit
auf. Namesänderungen sind möglich über:
  1. .env Variablen (Channel-/Rollen-IDs)
  2. den Settings-Override in der Datenbank (siehe settings.py)

WICHTIG: Einmal an den eigenen Server anpassen bzw. das setup/setup_server.py
Skript nutzen, das die Struktur 1:1 so anlegt.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Discord Bot Token (aus .env, NIEMALS direkt hier eintragen)
TOKEN = os.getenv("DISCORD_TOKEN")

# --- Design-Richtlinien (siehe discord-rp-server/README.md) ---
FARBE_INFO = 0x5865F2       # Blau – Standard/Info
FARBE_ERFOLG = 0x2ECC71     # Grün
FARBE_WARNUNG = 0xF1C40F    # Gelb
FARBE_FEHLER = 0xE74C3C     # Rot
FARBE_NEUTRAL = 0x95A5A6    # Grau

# Bewerbungs-/Abwesenheits-Statusfarben
STATUS_FARBEN = {
    "🟡": 0xF1C40F,   # In Prüfung / Eingereicht
    "🔵": 0x3498DB,   # Rückfrage / Verlängert
    "🟠": 0xE67E22,   # Vorstellungsgespräch
    "🟢": 0x2ECC71,   # Angenommen / Genehmigt / Aktiv
    "🔴": 0xE74C3C,   # Abgelehnt
    "⚫": 0x95A5A6,   # Zurückgezogen / Beendet
    "🟣": 0x9B59B6,   # Aktiv (Abwesenheit)
}

# ---------------------------------------------------------------------------
# Team-Rollen-Hierarchie: von oben (höchste Rechte) nach unten.
# WICHTIG: Reihenfolge muss exakt der Rollen-Anordnung im Discord-Server
# entsprechen. Der Index wird für Berechtigungs-Checks genutzt
# (Index 0 = Serverleitung = darf alles).
# ---------------------------------------------------------------------------
TEAM_ROLLEN = [
    "👑 Serverleitung",
    "🛡️ Stellvertretende Serverleitung",
    "💼 Management",
    "🔧 Administration",
    "🔨 Moderation",
    "🎫 Support",
    "📋 Bewerbungsteam",
    "🎭 Fraktionsverwaltung",
    "🎮 Event-Team",
    "📢 Social-Media-Team",
    "🎥 Content Creator",
]

# Indizes für Standard-Berechtigungen (je niedriger, desto mehr Rechte)
IDX_SERVERLEITUNG = 0
IDX_STELV_LEITUNG = 1
IDX_MANAGEMENT = 2
IDX_ADMINISTRATION = 3
IDX_MODERATION = 4
IDX_SUPPORT = 5
IDX_BEWERBUNGSTEAM = 6

# --- Community-/System-Rollen ---
ROLLE_ABWESEND = "💤 Abwesend"
ROLLE_NEUER_BUEGER = "🆕 Neuer Bürger"
ROLLE_MITGLIED = "👤 Mitglied"
ROLLE_BOTS = "🤖 Bots"

# --- Channel: START ---
CHANNEL_WILLKOMMEN = "👋・willkommen"
CHANNEL_ANKUENDIGUNGEN = "📢・ankündigungen"

# --- Channel: SUPPORT ---
CHANNEL_TICKET_ERSTELLEN = "🎫・ticket-erstellen"

# --- Channel: COMMUNITY ---
CHANNEL_VORSCHLAEGE = "💡・vorschläge"
CHANNEL_UMFRAGEN = "🗳️・umfragen"

# --- Channel: TEAM ---
CHANNEL_TEAM_ABWESENHEIT = "📅・team-abwesenheit"
CHANNEL_ABWESENHEITSUEBERSICHT = "📅・abwesenheitsübersicht"
CHANNEL_TEAM_CHAT = "💬・team-chat"

# --- Channel: LOGS ---
CHANNEL_MOD_LOGS = "📜・mod-logs"
CHANNEL_MEMBER_LOGS = "👤・member-logs"
CHANNEL_PUNISHMENT_LOGS = "🔨・punishment-logs"
CHANNEL_ROLE_LOGS = "🎭・role-logs"
CHANNEL_MESSAGE_LOGS = "💬・message-logs"
CHANNEL_VOICE_LOGS = "🎙️・voice-logs"
CHANNEL_BOT_LOGS = "🤖・bot-logs"
CHANNEL_ABWESENHEITS_LOGS = "💤・abwesenheits-logs"

# --- Kategorien ---
KATEGORIE_TICKETS = "🎫 Tickets"

# --- Welcome-System ---
WILLKOMMENS_TEXT = (
    "👋 Willkommen auf unserem Server!\n\n"
    "Schön, dass du da bist.\n\n"
    "Lies dir zuerst unsere Regeln und Serverinformationen durch.\n\n"
    "Danach kannst du dich in der Community beteiligen, am RP teilnehmen, "
    "eine Bewerbung einreichen oder dich mit anderen Mitgliedern austauschen.\n\n"
    "Viel Spaß!"
)

# --- AutoMod Standardwerte (über Settings anpassbar) ---
AUTOMOD = {
    "spam_nachrichten": 6,       # max. Nachrichten im Zeitfenster
    "spam_zeitfenster": 5,       # Zeitfenster in Sekunden
    "spam_timeout_ab": 3,        # wie oft spamden, bevor Timeout folgt
    "mention_max": 4,            # max. Erwähnungen pro Nachricht
    "link_blocken": True,        # discord.gg-Einladungen blocken
}

# --- Team-Abwesenheit ---
ABWESENHEIT = {
    "meldepflicht_ab_tagen": 3,  # ab so vielen Tagen muss gemeldet werden
    "erinnerung_vor_tagen": 1,   # Erinnerung X Tage vor Ende
}
