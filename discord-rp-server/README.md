# 🌌 Discord RP & Community Server – Master-Dokument

Komplettes, modulares Setup für eine große RP-, Gaming- und Community-Plattform.
Jedes System hat **genau eine klar definierte Aufgabe** – keine Überschneidungen.

---

## 📋 Inhaltsverzeichnis

| Ordner | Inhalt |
|---|---|
| `01_start/` | Serverstruktur (Kategorien/Channels), Rollen, Setup-Reihenfolge |
| `02_bots/` | Bot-Matrix + Einrichtungs-Guide für alle 10 Bots |
| `03_bewerbungen/` | Bewerbungssystem + alle 11 Bewerbungsformulare |
| `04_panels/` | Discohook-Embed-JSONs für alle Panels |
| `05_systeme/` | Economy, Level, Tickets, Logs, Sicherheit, Voice, Abwesenheit |
| `06_texte/` | Regeln, Willkommensnachricht, FAQ, Links |
| `07_tests/` | Gesamttest-Katalog vor dem Launch |

---

## 🤖 Bot-Matrix – Wer macht was?

| Bot | Aufgabe | Überschneidung? |
|---|---|---|
| 🌌 **GalaxyBot** | Moderation, AutoMod, Warnungen, Kicks, Bans, Timeout, Logs, Welcome, Rollenverwaltung, Tickets, Support, Vorschläge, Umfragen, Serverstatistiken, Teamverwaltung, Social-Media/News, Custom Commands | – |
| 📋 **Appy** | Bewerbungssystem (einziger Bot dafür) | keine |
| 🎨 **Discohook** | Statische Embeds/Panels | keine |
| 💰 **UnbelievaBoat** | Economy (einziger Bot dafür) | keine |
| 🛡️ **Wick** | Anti-Raid, Anti-Nuke, Anti-Spam, Schutz | nur Sicherheit |
| 🎭 **Carl-bot** | Reaction Roles, Rollenmenüs, Automatisierung | keine Moderation |
| 📈 **Arcane** | Levelsystem | keine |
| 📊 **Statbot** | Statistiken | keine Economy/Level |
| 🎙️ **TempVoice** | Temporäre Voice-Channels | keine |
| 📢 **MonitoRSS** | Externe News (YouTube, Twitch, RSS) | keine |

---

## 🚀 Setup-Reihenfolge (WICHTIG!)

1. **Server erstellen** & Grundrollen anlegen → `01_start/02_rollen.md`
2. **Kategorien & Channels** anlegen → `01_start/01_serverstruktur.md`
3. **Bots einladen** in dieser Reihenfolge: Wick → GalaxyBot → Carl-bot → Appy → UnbelievaBoat → Arcane → Statbot → TempVoice → MonitoRSS → Discohook
4. **Wick** als Erstes konfigurieren (Anti-Raid/Anti-Nuke) → Server ist geschützt
5. **GalaxyBot** Moderation, Logs, AutoMod, Welcome, Tickets, Vorschläge/Umfragen
6. **Carl-bot** Reaction Roles für die Grundrollen-Vergabe
7. **Appy** Bewerbungen + private Bewerbungsbereiche + Status-Channel
8. **UnbelievaBoat** Economy (Währung €, Jobs, Daily, Leaderboard)
9. **Arcane** Levelsystem + Level-Rollen
10. **Statbot** Statistik-Dashboards
11. **TempVoice** Voice-Hub
12. **MonitoRSS** externe Feeds
13. **Discohook** alle Panels posten (JSONs aus `04_panels/`)
14. **Appy-Formulare** anlegen (JSONs aus `03_bewerbungen/`)
15. **Rollenhierarchie & Berechtigungen** final prüfen → `01_start/03_setup-checkliste.md`

---

## 🎨 Design-Richtlinien

- **Sprache:** durchgehend Deutsch
- **Embed-Farbe:** einheitlich `#5865F2` (Blau) für Info, Akzentfarben nur für Status
- **Statusfarben:** 🟡 `#F1C40F` Prüfung · 🔵 `#3498DB` Rückfrage · 🟠 `#E67E22` Gespräch · 🟢 `#2ECC71` Angenommen · 🔴 `#E74C3C` Abgelehnt · ⚫ `#95A5A6` Zurückgezogen
- **Emojis:** einheitlich in Channelnamen & Panels (siehe Struktur-Dokument)
- **Keine Channel-Duplikate** – jedes Thema hat genau einen Channel
