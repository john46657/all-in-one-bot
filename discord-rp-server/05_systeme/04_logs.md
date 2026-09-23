# 📊 Log-System

Logs sind **nur für berechtigte Teammitglieder** sichtbar (Kategorie `📊 LOGS`).

---

## 📜 Channel-Zuordnung

| Channel | Inhalt | Bot |
|---|---|---|
| 📜・mod-logs | Moderationsaktionen | 🌌 GalaxyBot |
| 👤・member-logs | Join / Leave / Nick-Änderungen | 🌌 GalaxyBot + 🎭 Carl-bot |
| 🔨・punishment-logs | Warn, Kick, Ban, Timeout | 🛡️ Wick + 🌌 GalaxyBot |
| 🎭・role-logs | Rollenänderungen | 🎭 Carl-bot |
| 💬・message-logs | Gelöschte / bearbeitete Nachrichten | 🌌 GalaxyBot |
| 🎙️・voice-logs | Voice Join / Leave / Move | 🌌 GalaxyBot |
| 🤖・bot-logs | Bot-Aktionen, Statusänderungen | 🌌 GalaxyBot |
| 📋・bewerbungs-logs | Bewerbungsereignisse | 📋 Appy |
| 💰・economy-logs | Transaktionen, Strafen | 💰 UnbelievaBoat |

---

## 🔒 Berechtigungen

| Rolle | Logs sichtbar |
|---|---|
| 👑 Serverleitung | **alle** |
| 🛡️ Stellv. Serverleitung | **alle** |
| 💼 Management | alle außer 🤖・bot-logs |
| 🔧 Administration | mod-, member-, punishment-, role-, message-, voice-logs |
| 🔨 Moderation | mod-, member-, punishment-, message-logs |
| 📋 Bewerbungsteam | 📋・bewerbungs-logs |
| 🎫 Support | keine Logs |

---

## 🧾 Protokollierte Ereignisse

- **Member:** Join, Leave, Ban, Unban, Nickname-Änderung
- **Rollen:** Vergabe, Entzug (wer, welche Rolle, durch wen)
- **Nachrichten:** Löschung (Inhalt + Autor), Bearbeitung (vorher/nachher)
- **Moderation:** Warn, Timeout (Dauer), Kick, Ban (Grund, Moderator)
- **Voice:** Join, Leave, Move, Mute/Deafen (nur Stage/Voice-Events)
- **Channel:** Erstellung, Löschung, Berechtigungsänderungen
- **Bewerbung:** Einreichung, Statuswechsel, Entscheidung, Archivierung
- **Economy:** große Transaktionen ≥ 1.000 €, Daily-Claims, Strafen, Resets
- **Bot:** Start/Stop, Fehler, Konfigurationsänderungen

---

## ⚙️ Speicherung & Datenschutz

- Lösch-Logs enthalten den Inhalt – **nur** für das Team sichtbar
- Aufbewahrung: 90 Tage, danach automatische Löschung (GalaxyBot)
- Keine Protokollierung privater Fraktions-Chat-Inhalte
- Bewerbungs-Daten nur in archivierten Tickets (Serverleitung)
