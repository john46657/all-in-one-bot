# Emden RP Bot

Ein modularer Discord-Bot für den Emden Polizei-Roleplay-Server. Läuft komplett
eigenständig innerhalb von Discord, ohne API- oder Webhook-Verbindung zu Roblox.

## Funktionen

- 📋 **Bewerbungssystem** – `/bewerbung`
- 👥 **Teamliste** – automatisch aktualisierte Nachricht, Rangreihenfolge aus Discord-Rollen
- 🎉 **Beförderungs-/Entlassungs-Nachrichten** – automatisch bei Rollenänderungen, zusätzlich `/entlassen_roblox` per Roblox-Namen (falls die Person nicht mehr im Discord ist, z.B. nach einem Bann)
- 🔗 **Roblox-Verknüpfung** – `/roblox verknuepfen`, `/roblox info`, `/roblox suchen`
- 🕐 **Dienstzeiten-Tracking** – `/dienst start`, `/dienst ende`, `/dienst stunden`
- 📝 **Dienstberichte** – `/dienstbericht`, `/dienstberichte`
- 🎓 **Ausbildungssystem** – `/ausbildung zuweisen`, `/ausbildung modul`, `/ausbildung fortschritt`, `/ausbildung bericht`, `/ausbildung abschliessen`
- 🎯 **GSG9-Modul** – `/gsg9 bewerbung`, `/gsg9 einsatzbericht`, `/gsg9 liste`
- 🚦 **Gefahrenstatus-Panel** – Button-Panel (Grün/Gelb/Rot), `/gefahrenstatus_panel` zum Posten
- 🚔 **Fahndungssystem** – `/fahndung erstellen`, `/fahndung beenden`, `/fahndung liste`
- 📻 **Funk-Whitelist** – `/funk whitelist hinzufuegen`, `entfernen`, `entfernen_roblox`, `liste`, `check` (vergibt automatisch die Rolle "Funkberechtigt")
- 🎫 **Ticket-System** – Button-Panel, `/ticket_panel` zum Posten
- 🚪 **Abmelden-System (Team)** – `/abmelden jetzt` (Modal), `/abmelden setup` (mehrere berechtigte Rollen per Select-Menü oder Rollen-ID), automatische Rollen-Verwaltung bei Ablauf

## Einrichtung

### 1. Bot im Discord Developer Portal erstellen

1. Gehe zu https://discord.com/developers/applications und erstelle eine neue Application
2. Unter **Bot** → **Reset Token** → Token kopieren (brauchst du gleich)
3. Unter **Bot** → **Privileged Gateway Intents**: **SERVER MEMBERS INTENT** aktivieren
   (wird für Teamliste und Beförderungs-/Entlassungserkennung benötigt)
4. Unter **OAuth2 → URL Generator**: Scopes `bot` und `applications.commands` auswählen,
   bei Bot Permissions mindestens: `Manage Roles`, `Manage Channels`, `Send Messages`,
   `Manage Messages`, `Embed Links`, `Read Message History`
5. Die generierte URL öffnen und den Bot auf deinen Server einladen

### 2. Server vorbereiten

Lege folgende **Channels** an (Namen müssen zu `config.py` passen, oder passe die Namen dort an):
- `bewerbungen-log`
- `teamliste`
- `beförderungen`
- `entlassungen`
- `dienstberichte`
- `ausbildungsberichte`
- `gsg9-intern`
- `gefahrenstatus`
- `fahndungen`
- `funk-whitelist-log`
- `abmeldungen`
- Kategorie `Tickets`

Lege außerdem die **Rollen** an, die in `config.py` unter `RANG_REIHENFOLGE`, `ROLLE_LEITUNG`,
`ROLLE_AUSBILDER`, `ROLLE_GSG9`, `ROLLE_IM_DIENST`, `ROLLE_FUNKBERECHTIGT` und
`ROLLE_ABGMELDET` eingetragen sind
(oder passe die Namen in `config.py` an deine bestehenden Rollen an).

**Wichtig:** Die Bot-Rolle muss in der Rollen-Reihenfolge **über** allen Rang-Rollen stehen,
damit er sie automatisch erkennen und die Teamliste korrekt aufbauen kann.

### 3. Lokal einrichten

```bash
# Abhängigkeiten installieren
pip install -r requirements.txt

# .env Datei anlegen (Token eintragen)
cp .env.example .env
# .env öffnen und DISCORD_TOKEN=... eintragen

# Bot starten
python bot.py
```

### 4. Nach dem Start

- `/gefahrenstatus_panel` einmal in `#gefahrenstatus` ausführen, um das Button-Panel zu posten
- `/ticket_panel` einmal im gewünschten Support-Channel ausführen
- `/teamliste_aktualisieren` einmal manuell ausführen (danach läuft es automatisch)
- `/abmelden setup` einmal ausführen und die Rollen auswählen, die sich abmelden dürfen
  (mehrere möglich; alternativ `/abmelden rolle_hinzufuegen rolle_id:<ID>`)

**Wichtig fürs Abmelden-System:** Die Bot-Rolle muss in der Rollen-Reihenfolge **über**
der Rolle "Abgemeldet" stehen, sonst kann der Bot sie nicht automatisch vergeben/entfernen.

**Wichtig für Funk-Whitelist & Entlassungen per Roblox-Name:** Damit `/funk whitelist entfernen_roblox`
und `/entlassen_roblox` funktionieren, muss die Person vorher einmal mit `/roblox verknuepfen`
mit ihrem Roblox-Namen verknüpft worden sein (am besten direkt bei Bewerbungsannahme oder
Diensteintritt machen). Ohne Verknüpfung kennt der Bot keinen Zusammenhang zwischen Roblox-Namen
und Discord-Account.

## Web-Dashboard (getrennt vom Bot gehostet, z.B. Bot bei bot-hosting.net + Dashboard bei Cybrancee)

Das Dashboard ist eine eigenständige Flask-Anwendung im `dashboard/`-Ordner. Sie braucht
**keinen** Zugriff auf die Bot-Datenbank direkt – stattdessen läuft im Bot eine kleine,
per API-Key abgesicherte Web-Schnittstelle mit, die das Dashboard über das Internet
abfragt. So können Bot und Dashboard auf zwei völlig unterschiedlichen Servern laufen.

```
┌─────────────────────┐        HTTPS + API-Key        ┌──────────────────────┐
│  Bot (bot-hosting.net) │ <───────────────────────────  │ Dashboard (Cybrancee) │
│  - Discord-Bot          │                              │  - Flask-Webseite     │
│  - SQLite-Datenbank     │                              │  - Discord-Login      │
│  - eingebaute API :8080 │  ─────────────────────────>  │  - ruft Bot-API auf   │
└─────────────────────┘        Daten & Einstellungen     └──────────────────────┘
```

### Schritt 1: Bot bei bot-hosting.net einrichten

1. Server anlegen, Sprache **Python** auswählen
2. Alle Dateien AUSSER dem `dashboard/`-Ordner hochladen (der Bot braucht ihn nicht),
   oder das komplette Projekt hochladen - schadet auch nicht
3. `requirements.txt` wird automatisch erkannt und installiert (steht so im
   bot-hosting.net-Wiki), alternativ im Tab "Startup" unter "Additional Python
   packages" manuell nachtragen
4. In den Umgebungsvariablen/`.env` auf dem Server setzen (siehe `.env.example`):
   - `DISCORD_TOKEN`
   - `API_KEY` (frei erfundener, langer geheimer Schlüssel - merken, brauchst du gleich nochmal)
   - `API_PORT` (Standard 8080, nur ändern falls bot-hosting.net einen anderen Port vorschreibt)
5. **Wichtig:** Schau im bot-hosting.net-Kontrollpanel nach, ob/wie dein Server einen
   öffentlich erreichbaren Port oder eine Domain bekommt (oft unter "Ports" oder
   "Networking" im Panel). Diese Adresse brauchst du für `BOT_API_URL` im nächsten Schritt.
   Manche kostenlosen Bot-Hoster blockieren eingehende Web-Verbindungen zu benutzerdefinierten
   Ports - falls das bei euch der Fall ist, meld dich nochmal, dann bauen wir eine Alternative
   (z.B. über einen Tunnel-Dienst).
6. Bot starten

### Schritt 2: Dashboard bei Cybrancee einrichten

1. In eurem Cybrancee Web-Hosting-Paket eine Python/Node-fähige Anwendung anlegen
   (im Cybrancee-Panel meist unter "Setup App" o.ä. - je nach Paneltyp cPanel oder eigenes Panel)
2. Nur den Inhalt des `dashboard/`-Ordners hochladen
3. `dashboard/requirements.txt` installieren lassen (`pip install -r requirements.txt`)
4. `.env` im `dashboard/`-Ordner anlegen (Vorlage: `dashboard/.env.example`):
   - `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET` (aus dem Developer Portal, siehe unten)
   - `DISCORD_REDIRECT_URI` = `https://eure-cybrancee-domain.de/callback`
   - `DISCORD_GUILD_ID`
   - `DASHBOARD_SECRET_KEY` (beliebiger langer Zufallsstring)
   - `DISCORD_TOKEN` (derselbe Bot-Token wie beim Bot)
   - `BOT_API_URL` = die Adresse aus Schritt 1.5, z.B. `http://eure-bot-hosting-domain:8080`
   - `BOT_API_KEY` = **exakt derselbe Wert** wie `API_KEY` beim Bot
5. Startdatei ist `app.py` (Cybrancee fragt meist nach dem "Entry Point"/"Startdatei")

### Schritt 3: Discord Developer Portal

1. Dieselbe Application wie der Bot öffnen → **OAuth2**
2. Client Secret erstellen (falls noch nicht vorhanden) → kommt in die Dashboard-`.env`
3. Unter **Redirects**: `https://eure-cybrancee-domain.de/callback` eintragen
   (muss exakt mit `DISCORD_REDIRECT_URI` übereinstimmen, inkl. https/http)

### Schritt 4: Testen

1. Bot starten (bot-hosting.net) → in den Logs sollte "API-Server läuft auf Port 8080" stehen
2. Dashboard starten (Cybrancee) → im Browser die Cybrancee-Domain öffnen
3. Mit Discord einloggen → falls "Zugriff verweigert" oder "Bot-Server nicht erreichbar"
   kommt, prüfe zuerst `BOT_API_URL`/`BOT_API_KEY` auf Tippfehler, danach ob der Port
   beim Bot-Hoster wirklich von außen erreichbar ist

**Kurzfassung der Verbindung:** Bot und Dashboard reden nur über `BOT_API_URL` +
`API_KEY`/`BOT_API_KEY` miteinander. Diese beiden Werte müssen auf beiden Seiten
zusammenpassen - das ist der einzige "Klebstoff" zwischen den zwei Servern.



Für dauerhaften Betrieb brauchst du einen Ort, an dem `python bot.py` durchgehend läuft:
- Ein günstiger **VPS** (z.B. bei Hetzner, Contabo)
- **Railway** oder **Render** (haben kostenlose/günstige Tarife für kleine Bots)
- Ein **Raspberry Pi** zuhause, wenn er durchgehend läuft

Ein normaler Windows-PC, der ausgeschaltet wird, reicht nicht – der Bot muss die ganze
Zeit laufen, damit z.B. die automatische Teamliste und das Gefahrenstatus-Panel reagieren.

## Datenbank

Alle Daten (Dienstzeiten, Berichte, Fahndungen, etc.) werden in `data/bot.db` (SQLite)
gespeichert. Diese Datei regelmäßig sichern (z.B. per Cronjob kopieren), falls der Server
mal neu aufgesetzt werden muss.

## Struktur

```
emden-rp-bot/
├── bot.py                  # Haupt-Einstiegspunkt
├── api_server.py            # Eingebaute API fürs Dashboard
├── config.py                # Rollen-/Channel-Namen, Gefahrenstufen (Standardwerte)
├── settings.py               # Liest/schreibt Settings-Overrides aus der DB
├── checks.py                  # Dynamischer Rollen-Check für Slash-Commands
├── database.py               # SQLite-Datenbank-Setup
├── requirements.txt
├── .env.example
├── cogs/
│   ├── bewerbungen.py
│   ├── roblox.py
│   ├── teamliste.py
│   ├── dienst.py
│   ├── dienstberichte.py
│   ├── ausbildung.py
│   ├── gsg9.py
│   ├── gefahrenstatus.py
│   ├── fahndung.py
│   ├── funk.py
│   └── tickets.py
└── dashboard/                  # Komplett eigenständig deploybar (z.B. auf Cybrancee)
    ├── app.py                    # Flask-Hauptanwendung
    ├── dashboard_config.py       # Liest die .env im dashboard/-Ordner
    ├── discord_oauth.py          # Login-Logik
    ├── requirements.txt           # Eigene, schlanke Abhängigkeiten
    ├── .env.example
    └── templates/                 # HTML-Seiten
```

## Nächste Schritte / Erweiterungsideen

- Rechte-Checks feiner abstimmen (aktuell teils `manage_roles`/`administrator`, teils Rollen-Namen)
- Eigene Slash-Command-Berechtigungen direkt in Discord setzen (Server-Einstellungen → Integrationen)
- Backup-Automatisierung für `data/bot.db`
