# Deployment über GitHub

Diese Anleitung zeigt, wie du das Projekt einmal zu GitHub hochlädst und danach
sowohl den Bot (bot-hosting.net) als auch das Dashboard (Cybrancee) darüber aktuell hältst,
ohne Dateien manuell hin- und herzukopieren.

## 1. Einmalig: GitHub-Repository erstellen

1. Auf https://github.com/new ein neues Repository anlegen, z.B. `emden-rp-bot`
   - **Private** auswählen (dein Code enthält Server-/Rollen-Namen eures RP-Servers,
     muss zwar nicht geheim sein, ist aber auch nicht für die Öffentlichkeit gedacht)
   - Kein README/gitignore beim Erstellen anhaken (haben wir schon lokal)

2. Auf deinem Rechner (im entpackten `emden-rp-bot`-Ordner), Terminal öffnen:
   ```bash
   cd emden-rp-bot
   git init
   git add .
   git commit -m "Erster Commit"
   git branch -M main
   git remote add origin https://github.com/DEIN-USERNAME/emden-rp-bot.git
   git push -u origin main
   ```
   Falls `git` nach einem Login fragt: GitHub verlangt inzwischen ein **Personal Access
   Token** statt eines Passworts (Einstellungen → Developer settings → Personal access
   tokens auf github.com), das du dann als Passwort einfügst.

3. Prüfen: Auf GitHub sollte jetzt der komplette Code sichtbar sein - **außer** `.env`
   und `dashboard/.env` (die stehen in der `.gitignore` und werden nie hochgeladen).

## 2. Bot bei bot-hosting.net per Git verbinden

1. Im bot-hosting.net-Kontrollpanel deines Servers nach der Funktion **"Git"** bzw.
   **"Clone a Git repository"** suchen (steht so in deren Wiki)
2. Dort die Repo-URL eintragen: `https://github.com/DEIN-USERNAME/emden-rp-bot.git`
   - Bei einem privaten Repo brauchst du dafür ein Personal Access Token statt Passwort
     (dasselbe wie oben, mit Leserechten auf das Repo reicht)
3. Server zieht sich den Code. `.env` musst du dort **einmalig manuell** im Panel anlegen
   (Datei-Editor im Panel öffnen, `.env` erstellen, Werte aus `.env.example` übernehmen)
   - das ist Absicht, da Secrets nie im Git-Repo landen sollen
4. Danach: bei jeder Code-Änderung reicht im Panel ein Klick auf "Pull"/"Update" (Name je
   nach Panel-Version leicht anders), statt neu hochzuladen

## 3. Dashboard bei Cybrancee per Git verbinden

1. Im Cybrancee-Panel nach **"Git Version Control"** oder ähnlichem suchen
2. Repo-URL eintragen, aber **nur den `dashboard/`-Unterordner** als Wurzel angeben, falls
   das Panel das unterstützt (manche Panels erlauben "Repository Path" innerhalb des Repos).
   Unterstützt Cybrancee das nicht, klonst du das ganze Repo und stellst den "Application
   Root"/"Startordner" der App auf `dashboard/` ein
3. `dashboard/.env` auch hier einmalig manuell im Panel anlegen (Werte aus
   `dashboard/.env.example`)
4. Bei Änderungen: "Pull"/"Update" im Panel klicken

## 4. Ablauf bei künftigen Änderungen

```bash
# Änderungen lokal machen, dann:
git add .
git commit -m "Kurze Beschreibung der Änderung"
git push
```
Danach auf beiden Panels (bot-hosting.net und Cybrancee) einmal "Pull"/"Update" klicken
(oder den Server dort neu starten, falls das Panel Git-Updates nur beim Neustart zieht).

**Falls ein Panel Auto-Deploy bei jedem Push unterstützt** (oft als "Webhook" oder
"Auto-Deploy" bezeichnet), kannst du das aktivieren - dann entfällt sogar der manuelle
Klick.
