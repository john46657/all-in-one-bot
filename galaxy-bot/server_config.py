"""
Zentrale Server-Konfiguration für GalaxyBot.

Alle anpassbaren Dinge liegen in `server_config.json` und können:
  1. per Hand editiert werden (danach `/einstellungen neu_laden`)
  2. live aus Discord heraus mit `/einstellungen ...` geändert werden
  3. aus anderen Tools/Dashboards heraus geschrieben werden

Alles ist verschachtelt; unbekannte Schlüssel werden mit den Standardwerten
verschmolzen, sodass eine unvollständige JSON-Datei trotzdem funktioniert.
"""

import json
import logging
import os
import threading

log = logging.getLogger("galaxy.config")

PFAD = os.path.join(os.path.dirname(__file__), "server_config.json")
_lock = threading.Lock()
_daten: dict | None = None


def _standard() -> dict:
    """Die vollständigen Standardwerte (fallback)."""
    return {
        "version": 1,
        # --- Rollen ---
        "rollen": {
            # Team-Hierarchie von oben (höchste Rechte) nach unten.
            # Reihenfolge ist maßgeblich für alle Berechtigungen.
            "hierarchie": [
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
            ],
            "abwesend": "💤 Abwesend",
            "neuer_buerger": "🆕 Neuer Bürger",
            "mitglied": "👤 Mitglied",
            "bots": "🤖 Bots",
        },
        # --- Berechtigungen: Befehl -> mindestens erforderliche Rolle ---
        # "*" bedeutet: jedes Teammitglied (jede Rolle aus der Hierarchie).
        "berechtigungen": {
            "moderation.warn": "🔨 Moderation",
            "moderation.warnungen": "🔨 Moderation",
            "moderation.timeout": "🔨 Moderation",
            "moderation.kick": "🔧 Administration",
            "moderation.ban": "🔧 Administration",
            "ticket.panel": "👑 Serverleitung",
            "ticket.hinzufuegen": "🎫 Support",
            "ticket.transkript": "🎫 Support",
            "vorschlag.panel": "👑 Serverleitung",
            "vorschlag.bewerten": "🔧 Administration",
            "umfrage.starten": "🔨 Moderation",
            "umfrage.beenden": "🔨 Moderation",
            "abwesenheit.nutzen": "*",
            "abwesenheit.panel": "👑 Serverleitung",
            "abwesenheit.genehmigen": "🛡️ Stellvertretende Serverleitung",
            "einstellungen.verwalten": "👑 Serverleitung",
        },
        # --- Channels ---
        "channels": {
            "willkommen": "👋・willkommen",
            "ankuendigungen": "📢・ankündigungen",
            "ticket_erstellen": "🎫・ticket-erstellen",
            "vorschlaege": "💡・vorschläge",
            "umfragen": "🗳️・umfragen",
            "team_abwesenheit": "📅・team-abwesenheit",
            "abwesenheitsuebersicht": "📅・abwesenheitsübersicht",
            "kategorie_tickets": "🎫 Tickets",
            "mod_logs": "📜・mod-logs",
            "member_logs": "👤・member-logs",
            "punishment_logs": "🔨・punishment-logs",
            "role_logs": "🎭・role-logs",
            "message_logs": "💬・message-logs",
            "voice_logs": "🎙️・voice-logs",
            "bot_logs": "🤖・bot-logs",
            "abwesenheits_logs": "💤・abwesenheits-logs",
        },
        # --- Vordefinierte Ticket-Arten ---
        "tickets": [
            {"id": "support", "emoji": "🎫", "label": "Support", "farbe": "3498DB"},
            {"id": "bewerbung", "emoji": "📋", "label": "Bewerbung", "farbe": "F1C40F"},
            {"id": "spieler_meldung", "emoji": "⚠️", "label": "Spieler melden", "farbe": "E67E22"},
            {"id": "bug_meldung", "emoji": "🐛", "label": "Bug melden", "farbe": "E74C3C"},
            {"id": "vorschlag", "emoji": "💡", "label": "Vorschlag", "farbe": "2ECC71"},
            {"id": "partnerschaft", "emoji": "🤝", "label": "Partnerschaft", "farbe": "9B59B6"},
        ],
        # --- Team-Abwesenheit ---
        "abwesenheit": {
            "gruende": [
                {"label": "Urlaub", "emoji": "🌴"},
                {"label": "Schule/Ausbildung", "emoji": "🎓"},
                {"label": "Arbeit", "emoji": "💼"},
                {"label": "Private Gründe", "emoji": "🔒"},
                {"label": "Gesundheitliche Gründe", "emoji": "🤒"},
                {"label": "Technische Probleme", "emoji": "🔧"},
                {"label": "Sonstiges", "emoji": "📦"},
                {"label": "Privater Grund", "emoji": "🤫"},
            ],
            "erreichbarkeit": [
                {"id": "erreichbar", "label": "🟢 Erreichbar", "emoji": "🟢"},
                {"id": "eingeschraenkt", "label": "🟡 Eingeschränkt erreichbar", "emoji": "🟡"},
                {"id": "nicht_erreichbar", "label": "🔴 Nicht erreichbar", "emoji": "🔴"},
            ],
            "meldepflicht_ab_tagen": 3,
            "erinnerung_vor_tagen": 1,
            "min_woerter": 50,
            "max_woerter": 250,
        },
        # --- Welcome ---
        "willkommen": {
            "text": (
                "👋 Willkommen auf unserem Server!\n\n"
                "Schön, dass du da bist.\n\n"
                "Lies dir zuerst unsere Regeln und Serverinformationen durch.\n\n"
                "Danach kannst du dich in der Community beteiligen, am RP teilnehmen, "
                "eine Bewerbung einreichen oder dich mit anderen Mitgliedern austauschen.\n\n"
                "Viel Spaß!"
            ),
        },
        # --- Farben (Hex ohne #) ---
        "farben": {
            "info": "5865F2",
            "erfolg": "2ECC71",
            "warnung": "F1C40F",
            "fehler": "E74C3C",
            "neutral": "95A5A6",
            "status": {
                "gelb": "F1C40F",
                "blau": "3498DB",
                "orange": "E67E22",
                "gruen": "2ECC71",
                "rot": "E74C3C",
                "grau": "95A5A6",
                "lila": "9B59B6",
            },
        },
        # --- AutoMod ---
        "automod": {
            "spam_nachrichten": 6,
            "spam_zeitfenster": 5,
            "spam_timeout_ab": 3,
            "mention_max": 4,
            "link_blocken": True,
            "timeout_minuten": 10,
        },
        # --- Ticket-Transkripte ---
        "transkripte": {
            # Channel, in den das HTML-Transkript beim Schließen hochgeladen wird
            "channel": "🎫・ticket-archiv",
            # Web-Zugang (im Browser abrufbar). Nur aktiv, wenn web_key gesetzt!
            "web_port": 8080,
            "web_key": "",
        },
    }


def _verschmelzen(basis, ueberschreibung):
    """Tiefes Verschmelzen: Werte aus ueberschreibung gewinnen, unbekannte Schlüssel ergänzen."""
    if isinstance(basis, dict) and isinstance(ueberschreibung, dict):
        ergebnis = dict(basis)
        for schluessel, wert in ueberschreibung.items():
            if schluessel in ergebnis:
                ergebnis[schluessel] = _verschmelzen(ergebnis[schluessel], wert)
            else:
                ergebnis[schluessel] = wert
        return ergebnis
    return ueberschreibung


def neu_laden():
    """Lädt die JSON-Datei neu (verschmolzen mit den Standardwerten)."""
    global _daten
    with _lock:
        if not os.path.exists(PFAD):
            log.info("server_config.json nicht gefunden – Standardwerte werden geschrieben.")
            _daten = _standard()
            _schreibe_ohne_lock()
            return
        try:
            with open(PFAD, encoding="utf-8") as datei:
                roh = json.load(datei)
            _daten = _verschmelzen(_standard(), roh)
            log.info("server_config.json geladen.")
        except (json.JSONDecodeError, OSError) as e:
            log.error("Fehler beim Lesen von server_config.json: %s – Standardwerte genutzt.", e)
            _daten = _standard()


def _schreibe_ohne_lock():
    tmp = PFAD + ".tmp"
    with open(tmp, "w", encoding="utf-8") as datei:
        json.dump(_daten, datei, indent=2, ensure_ascii=False)
        datei.write("\n")
    os.replace(tmp, PFAD)


def speichern():
    """Schreibt die aktuelle Konfiguration in die JSON-Datei."""
    with _lock:
        if _daten is None:
            return
        _schreibe_ohne_lock()


def daten() -> dict:
    """Vollständige Konfiguration (Kopie)."""
    if _daten is None:
        neu_laden()
    return json.loads(json.dumps(_daten))


def abschnitt(name: str) -> dict:
    return daten().get(name, {})


def wert(*keys):
    """Verschachtelter Wert: wert('abwesenheit', 'min_woerter')."""
    aktuell = daten()
    for k in keys:
        if not isinstance(aktuell, dict) or k not in aktuell:
            return None
        aktuell = aktuell[k]
    return aktuell


def setze(*keys_and_value):
    """Setzt einen verschachtelten Wert und speichert.
    Beispiel: setze('abwesenheit', 'min_woerter', 60)"""
    if len(keys_and_value) < 2:
        raise ValueError("setze braucht mindestens einen Schlüssel und einen Wert.")
    keys = list(keys_and_value[:-1])
    value = keys_and_value[-1]
    with _lock:
        if _daten is None:
            neu_laden()
        aktuell = _daten
        for k in keys[:-1]:
            if k not in aktuell or not isinstance(aktuell[k], dict):
                aktuell[k] = {}
            aktuell = aktuell[k]
        aktuell[keys[-1]] = value
        _schreibe_ohne_lock()


# ---------------------------------------------------------------------------
# Komfort-Helfer (live, ohne Cache-Effekte)
# ---------------------------------------------------------------------------

def hierarchie() -> list[str]:
    return list(wert("rollen", "hierarchie") or [])


def rolle_index(rollen_name: str) -> int | None:
    try:
        return hierarchie().index(rollen_name)
    except ValueError:
        return None


def rolle_by_index(index: int) -> str:
    """Rollenname am Hierarchie-Index ('' bei ungültigem Index)."""
    h = hierarchie()
    return h[index] if 0 <= index < len(h) else ""


def mindest_rolle(befehl_key: str) -> str | None:
    return (wert("berechtigungen") or {}).get(befehl_key)


def hex_zu_int(hex_str: str | int | None, default: int = 0x5865F2) -> int:
    if hex_str is None:
        return default
    if isinstance(hex_str, int):
        return hex_str
    try:
        return int(str(hex_str).strip().lstrip("#"), 16)
    except (TypeError, ValueError):
        return default


def farbe(key: str, default: int = 0x5865F2) -> int:
    return hex_zu_int(wert("farben", key), default)


def status_farbe(name: str) -> int:
    return hex_zu_int(wert("farben", "status", name), 0xF1C40F)


def ticket_typen() -> list[dict]:
    return wert("tickets") or []


def ticket_typ(ticket_id: str) -> dict | None:
    for t in ticket_typen():
        if t["id"] == ticket_id:
            return t
    return None


def gruende() -> list[dict]:
    return wert("abwesenheit", "gruende") or []


def erreichbarkeit() -> list[dict]:
    return wert("abwesenheit", "erreichbarkeit") or []


def channel(name: str) -> str:
    return wert("channels", name) or ""


def rolle(name: str) -> str:
    return wert("rollen", name) or ""


def darf_befehl(member, befehl_key: str) -> bool:
    """Prüft, ob `member` den Befehl darf. member braucht .roles + .guild_permissions."""
    rollen_name = mindest_rolle(befehl_key)
    if rollen_name is None:
        return False
    if getattr(member.guild_permissions, "administrator", False):
        return True
    if rollen_name == "*":
        return hat_team_rolle(member)
    idx = rolle_index(rollen_name)
    if idx is None:
        return False
    return _index(member) is not None and _index(member) <= idx


def _index(member) -> int | None:
    namen = {r.name for r in member.roles}
    for i, name in enumerate(hierarchie()):
        if name in namen:
            return i
    return None


def hat_team_rolle(member) -> bool:
    return _index(member) is not None


# Beim Import einmal laden
neu_laden()
