# 🎙️ Voice-System (TempVoice)

**Bot:** TempVoice (einziger Bot für temporäre Voice-Channels).

---

## 🔊 Statische Channels (Kategorie `🔊 VOICE`)

| Channel | Zweck |
|---|---|
| 🔊・Lobby | Allgemein |
| 🎮・Gaming | Gaming |
| 💬・Talk | Quatschen |
| 🎵・Musik | Musik |
| ➕・Raum-erstellen | **Hub** – erstellen temporäre Räume |

---

## ➕ Temporäre Räume

Beim Beitritt zu `➕・Raum-erstellen` erstellt TempVoice automatisch einen eigenen Channel:
- Name: `🎙️ <Username>`
- Kategorie: `🔊 VOICE`
- Nur der Ersteller hat Rechte (Verschieben, Stummschalten, Kicken)

### Befehle im eigenen Raum

| Befehl | Wirkung |
|---|---|
| `!voice name <Neuer Name>` | Namen ändern |
| `!voice limit <2-20>` | User-Limit setzen |
| `!voice lock` | Raum sperren (niemand kann mehr joinen) |
| `!voice unlock` | Sperre aufheben |
| `!voice kick <@user>` | Nutzer aus dem Raum werfen |
| `!voice ban <@user>` | Nutzer dauerhaft ausschließen |
| `!voice unban <@user>` | Ausschluss aufheben |
| `!voice claim` | Besitz übernehmen (wenn Ersteller weg ist) |

Der Raum wird automatisch gelöscht, wenn er **0 Mitglieder** hat.

---

## 🔒 Privatsphäre

- Räume sind standardmäßig privat (Ersteller + Eingeladene)
- Team-Rollen können alle Räume sehen (Support-Fälle)
- Log in `🎙️・voice-logs` nur bei Erstellung/Löschung, nicht bei Join/Leave jedes Mitglieds (Redundanz zu GalaxyBot vermeiden → GalaxyBot macht Voice-Logs)
