# 🤖 Bot-Matrix – Verantwortlichkeiten & Abgrenzungen

Keine Funktion wird von zwei Bots ausgeführt.

| Funktion | Zuständig | Nicht zuständig |
|---|---|---|
| Warn / Kick / Ban / Timeout | 🌌 GalaxyBot | Wick (nur Auto-Protect) |
| Anti-Raid / Anti-Nuke | 🛡️ Wick | GalaxyBot (nur AutoMod-Filter) |
| Bewerbungen | 📋 Appy | GalaxyBot, Carl-bot |
| Economy | 💰 UnbelievaBoat | GalaxyBot, Arcane |
| Level / XP | 📈 Arcane | Statbot |
| Statistiken | 📊 Statbot | Arcane |
| Temporäre Voice | 🎙️ TempVoice | GalaxyBot |
| Reaction Roles | 🎭 Carl-bot | GalaxyBot (nur rollenbasiert bei Bewerbungsannahme) |
| Externe News | 📢 MonitoRSS | GalaxyBot (nur interne Ankündigungen) |
| Statische Panels | 🎨 Discohook | GalaxyBot (nur dynamische/interaktive Panels) |
| Tickets | 🌌 GalaxyBot | Appy (Bewerbungen = eigener Bereich) |
| Logs | 🌌 GalaxyBot (Haupt-Logs) + Carl-bot (Rollen) + Appy (Bewerbungen) + UnbelievaBoat (Economy) | Statbot (nur Statistik) |
| Welcome | 🌌 GalaxyBot (DM + Channel) | Discohook (nur statisches Panel) |
| Custom Commands | 🌌 GalaxyBot | Carl-bot (nur Utility) |

---

## ⚠️ Konfliktvermeidung

1. **AutoMod (GalaxyBot) vs. Anti-Spam (Wick):** Wick greift bei Massenaktionen (Raid/Nuke), GalaxyBot-Filter bei einzelnen Nachrichten (Bad Words, Links). Überschneidung bewusst: GalaxyBot filtert → wird umgangen → Wick punisht.
2. **Economy-Logs:** nur UnbelievaBoat; GalaxyBot loggt **keine** Transaktionen.
3. **Rollenvergabe:** Carl-bot = selbst gewählbar (VIP etc.); Appy = Fraktionsrollen bei Annahme; Arcane = Level-Rollen. Kein Bot vergibt Team-Rollen außer Appy (Support/Moderator/etc. nach Team-Entscheidung).
4. **Statistik-Rangliste:** nur **ein** öffentliches Ranking (Statbot). Arcane `/rank` = privat per DM/ephemeral.
5. **News-Channels:** `📢・ankündigungen` = nur Team (GalaxyBot). Externe Feeds = `📺・youtube`/RSS-Channel (MonitoRSS).
