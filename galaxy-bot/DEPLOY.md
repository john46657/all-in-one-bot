# 🚀 GalaxyBot deployen (Hosting)

Anleitung für dauerhaften 24/7-Betrieb, z. B. auf **bot-hosting.net**
(andere Python-Hoster funktionieren analog).

---

## 1. Voraussetzungen im Discord Developer Portal

1. Application öffnen → **Bot**
2. **Privileged Gateway Intents** aktivieren:
   - ✅ **SERVER MEMBERS INTENT** (zwingend für Welcome/Logs/Teamliste)
   - ✅ **MESSAGE CONTENT INTENT** (zwingend für AutoMod)
3. **OAuth2 → URL Generator**: Scopes `bot` + `applications.commands`
4. Bot Permissions auswählen:
   `Manage Roles`, `Manage Channels`, `Moderate Members`, `Kick Members`,
   `Ban Members`, `Send Messages`, `Manage Messages`, `Embed Links`,
   `Read Message History`, `View Audit Log`
5. URL öffnen → Bot auf den Server einladen

> ⚠️ Ohne die beiden Intents startet der Bot nicht (Fehler
> `PrivilegedIntentsRequired`). Das ist die häufigste Fehlerursache.

---

## 2. Server vorbereiten (einmalig)

Am einfachsten mit dem Setup-Skript (auf deinem Rechner ausführen, einmalig):
```bash
cd setup
python setup_server.py --guild-id <SERVER_ID> --dry-run   # Plan prüfen
python setup_server.py --guild-id <SERVER_ID>             # anlegen
```
Legt alle 23 Rollen, 16 Kategorien und Channels inkl. Berechtigungen an.
Danach den Bot in den Server einladen (Schritt 1) – die Rollen/Channels
existieren dann schon.

---

## 3. Bei bot-hosting.net hochladen

1. Server anlegen, Sprache **Python** wählen
2. Den **Inhalt des `galaxy-bot/`-Ordners** hochladen – **ohne** den Ordner
   `venv/` (wird vom Hoster automatisch über `requirements.txt` installiert)
3. Unter **Umgebungsvariablen** (oder `.env`):
   - `DISCORD_TOKEN` = dein Bot-Token
   - optional `SSL_CERT_FILE` = Pfad zu `certifi` (nur bei SSL-Fehlern nötig;
     Linux-Hoster haben das meist korrekt konfiguriert)
4. Startdatei / Entry Point: **`bot.py`** (Startkommando `python bot.py`)
5. Server starten

In den Logs sollten nacheinander erscheinen:
```
Cog geladen: cogs.welcome        … cogs.logs
5 Slash-Commands synchronisiert.
Eingeloggt als GalaxyBot#XXXX (ID: ...)
GalaxyBot ist bereit. Verbunden mit 1 Server(n).
```

---

## 4. Nach dem ersten Start (einmalig)

Diese Befehle **einmal** ausführen, um die Panels zu posten:

| Befehl | Channel |
|---|---|
| `/ticket panel` | 🎫・ticket-erstellen |
| `/vorschlag panel` | 💡・vorschläge |
| `/abwesenheit panel` | 📅・team-abwesenheit |

Danach sind alle Systeme scharf geschaltet. Die Panels funktionieren auch nach
einem Bot-Neustart automatisch weiter (persistente Views).

---

## 5. Laufenden Betrieb

- **Neustarts** übernimmt der Hoster (bei bot-hosting.net standardmäßig aktiviert).
- **Logs** liegen beim Hoster im Panel; lokal in `data/galaxybot.log`.
- **Datenbank:** `data/galaxy.db` regelmäßig sichern (z. B. wöchentlich
  herunterladen). Beim Umzug einfach wieder hochladen.
- **Updates:** neuen Code hochladen + Server neu starten.

---

## 6. Lokal starten (zum Testen)

```bash
cd galaxy-bot
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
cp .env.example .env            # DISCORD_TOKEN eintragen
./run_bot.sh
```

> macOS-Hinweis: Falls `SSL: CERTIFICATE_VERIFY_FAILED` auftritt,
> `certifi` installieren und `SSL_CERT_FILE` setzen – `run_bot.sh` macht das
> automatisch. Bei Linux-Hosting tritt der Fehler nicht auf.

---

## 🧪 Vor dem scharfen Betrieb testen

1. `python tests/test_logik.py` (lokal)
2. `dashboard.html` im Browser (alle Systeme offline durchklicken)
3. `discord-rp-server/07_tests/01_gesamttest.md` abarbeiten
