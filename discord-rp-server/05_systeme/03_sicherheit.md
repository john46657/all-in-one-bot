# 🛡️ Sicherheit (Wick + GalaxyBot)

Wick und GalaxyBot ergänzen sich: **Wick = Massenaktionen/Raid-Schutz, GalaxyBot = einzelne Nachrichten/Filter.**

---

## 🧱 Wick – Schutz-Schichten

| Modul | Einstellung |
|---|---|
| Anti-Raid | Stufe `Strict` – automatischer Modus, Account-Alter prüfen |
| Anti-Nuke | Massen-Kick/Ban/Channel-Löschung blockieren, Role-Hoist-Schutz |
| Anti-Spam | Stufe `Medium` – Mention-Spam `5/10s` |
| Role Protection | Serverleitung, Stellv. Leitung, Management, Administration, Moderation, Fraktionsverwaltung, Bots |
| Channel Protection | Kategorien `🔐 TEAM`, `📊 LOGS`, private Fraktionsbereiche |
| Anti-Webhook | Webhook-Missbrauch blockieren |
| Anti-Emoji/Stecker | Massenlöschung von Emojis verhindern |

**Auto-Punish:** Warn → Timeout 10 Min → Kick → Ban (bei Wiederholung).

---

## 🤖 GalaxyBot – AutoMod

| Filter | Einstellung |
|---|---|
| Bad-Word-Filter | deutsches + englisches Wortliste, `***`-Zensur |
| Mention-Spam | max. 5 Erwähnungen pro Nachricht |
| Link-Schutz | Discord-Invites blockieren (außer Whitelist), verdächtige Domains warnen |
| Spam-Schutz | Identische Nachrichten ≤ 3 in 10 s |
| Emoji-Spam | max. 10 Emojis pro Nachricht |
| Caps-Lock | > 70 % Großbuchstaben blockieren |
| Zweitaccount-Erkennung | Join-Überwachung, verdächtige Muster markieren |

---

## 🔐 Account & Server

- Verifizierungsstufe: **Hoch** (verifizierte E-Mail, 5 min Mitglied)
- 2FA-Pflicht für alle Team-Rollen (Servereinstellungen → Sicherheit)
- "Server-Inhalt scannen" für alle Mitglieder
- Rolle `🆕 Neuer Bürger` mit eingeschränkten Rechten bis zur Verifizierung
- `👤 Mitglied` wird erst nach Regeln-Lesen vergeben (Carl-bot Reaction Role)

---

## 📡 Protokollierung

Alle Sicherheitsereignisse landen in `📊 LOGS` – siehe `04_logs.md`.
Wick-spezifische Punishments → `🔨・punishment-logs`.

---

## 🚨 Notfall-Plan

1. Raid erkannt → Wick sperrt automatisch (Modus "Panic" per `w!panic`)
2. Serverleitung informiert (Ping in `🔐 TEAM`)
3. Manuelle Nachprüfung in `📜・mod-logs`
4. Ggf. vorübergehend Verifizierungsstufe auf **Höchste**
