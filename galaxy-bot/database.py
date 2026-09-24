"""
Zentrale Datenbank-Verwaltung für GalaxyBot.
SQLite - reicht für einen Discord-Server komplett aus, kein externer Server nötig.
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "galaxy.db")


def get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Foreign Keys aktivieren (SQLite macht das nicht standardmäßig)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Erstellt alle Tabellen, falls sie noch nicht existieren. Wird beim Start aufgerufen."""
    conn = get_connection()
    cur = conn.cursor()

    # Allgemeine Config (Channel-IDs, Panel-Message-IDs, Overrides, ...)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # --- Moderation: Verwarnungen ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS warnungen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            moderator_id INTEGER NOT NULL,
            grund TEXT NOT NULL,
            erstellt_am TEXT NOT NULL
        )
    """)

    # --- Moderation: Aktionen (timeout / kick / ban) ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS moderation_aktionen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            typ TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            moderator_id INTEGER NOT NULL,
            grund TEXT,
            dauer TEXT,
            erstellt_am TEXT NOT NULL
        )
    """)

    # --- AutoMod: Verstöße pro User (für Eskalation) ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS automod_verstoesse (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            typ TEXT NOT NULL,
            channel_id INTEGER,
            erstellt_am TEXT NOT NULL
        )
    """)

    # --- Tickets ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL UNIQUE,
            user_id INTEGER NOT NULL,
            channel_id INTEGER,
            typ TEXT NOT NULL,
            status TEXT DEFAULT 'offen',
            erstellt_am TEXT NOT NULL,
            geschlossen_am TEXT
        )
    """)

    # --- Vorschläge ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vorschlaege (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message_id INTEGER,
            channel_id INTEGER,
            titel TEXT NOT NULL,
            beschreibung TEXT,
            status TEXT DEFAULT 'offen',
            erstellt_am TEXT NOT NULL
        )
    """)

    # --- Umfragen ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS umfragen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            umfrage_id TEXT NOT NULL UNIQUE,
            user_id INTEGER NOT NULL,
            message_id INTEGER,
            channel_id INTEGER,
            frage TEXT NOT NULL,
            optionen TEXT NOT NULL,          -- JSON: [{"label": "..", "emoji": ".."}]
            ergebnisse TEXT NOT NULL,         -- JSON: {option_index: anzahl}
            ablauf TEXT,                      -- ISO datetime
            aktiv INTEGER DEFAULT 1,
            thread_id INTEGER,
            erstellt_am TEXT NOT NULL
        )
    """)

    # --- Umfragen: abgegebene Stimmen (Double-Voting verhindern) ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS umfragen_stimmen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            umfrage_id TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            option_index INTEGER NOT NULL,
            abgegeben_am TEXT NOT NULL,
            UNIQUE (umfrage_id, user_id)
        )
    """)

    # --- Team-Abwesenheit: Rollen, die das System nutzen dürfen ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS abwesenheit_rollen (
            rolle_id INTEGER PRIMARY KEY
        )
    """)

    # --- Team-Abwesenheit: laufende & vergangene Abmeldungen ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS abwesenheiten (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            abwesenheit_id TEXT NOT NULL UNIQUE,        -- z. B. ABW-0001
            user_id INTEGER NOT NULL,
            team_rolle TEXT,
            typ TEXT DEFAULT 'normal',                  -- normal | kurzfristig
            von_datum TEXT NOT NULL,
            bis_datum TEXT,
            dauer TEXT,                                 -- nur bei kurzfristig
            rueckkehr_datum TEXT,
            grund TEXT,
            erreichbarkeit TEXT,
            uebergabe_erforderlich INTEGER DEFAULT 0,
            uebergabe_text TEXT,
            vertretung_id INTEGER,
            vertretung_text TEXT,
            status TEXT NOT NULL DEFAULT 'eingereicht',
            -- eingereicht | genehmigt | abgelehnt | verlaengert | aktiv | beendet
            erstellt_am TEXT NOT NULL,
            genehmigt_von INTEGER,
            genehmigt_am TEXT,
            beendet_am TEXT,
            erinnert INTEGER DEFAULT 0,
            panel_message_id INTEGER,
            panel_channel_id INTEGER
        )
    """)

    # --- Team-Abwesenheit: Verlängerungs-Anträge (müssen bestätigt werden) ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS abwesenheit_verlaengerungen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            abwesenheit_id TEXT NOT NULL,
            neues_enddatum TEXT NOT NULL,
            hinweis TEXT,
            status TEXT DEFAULT 'eingereicht',          -- eingereicht | genehmigt | abgelehnt
            erstellt_am TEXT NOT NULL,
            entschieden_am TEXT
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
