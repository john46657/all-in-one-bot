# 📌 Serverstruktur – Kategorien & Channels

Legt die Kategorien in dieser Reihenfolge an (top → bottom im Channel-Menü).
Rechte siehe `02_rollen.md`.

---

## 📌 START

| Channel | Typ | Sichtbar | Inhalt |
|---|---|---|---|
| 👋・willkommen | Text | alle | Willkommensnachricht (GalaxyBot) |
| 📜・regeln | Text | alle | Regelwerk (Discohook-Panel) |
| 📢・ankündigungen | Text | alle | Ankündigungen (GalaxyBot/Team) |
| 📋・server-informationen | Text | alle | Serverinfo-Panel |
| 🆕・changelog | Text | alle | Updates/Änderungen |
| ❓・faq | Text | alle | FAQ-Panel |
| 🔗・links | Text | alle | Discord/Regeln/Sozial-Media-Links |

**Schreibrechte:** nur Team (👥 Mitglied darf lesen).

---

## 🎭 ROLEPLAY

| Channel | Typ | Inhalt |
|---|---|---|
| 🎭・rp-informationen | Text | RP-Grundlagen-Panel |
| 📖・rp-regeln | Text | RP-spezifische Regeln |
| 📝・charakter-erstellung | Text | Guide + Vorlage |
| 📰・rp-news | Text | RP-Neuigkeiten (Team) |
| 📅・rp-events | Text | Event-Ankündigungen |
| 💼・fraktionen | Text | Fraktionsübersicht-Panel |
| 🏠・immobilien | Text | Immobilien-System |
| 🚗・fahrzeuge | Text | Fahrzeug-System |

---

## 📋 BEWERBUNGEN

| Channel | Typ | Sichtbar | Inhalt |
|---|---|---|---|
| 📋・bewerbungen | Text | alle | Bewerbungs-Panel mit Buttons (Discohook) |
| 📥・bewerbungs-status | Text | alle | Status-Übersicht (Appy) |
| 📊・bewerbungs-info | Text | alle | Mindestanforderungen + Ablauf |

Appy erstellt **private Bewerbungsbereiche** automatisch (nur Bewerber + Bewerbungsteam).

---

## 💰 ECONOMY

| Channel | Typ | Befehle (UnbelievaBoat) |
|---|---|---|
| 💰・economy-info | Text | Erklärungs-Panel |
| 💼・jobs | Text | `/jobs`, `/job` |
| 🏪・shop | Text | `/shop`, `/buy`, `/inventory` |
| 💸・überweisungen | Text | `/pay`, `/bank`, `/deposit`, `/withdraw` |
| 🏆・economy-ranking | Text | `/leaderboard`, `/rank` |

---

## 💬 COMMUNITY

| Channel | Typ | Hinweis |
|---|---|---|
| 💬・allgemein | Text | Hauptchat |
| 😂・memes | Text | Memes/Clips |
| 📸・bilder | Text | Bilder/Screenshots |
| 🎮・gaming | Text | Gaming-Themen |
| 🎵・musik | Text | Musik |
| 💡・vorschläge | Text | Vorschlags-Panel (GalaxyBot) |
| 🗳️・umfragen | Text | Umfragen (GalaxyBot) |
| 🎁・giveaways | Text | Giveaways (Team) |

---

## 🎫 SUPPORT

| Channel | Typ | Zweck |
|---|---|---|
| 🎫・ticket-erstellen | Text | Ticket-Panel (GalaxyBot) |
| 🆘・support | Text | Allgemeine Hilfe |
| ⚠️・spieler-meldung | Text | Spieler melden |
| 🐛・bug-meldung | Text | Bugs melden |
| 💡・vorschlag | Text | Vorschläge ans Team |

> ⚠️ `💡・vorschlag` (Support) ist die **Meldung an das Team** (ticket-gebunden),
> `💡・vorschläge` (Community) ist die **öffentliche Abstimmung**. Keine Duplikation – unterschiedliche Zwecke.

---

## 👮 FRAKTIONEN

Öffentliche Channel je Fraktion:

| Channel | Fraktion |
|---|---|
| 👮・polizei | Polizei |
| 🚒・feuerwehr | Feuerwehr |
| 🚑・rettungsdienst | Rettungsdienst |
| ⚖️・justiz | Justiz |
| 🏛️・regierung | Regierung |
| 💼・unternehmen | Unternehmen |

### Private Fraktionsbereiche (je Fraktion, nur Fraktionsrolle)

- 📢・dienst-news
- 💬・dienst-chat
- 📋・dienstplan
- 📁・dokumente
- 🎙️・besprechung (Voice)

---

## 🔊 VOICE

| Channel | Typ | Hinweis |
|---|---|---|
| 🔊・Lobby | Voice | Standard |
| 🎮・Gaming | Voice | Standard |
| 💬・Talk | Voice | Standard |
| 🎵・Musik | Voice | Standard |
| ➕・Raum-erstellen | Voice | **TempVoice-Hub** – triggert temporäre Räume |

TempVoice-Befehle im eigenen Raum: `!voice name`, `!voice limit`, `!voice lock`, `!voice unlock`.

---

## 🔐 TEAM (nur Team-Rollen)

- 💬・team-chat
- 📢・team-news
- 📋・team-aufgaben
- 📋・bewerbungen-team (Appy leitet hierher weiter)
- ⚠️・verwarnungen (interne Sicht)
- 🚪・abmeldungen (Team-Abmeldungen, Bot postet automatisch)
- 📁・team-dokumente
- 🔊・team-besprechung (Voice)

---

## 📊 LOGS (nur Serverleitung + ausgewählte Team-Rollen)

| Channel | Log-Typ |
|---|---|
| 📜・mod-logs | Moderationsaktionen |
| 👤・member-logs | Join/Leave |
| 🔨・punishment-logs | Warn/Kick/Ban/Timeout |
| 🎭・role-logs | Rollenänderungen |
| 💬・message-logs | Löschungen/Änderungen |
| 🎙️・voice-logs | Voice Join/Leave |
| 🤖・bot-logs | Bot-Aktionen |
| 📋・bewerbungs-logs | Bewerbungsereignisse (Appy) |
| 💰・economy-logs | Economy-Transaktionen (UnbelievaBoat) |
