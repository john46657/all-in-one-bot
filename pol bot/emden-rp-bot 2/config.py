"""
Hier trägst du die Namen deiner Rollen/Channels ein, damit der Bot weiß, was er verwenden soll.
Du kannst auch Channel-IDs statt Namen nutzen (empfohlen, da Namen sich ändern können).

WICHTIG: Diese Datei einmal an deinen Server anpassen, bevor du den Bot startest.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Discord Bot Token (kommt aus der .env Datei, NIEMALS hier direkt eintragen)
TOKEN = os.getenv("DISCORD_TOKEN")

# --- Rollen-Namen (müssen exakt mit deinen Server-Rollen übereinstimmen) ---
ROLLE_LEITUNG = "Leitung"                 # darf Gefahrenstatus setzen, Ausbildungen abschließen etc.
ROLLE_AUSBILDER = "Ausbilder"
ROLLE_GSG9 = "GSG9"
ROLLE_IM_DIENST = "Im Dienst"             # wird bei Gefahrenstatus-Änderung gepingt
ROLLE_FUNKBERECHTIGT = "Funkberechtigt"   # wird automatisch bei Funk-Whitelist-Aufnahme vergeben

# Reihenfolge der Rang-Rollen für die Teamliste, von oben (höchster Rang) nach unten.
# Trage hier ALLE Ränge ein, in der Reihenfolge, wie sie in der Teamliste erscheinen sollen.
RANG_REIHENFOLGE = [
    "Leitung",
    "Stellv. Leitung",
    "Ausbilder",
    "GSG9",
    "Polizeioberkommissar",
    "Polizeikommissar",
    "Polizeimeister",
    "Anwärter",
]

# --- Channel-Namen ---
CHANNEL_BEWERBUNGEN_LOG = "bewerbungen-log"
CHANNEL_TEAMLISTE = "teamliste"
CHANNEL_BEFOERDERUNGEN = "beförderungen"
CHANNEL_ENTLASSUNGEN = "entlassungen"
CHANNEL_DIENSTBERICHTE = "dienstberichte"
CHANNEL_AUSBILDUNGSBERICHTE = "ausbildungsberichte"
CHANNEL_GSG9_LOG = "gsg9-intern"
CHANNEL_GEFAHRENSTATUS = "gefahrenstatus"
CHANNEL_FAHNDUNGEN = "fahndungen"
CHANNEL_FUNK_LOG = "funk-whitelist-log"
CHANNEL_TICKET_KATEGORIE = "Tickets"      # Name der Kategorie, in der Ticket-Channels erstellt werden

# --- Abmelden-System (Team) ---
CHANNEL_ABMELDUNGEN = "abmeldungen"       # hier postet der Bot die Abmeldungen
ROLLE_ABGMELDET = "Abgemeldet"             # wird bei Abmeldung vergeben, bei Ablauf entfernt

# --- Gefahrenstatus-Stufen (Name, Emoji, Embed-Farbe als Hex-Int) ---
GEFAHRENSTUFEN = {
    "gruen": {"label": "Grün – Normaler Dienst", "emoji": "🟢", "farbe": 0x2ecc71},
    "gelb":  {"label": "Gelb – Erhöhte Vorsicht", "emoji": "🟡", "farbe": 0xf1c40f},
    "rot":   {"label": "Rot – Akute Gefahrenlage", "emoji": "🔴", "farbe": 0xe74c3c},
}
