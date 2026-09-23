# 🤖 Bot-Setup-Guide – alle 10 Bots

Einladungs-Reihenfolge: **Wick → GalaxyBot → Carl-bot → Appy → UnbelievaBoat → Arcane → Statbot → TempVoice → MonitoRSS → Discohook**

Benötigte Berechtigungen (OAuth2) je Bot – nur die aufgeführten Rechte vergeben (Prinzip der minimalen Rechte).

---

## 🛡️ 1. Wick – Sicherheit (zuerst einladen!)

**Rechte:** Administrator (für Anti-Nuke zwingend), `Manage Roles`, `Manage Channels`, `Kick`, `Ban`, `Manage Messages`.

**Einrichtung:**
1. Dashboard öffnen (`w!dashboard` oder web-Panel)
2. **Anti-Raid**: Stufe `Strict`, automatischer Modus
3. **Anti-Nuke**: aktivieren – Massen-Kick/Ban/Channel-Löschung blockieren
4. **Anti-Spam**: Stufe `Medium`, Mention-Spam-Limit `5 Erwähnungen/10s`
5. **Rollen-Schutz**: `👑 Serverleitung`, `🛡️ Stellvertretende Serverleitung`, `💼 Management`, `🔧 Administration`, `🔨 Moderation`, `🎭 Fraktionsverwaltung`, `🤖 Bots`
6. **Channel-Schutz**: Kategorien `🔐 TEAM`, `📊 LOGS`, private Fraktionsbereiche
7. Auto-Punish: Stufe `Warn → Timeout 10m → Kick`

**Logs nach:** `🔨・punishment-logs` (Kanal-ID im Dashboard eintragen).

---

## 🌌 2. GalaxyBot – Hauptbot

**Rechte:** `Kick`, `Ban`, `Timeout`, `Manage Roles`, `Manage Channels`, `Manage Messages`, `Read Message History`, `Embed Links`, `View Audit Log`, `Mention Everyone` (nur für Ankündigungen).

**Module & Ziel-Channels:**

| Modul | Ziel |
|---|---|
| Moderation (warn/kick/ban/timeout) | Befehle im Team-Bereich |
| AutoMod | Bad-Word-Filter, Link-Schutz, Mention-Spam |
| Welcome | `👋・willkommen` (automatische Begrüßung) |
| Logs | siehe `05_systeme/04_logs.md` |
| Tickets | `🎫・ticket-erstellen` (Panel) |
| Support | `🆘・support` |
| Vorschläge | `💡・vorschläge` (Panel + Abstimmung) |
| Umfragen | `🗳️・umfragen` |
| Serverstatistiken | `📋・server-informationen` (Counter) |
| Teamverwaltung | `🔐 TEAM` |
| Social-Media/News | `📢・ankündigungen`, `🔗・links` |
| Custom Commands | z. B. `/server`, `/regeln`, `/bewerbung`, `/economy` |

**Wichtig:** GalaxyBot macht **keine** Economy, **keine** Bewerbungen, **keine** Levels.

---

## 🎭 3. Carl-bot – Rollen & Automatisierung

**Rechte:** `Manage Roles`, `Manage Messages`, `Add Reactions`, `Read Message History`.

**Einrichtung:**
1. **Reaction Roles** für: `👤 Mitglied` (Verifizierung), `⭐ VIP` (falls selbst wählbar), Fraktionsrollen **nicht** (nur über Appy!)
2. **Rollenmenü** in `📋・server-informationen` posten
3. **Custom Commands** (nicht mit GalaxyBot kollidieren – nur Sprite-Utility wie `/avatar`, `/serverinfo-helfer`)
4. **Zusätzliche Logs**: `🎭・role-logs`, `👤・member-logs`

---

## 📋 4. Appy – Bewerbungssystem

**Rechte:** `Manage Channels`, `Manage Roles`, `Manage Messages`, `Embed Links`, `Read Message History`, `Add Reactions`.

**Einrichtung:**
1. Bewerbungs-Kategorie in Appy anlegen → Output nach `📋・bewerbungen-team` (`🔐 TEAM`)
2. Archiv-Kategorie anlegen (`🗄️ Archiv`, nur Serverleitung)
3. Status-Channel → `📥・bewerbungs-status`
4. Log-Channel → `📋・bewerbungs-logs`
5. **11 Formulare** anlegen (Vorlagen: `03_bewerbungen/`)
6. Pro Formular: Freitext-Felder mit **Min. 50 / Max. 250 Wörter**, Auswahlfelder, Pflicht-Checkboxen
7. Annahme → automatische Rollenvergabe (Fraktionsrolle oder Team-Rolle) + Einstiegsrang
6. Bei Annahme: `🟢 Angenommen`, bei Ablehnung `🔴 Abgelehnt` – Beweber immer per DM benachrichtigen

**Status-Workflow:** `🟡 In Prüfung` → `🔵 Rückfrage` → `🟠 Vorstellungsgespräch` → `🟢 Angenommen` / `🔴 Abgelehnt` / `⚫ Zurückgezogen`

---

## 💰 5. UnbelievaBoat – Economy

**Rechte:** `Manage Roles`, `Embed Links`, `Add Reactions` (Leaderboard-Sortierung), `Read Message History`.

**Einrichtung:**
1. Währung: `€` (Euro), Symbol anpassen
2. Startguthaben: `500 €` Bargeld, `0 €` Bank
3. **Jobs** mit Einkommen (siehe `05_systeme/01_economy.md`)
4. **Rollen-Einkommen** (hourly/daily):
   - 👮 Polizei → 2.500 € · 🚒 Feuerwehr → 2.400 € · 🚑 Rettungsdienst → 2.300 €
   - ⚖️ Justiz → 3.000 € · 🏛️ Regierung → 3.200 € · 💼 Unternehmen → variabel
   - 💎 Booster/⭐ VIP → Bonus-Multiplikator
5. Daily Reward aktivieren (Streak-Boni)
6. Shop-Items anlegen (siehe Economy-Dokument)
7. Leaderboard-Channel → `🏆・economy-ranking`
8. Logs → `💰・economy-logs`

---

## 📈 6. Arcane – Levelsystem

**Rechte:** `Manage Roles` (für Level-Rollen), `Embed Links`, `Read Message History`, `Read Messages`.

**Einrichtung:**
1. XP: `15–25 XP pro Nachricht` ( cooldown `60s`), Voice XP `5 XP/Min`
2. Level-Rollen:
   - Level 5 → 🆕 Aktives Mitglied
   - Level 10 → ⭐ Stammmitglied
   - Level 20 → 💎 Veteran
   - Level 30 → 🏆 Community-Legende
3. Rangliste → `🏆・economy-ranking` **nicht** verwenden! Eigenen Arcane-Channel `📈・level-ranking` anlegen oder Statbot überlassen → **Empfehlung:** Arcane-Ranking per `/rank` Befehl nur privat, öffentlich nur Statbot-Aktivitätsranking.
4. XP-Boost für Booster: `2x XP` für 💎 Booster
5. Blacklist: `📊 LOGS`, `🔐 TEAM`, private Bewerbungsbereiche (kein Farmen)

---

## 📊 7. Statbot – Statistiken

**Rechte:** `View Channels`, `Read Message History`, `Embed Links`.

**Einrichtung:**
1. Message-Statistik-Dashboards: `💬・allgemein`, `🎮・gaming`, `📸・bilder`
2. Voice-Statistik: `🔊 VOICE` (Lobby, Gaming, Talk, Musik)
3. Member-Aktivität: `👤・member-logs` Statistik-Panel (Read-only)
4. Wöchentlicher Report → `📢・team-news` (Sonntags)
5. **Keine** XP/Rollen vergeben – Statbot nur lesen/auswerten

---

## 🎙️ 8. TempVoice – Voice

**Rechte:** `Manage Channels`, `Connect`, `Speak`, `Move Members`.

**Einrichtung:**
1. Hub-Channel: `➕・Raum-erstellen` (Kategorie `🔊 VOICE`)
2. Template: Name des Users als Channelnamen
3. Benutzer-Befehle: `!voice name <Name>`, `!voice limit <Zahl>`, `!voice lock`, `!voice unlock`, `!voice kick <User>`
4. Private Räume: nur Ersteller + vom Ersteller Freigegebene
5. Auto-Löschung bei 0 Mitgliedern

---

## 📢 9. MonitoRSS – externe News

**Rechte:** `Manage Webhooks`, `Embed Links`, `Read Message History`.

**Einrichtung:**
1. YouTube-Kanal verknüpfen → `📢・ankündigungen` **oder** besser eigenen Channel `📺・youtube` anlegen (Vermeidung von Überschneidung mit Team-Ankündigungen)
2. Twitch-Stream-Alerts → `📺・youtube` oder `🎮・gaming`
3. RSS-Feeds (RP-News, Community-News) → `📰・rp-news` **nur** wenn RP-relevant, sonst `🔗・links`
4. Format: Embed mit Titel, Thumbnail, Link
5. Cooldown `10 Min` pro Feed

---

## 🎨 10. Discohook – Embeds & Panels

**Rechte:** `Manage Webhooks` (nur für Panels), `Embed Links`, `Read Message History`.

**Einrichtung:**
1. Webhook pro Panel-Channel anlegen
2. Panels aus `04_panels/` als JSON laden (Webhook-Format, kompatibel mit `discohook` & `hook.gg`)
3. Einheitliche Farbe `#5865F2`, Footer `🌌 Servername • Community`
4. Panels sind **statisch** – interaktive Dinge (Tickets, Bewerbungen) über GalaxyBot/Appy

**Panels posten in:**
`👋・willkommen` · `📜・regeln` · `📋・server-informationen` · `❓・faq` · `🔗・links` · `🎭・rp-informationen` · `📖・rp-regeln` · `💼・fraktionen` · `📋・bewerbungen` · `🎫・ticket-erstellen` · `💰・economy-info` · `💡・vorschläge`
