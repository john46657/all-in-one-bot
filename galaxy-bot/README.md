# 🌌 GalaxyBot – zentraler Server-Bot

GalaxyBot ist der zentrale Allround-Bot der RP-/Community-Plattform.
Er übernimmt **übergreifende** Systeme – Bewerbungen (Appy) und Economy
(UnbelievaBoat) gehören bewusst **nicht** zu seinem Aufgabengebiet
(Master-Prompt §1: keine Überschneidungen).

## 🧩 Module (Cogs)

| Cog | Funktion |
|---|---|
| `cogs/welcome.py` | Willkommensnachricht + Rolle 🆕 Neuer Bürger + Member-Logs |
| `cogs/moderation.py` | `/warn`, `/warnungen`, `/timeout`, `/kick`, `/ban` |
| `cogs/automod.py` | Spam-, Mention-Spam- und Link-Schutz mit Auto-Timeout |
| `cogs/tickets.py` | 6 Ticketarten, private Channel, Schließen-Button |
| `cogs/suggestions.py` | Vorschlags-Panel + Umfragen mit Auswertung |
| `cogs/absence.py` | Team-Abwesenheit: Anträge, Freigabe, Verlängerung, Übersicht |
| `cogs/logs.py` | Member-, Rollen-, Nachrichten- und Voice-Logs |

## 🚀 Einrichtung

1. **Serverstruktur anlegen** (empfohlen):
   ```bash
   cd ../setup
   python setup_server.py --guild-id <DEINE_SERVER_ID> --dry-run   # Plan prüfen
   python setup_server.py --guild-id <DEINE_SERVER_ID>             # anlegen
   ```
   Das Skript erstellt alle Rollen, Kategorien und Channels inkl. Berechtigungen.

2. **Bot im Developer Portal** erstellen:
   - Privileged Gateway Intents: **Server Members** + **Message Content** aktivieren
   - Scopes `bot` + `applications.commands`
   - Rechte mindestens: `Manage Roles`, `Manage Channels`, `Moderate Members`,
     `Kick Members`, `Ban Members`, `Send Messages`, `Manage Messages`,
     `Embed Links`, `Read Message History`, `View Audit Log`

3. **Bot-Rolle** `🤖 Bots` **über** allen Rollen platzieren, die der Bot verwalten
   soll (besonders `💤 Abwesend`), sonst schlagen Rollenänderungen fehl.

4. **Lokal starten**:
   ```bash
   pip install -r requirements.txt
   cp .env.example .env       # DISCORD_TOKEN eintragen
   python bot.py
   ```

5. **Panels einmal posten**:
   - `/ticket panel` in `🎫・ticket-erstellen`
   - `/vorschlag panel` in `💡・vorschläge`
   - `/abwesenheit panel` in `📅・team-abwesenheit`

## 📋 Befehle

| Befehl | Berechtigung | Wirkung |
|---|---|---|
| `/moderation warn` | ab 🔨 Moderation | Verwarnung |
| `/moderation warnungen` | ab 🔨 Moderation | Verwarnungen anzeigen |
| `/moderation timeout` | ab 🔨 Moderation | Timeout (`10m`, `1h`, `2h30m`, `1d`) |
| `/moderation kick` | ab 🔧 Administration | Kick |
| `/moderation ban` | ab 🔧 Administration | Ban |
| `/ticket panel` | Administrator | Ticket-Panel posten |
| `/ticket hinzufuegen` | ab 🎫 Support | Nutzer zum Ticket hinzufügen |
| `/vorschlag panel` | Administrator | Vorschlags-Panel posten |
| `/umfrage` | ab 🔨 Moderation | Umfrage mit bis zu 8 Optionen |
| `/abwesenheit panel` | Administrator | Abwesenheits-Panel posten |
| `/abwesenheit übersicht` | Team | Abwesenheitsübersicht aktualisieren |

Berechtigungen werden über die **Team-Hierarchie** geprüft
(`config.TEAM_ROLLEN`, Index 0 = Serverleitung).

## 💤 Team-Abwesenheit

Vollständiges System nach Master-Prompt §§14–25:

- 5 Buttons: melden / meine / verlängern / Rückkehr / kurzfristig
- Status: 🟡 Eingereicht → 🟢 Genehmigt / 🔴 Abgelehnt → 🟣 Aktiv → ⚫ Beendet
- Freigabe nur durch Serverleitung; Verlängerungen müssen bestätigt werden
- Automatische Aktivierung zum Start, Erinnerung vor Ende, Auto-Beendigung
- Rolle `💤 Abwesend` wird automatisch vergeben/entfernt
- Aufgabenübergabe: **50–250 Wörter** (wie alle Freitextfelder der Bewerbungen)
- Übersicht in `📅・abwesenheitsübersicht`, Logs in `💤・abwesenheits-logs`
- Datensparsam: „Privater Grund“ wird immer akzeptiert

## 🧪 Testen

### Logik-Tests (ohne Discord)
```bash
python tests/test_logik.py
```
Prüft Wortgrenzen (49/50/250/251), Datum- und Dauer-Parser,
Team-Hierarchie und Status-Farben.

### Interaktives Test-Dashboard (Browser)
`dashboard.html` im Browser öffnen – offline, ohne Discord. Simuliert:
- Bewerbungen mit Grenzwert-Tests (49/50/250/251 Wörter) + Status-Übergänge
- kompletten Abwesenheits-Workflow inkl. Verlängerung und Rückkehr
- Tickets, Moderation, Economy, AutoMod, Logs
- Fortschrittsanzeige für den Gesamttest (Master-Prompt §34)

Alle Daten bleiben im Browser (localStorage).

## ⚙️ Konfiguration

Alle Channel-/Rollen-Namen, Farben, AutoMod-Grenzen, Abwesenheits-Regeln und
Berechtigungen liegen in `server_config.json`. Ändern kann man sie:

1. per Hand in der Datei (danach `/einstellungen neu_laden`)
2. live aus Discord heraus mit `/einstellungen ...` (Channel, Rolle,
   Berechtigung, AutoMod, Abwesenheit, Willkommenstext) – greift sofort,
   ohne Neustart

`config.py` ist nur eine Dünnschicht darauf; im Code bitte `server_config`
nutzen.

## 🗂️ Struktur

```
galaxy-bot/
├── bot.py                  # Einstiegspunkt
├── config.py               # Dünnschicht über server_config.json
├── server_config.py        # Lese/Schreib-Zugriff auf server_config.json
├── server_config.json      # gesamte Server-Konfiguration (live anpassbar)
├── database.py             # SQLite (data/galaxy.db)
├── checks.py               # Team-Hierarchie / Berechtigungen
├── logging_utils.py        # Zentrale Log-Helfer
├── dashboard.html          # Offline-Test-Dashboard (Browser)
├── requirements.txt
├── tests/test_logik.py     # Logik-Tests
└── cogs/                   # 8 Module (siehe oben)
```
