# 🌌 RP & Community Discord – Komplettsystem

Vollständiges, modulares Setup für eine große RP-, Gaming- und Community-Plattform
(GTA/FiveM-RP, Roleplay, Gaming) nach dem Master-Prompt.

Jeder Bot hat **genau eine klar definierte Aufgabe** – keine Überschneidungen.
Berechtigungen folgen dem Prinzip der geringstmöglichen notwendigen Rechte.

---

## 📦 Was ist enthalten?

| Komponente | Ort | Inhalt |
|---|---|---|
| 🌌 **GalaxyBot** | [`galaxy-bot/`](galaxy-bot) | Zentraler Bot: Moderation, AutoMod, Welcome, Tickets, Vorschläge/Umfragen, Team-Abwesenheit, Logs – als ausführbarer Code |
| 🏗️ **Setup-Skript** | [`setup/`](setup) | Legt Serverstruktur (Rollen, Kategorien, Channels, Berechtigungen) 1:1 an – idempotent |
| 🤖 **Emden RP Bot** | [`emden-rp-bot/`](emden-rp-bot) | Fraktions-Bot (Polizei): Dienst, Ausbildung, GSG9, Fahndung, Funk, Teamliste |
| 📚 **Doku-Paket** | [`discord-rp-server/`](discord-rp-server) | Serverstruktur, Rollen, Bot-Matrix, 11 Bewerbungsformulare, Discohook-Panels, Systeme, Gesamttest |

---

## 🚀 Schnellstart (Master-Prompt §33: Einrichtungs-Reihenfolge)

```bash
# 1. Serverstruktur + Rollen + Berechtigungen anlegen
cd setup
python setup_server.py --guild-id <ID> --dry-run   # erst prüfen
python setup_server.py --guild-id <ID>             # dann anlegen

# 2. GalaxyBot starten
cd ../galaxy-bot
pip install -r requirements.txt
cp .env.example .env       # DISCORD_TOKEN eintragen
python bot.py

# 3. Panels posten (je einmal)
#    /ticket panel, /vorschlag panel, /abwesenheit panel
```

Danach: Wick → Carl-bot → Appy → UnbelievaBoat → Arcane → Statbot →
TempVoice → MonitoRSS → Discohook einladen und konfigurieren
(siehe `discord-rp-server/02_bots/`).

---

## 🧪 Testen vor dem Launch

| Test | Wie |
|---|---|
| Bot-Logik (Wortgrenzen 49/50/250/251, Parser, Hierarchie) | `cd galaxy-bot && python tests/test_logik.py` |
| Alle Systeme interaktiv (Browser, offline) | `galaxy-bot/dashboard.html` öffnen |
| Gesamttest-Katalog | `discord-rp-server/07_tests/01_gesamttest.md` abarbeiten |

---

## 🤖 Bot-Matrix

| Bot | Aufgabe |
|---|---|
| 🌌 **GalaxyBot** | Moderation, AutoMod, Welcome, Tickets, Vorschläge/Umfragen, Abwesenheit, Logs |
| 📋 **Appy** | Bewerbungen (einziger Bot dafür) |
| 🎨 **Discohook** | Statische Embeds/Panels |
| 💰 **UnbelievaBoat** | Economy (einziger Bot dafür) |
| 🛡️ **Wick** | Anti-Raid, Anti-Nuke, Anti-Spam |
| 🎭 **Carl-bot** | Reaction Roles, Automatisierung |
| 📈 **Arcane** | Levelsystem |
| 📊 **Statbot** | Statistiken |
| 🎙️ **TempVoice** | Temporäre Voice-Channels |
| 📢 **MonitoRSS** | Externe News (YouTube, Twitch, RSS) |
| 🚔 **Emden RP Bot** | Fraktionsmechaniken (Polizei): Dienst, Funk, GSG9, Fahndung |

---

## 📐 Grundsätze

- **Keine Funktionsüberschneidungen** zwischen Bots (Master-Prompt §1)
- Berechtigungen nach dem Prinzip der **geringstmöglichen Rechte** (§4)
- **Datensparsamkeit**: „Privater Grund“ wird immer akzeptiert (§25)
- Alles modular, sicher, übersichtlich und langfristig erweiterbar
- Durchgehend **deutsch**, einheitliches Design (Farbe `#5865F2`)
