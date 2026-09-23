# 🎭 Rollen – Hierarchie & Berechtigungen

Rollen von **oben (höchste Rechte) nach unten** anlegen. Die Reihenfolge ist maßgeblich für Berechtigungen.

---

## 👑 Team-Rollen

| Rolle | Farbe | Wichtigste Rechte |
|---|---|---|
| 👑 Serverleitung | `#FFD700` | Administrator (alles) |
| 🛡️ Stellvertretende Serverleitung | `#FF8C00` | Administrator, Wick-Einstellungen, Bot-Verwaltung |
| 💼 Management | `#9B59B6` | Kanäle/Rollen verwalten, Bewerbungs-Entscheidungen |
| 🔧 Administration | `#E91E63` | Moderation (kick/ban/timeout), Bewerbungen, Logs einsehen |
| 🔨 Moderation | `#3498DB` | timeout, warn, Nachrichten löschen, mod-logs |
| 🎫 Support | `#1ABC9C` | Tickets, Support-Channel, spieler-meldung |
| 📋 Bewerbungsteam | `#F1C40F` | Bewerbungen einsehen/entscheiden (Appy) |
| 🎭 Fraktionsverwaltung | `#2ECC71` | Fraktionsbereiche verwalten |
| 🎮 Event-Team | `#E67E22` | rp-events, Giveaways |
| 📢 Social-Media-Team | `#FF69B4` | ankündigungen, Social-Media-Funktionen |
| 🎥 Content Creator | `#00B0F4` | Eigene Inhalte teilen (keine Moderation) |
| 🚪 Abgemeldet | `#95A5A6` | Indikator-Rolle – wird vom Bot bei Abmeldung vergeben/entfernt |

## 💎 Community-Rollen

| Rolle | Farbe | Rechte |
|---|---|---|
| 💎 Booster | `#F47FFF` | Danke-Extras (Booster-spezifisch) |
| ⭐ VIP | `#FFD700` | Extra-Economy-Boni, Priority-Queue |
| 👤 Mitglied | `#5865F2` | Standard (Lesen/Schreiben nach Verifizierung) |
| 🆕 Neuer Bürger | `#95A5A6` | Lesen, eingeschränktes Schreiben (bis Verifizierung) |

## 🤖 Bot-Rolle

| Rolle | Hinweis |
|---|---|
| 🤖 Bots | **Ganz oben** platzieren (für Rollenverwaltung); keine Administrator-Rechte außer GalaxyBot |

## 👮 RP-Rollen (Fraktionen)

| Rolle | Farbe | Einkommen (UnbelievaBoat) |
|---|---|---|
| 👮 Polizei | `#0044CC` | 2.500 € |
| 🚒 Feuerwehr | `#CC3300` | 2.400 € |
| 🚑 Rettungsdienst | `#FF0000` | 2.300 € |
| ⚖️ Justiz | `#8B0000` | 3.000 € |
| 🏛️ Regierung | `#FFD700` | 3.200 € |
| 💼 Unternehmen | `#2ECC71` | variabel |

## 🏆 Level-Rollen (Arcane – automatisch vergeben)

| Level | Rolle |
|---|---|
| 5 | 🆕 Aktives Mitglied |
| 10 | ⭐ Stammmitglied |
| 20 | 💎 Veteran |
| 30 | 🏆 Community-Legende |

> Level-Rollen unterhalb der Fraktionsrollen platzieren, damit Fraktionsrechte Vorrang haben.

---

## 🔒 Rollen-Schutz (Wick)

Folgende Rollen müssen in Wick als **geschützt** markiert werden:
`👑 Serverleitung`, `🛡️ Stellvertretende Serverleitung`, `💼 Management`, `🔧 Administration`, `🔨 Moderation`, `🎭 Fraktionsverwaltung`, `🤖 Bots`.

Niemand außer `👑 Serverleitung` darf diese Rollen vergeben/entfernen.

---

## 📝 Berechtigungs-Matrix (Kategorie-Sichtbarkeit)

| Kategorie | Mitglied | Team | Bemerkung |
|---|---|---|---|
| 📌 START | ✅ lesen | ✅ | Schreiben nur Team |
| 🎭 ROLEPLAY | ✅ | ✅ | Schreiben nur Team in News/Events |
| 📋 BEWERBUNGEN | ✅ Panel | ✅ | Nur Bewerbungsteam sieht private Bereiche |
| 💰 ECONOMY | ✅ | ✅ | economy-logs nur Team |
| 💬 COMMUNITY | ✅ | ✅ | AutoMod aktiv |
| 🎫 SUPPORT | ✅ | ✅ | Tickets nur Ersteller + Team |
| 👮 FRAKTIONEN (öffentlich) | ✅ | ✅ | – |
| 👮 FRAKTIONEN (privat) | ❌ | ✅ | Nur jeweilige Fraktionsrolle |
| 🔊 VOICE | ✅ | ✅ | – |
| 🔐 TEAM | ❌ | ✅ | Nur Team-Rollen |
| 📊 LOGS | ❌ | ✅ | Nur Serverleitung + Administration |
