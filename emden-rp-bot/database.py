"""
Zentrale Datenbank-Verwaltung für den Emden RP Bot.
Nutzt SQLite - reicht für einen RP-Server locker aus und braucht keinen extra Server.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "bot.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Erstellt alle Tabellen, falls sie noch nicht existieren. Wird einmal beim Start aufgerufen."""
    conn = get_connection()
    cur = conn.cursor()

    # Dienstzeiten: laufende und abgeschlossene Schichten
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dienstzeiten (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            start_zeit TEXT NOT NULL,
            ende_zeit TEXT,
            dauer_sekunden INTEGER,
            unit TEXT DEFAULT 'polizei'
        )
    """)

    # Dienstberichte
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dienstberichte (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            datum TEXT NOT NULL,
            dauer TEXT,
            taetigkeiten TEXT,
            besonderheiten TEXT,
            erstellt_am TEXT NOT NULL
        )
    """)

    # Ausbildung: Zuordnung Rekrut -> Ausbilder
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ausbildung (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rekrut_id INTEGER NOT NULL UNIQUE,
            ausbilder_id INTEGER NOT NULL,
            start_datum TEXT NOT NULL,
            abgeschlossen INTEGER DEFAULT 0
        )
    """)

    # Ausbildungsmodule (Checkliste pro Rekrut)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ausbildung_module (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rekrut_id INTEGER NOT NULL,
            modul_name TEXT NOT NULL,
            bestanden INTEGER DEFAULT 0,
            abgenommen_von INTEGER,
            datum TEXT
        )
    """)

    # Ausbildungs-/Prüfungsberichte
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ausbildungsberichte (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rekrut_id INTEGER NOT NULL,
            ausbilder_id INTEGER NOT NULL,
            datum TEXT NOT NULL,
            dauer TEXT,
            themen TEXT,
            bewertung TEXT,
            bestanden INTEGER,
            erstellt_am TEXT NOT NULL
        )
    """)

    # GSG9 Mitglieder (separates Roster)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS gsg9_mitglieder (
            user_id INTEGER PRIMARY KEY,
            rang TEXT,
            beigetreten_am TEXT NOT NULL
        )
    """)

    # GSG9 Einsatzberichte
    cur.execute("""
        CREATE TABLE IF NOT EXISTS gsg9_einsatzberichte (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            datum TEXT NOT NULL,
            einsatzart TEXT,
            beschreibung TEXT,
            erstellt_am TEXT NOT NULL
        )
    """)

    # Gefahrenstatus (aktueller Status + Verlauf)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS gefahrenstatus_verlauf (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT NOT NULL,
            grund TEXT,
            gesetzt_von INTEGER NOT NULL,
            gesetzt_am TEXT NOT NULL
        )
    """)

    # Fahndungen
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fahndungen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            grund TEXT,
            beschreibung TEXT,
            dringlichkeit TEXT DEFAULT 'normal',
            erstellt_von INTEGER NOT NULL,
            erstellt_am TEXT NOT NULL,
            aktiv INTEGER DEFAULT 1,
            message_id INTEGER,
            channel_id INTEGER
        )
    """)

    # Roblox-Verknüpfung: welcher Discord-User gehört zu welchem Roblox-Namen
    # (wichtig, damit man jemanden auch nach einem Bann/Verlassen des Servers noch zuordnen kann)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS roblox_verknuepfungen (
            user_id INTEGER PRIMARY KEY,
            roblox_name TEXT NOT NULL,
            letzter_discord_name TEXT,
            verknuepft_von INTEGER NOT NULL,
            verknuepft_am TEXT NOT NULL
        )
    """)

    # Funk-Whitelist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS funk_whitelist (
            user_id INTEGER PRIMARY KEY,
            hinzugefuegt_von INTEGER NOT NULL,
            hinzugefuegt_am TEXT NOT NULL
        )
    """)

    # Abmelden-System: welche Rollen dürfen sich abmelden?
    cur.execute("""
        CREATE TABLE IF NOT EXISTS abmelden_rollen (
            rolle_id INTEGER PRIMARY KEY
        )
    """)

    # Abmelden-System: laufende und vergangene Team-Abmeldungen
    cur.execute("""
        CREATE TABLE IF NOT EXISTS abmeldungen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            von_datum TEXT NOT NULL,
            bis_datum TEXT NOT NULL,
            grund TEXT,
            vertretung TEXT,
            erstellt_am TEXT NOT NULL,
            beendet_am TEXT,
            aktiv INTEGER DEFAULT 1,
            message_id INTEGER,
            channel_id INTEGER
        )
    """)

    # Konfiguration (Channel-IDs, Panel-Message-IDs etc. - damit man nicht alles in Code hardcoden muss)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    conn.commit()
    conn.close()


def get_config(key: str, default=None):
    conn = get_connection()
    row = conn.execute("SELECT value FROM config WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_config(key: str, value: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO config (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, str(value)),
    )
    conn.commit()
    conn.close()
