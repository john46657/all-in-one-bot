# 🧪 Gesamttest – vor dem Launch

Vor dem offiziellen Launch (Master-Prompt §34/§35) müssen **alle** Systeme
durchgetestet werden. Jede Zeile muss abgehakt werden.

> Tipp: Das **HTML-Test-Dashboard** (`galaxy-bot/dashboard.html` im Browser öffnen!)
> bildet die meisten dieser Tests 1:1 offline nach – inklusive der Wortgrenzen
> 49/50/250/251 und des kompletten Abwesenheits-Workflows.

---

## 📋 Bewerbungen (Appy)

- [ ] 49 Wörter → ablehnen
- [ ] 50 Wörter → akzeptieren
- [ ] 250 Wörter → akzeptieren
- [ ] 251 Wörter → ablehnen
- [ ] Bewerbung absenden
- [ ] Bewerbungs-ID wird erstellt
- [ ] Status 🟡 In Prüfung
- [ ] Zuständiges Team wird benachrichtigt
- [ ] Rückfrage (🔵)
- [ ] Vorstellungsgespräch (🟠)
- [ ] Annahme (🟢) + Rolle vergeben
- [ ] Ablehnung (🔴)
- [ ] Zurückgezogen (⚫)
- [ ] Archivierung
- [ ] Bewerbungslog erstellt

---

## 💤 Abwesenheit (GalaxyBot)

- [ ] Antrag einreichen (Status 🟡 Eingereicht)
- [ ] Genehmigung (🟢)
- [ ] Ablehnung (🔴)
- [ ] Automatischer Start → 🟣 Aktiv
- [ ] Rolle 💤 Abwesend vergeben
- [ ] Erinnerung vor Ende
- [ ] Verlängerung beantragt (🔵)
- [ ] Verlängerung bestätigt
- [ ] Rückkehr melden (⚫)
- [ ] Rolle entfernt
- [ ] Automatische Beendigung bei Ablauf
- [ ] Abwesenheitsübersicht aktualisiert
- [ ] Abwesenheitslog erstellt
- [ ] Kurzfristige Abmeldung (sofort aktiv)
- [ ] Übergabe-Text mit < 50 Wörtern wird blockiert

---

## 💰 Economy (UnbelievaBoat)

- [ ] Bargeld anzeigen
- [ ] Bankkonto
- [ ] Job annehmen
- [ ] Shop / Items kaufen
- [ ] Überweisung an anderen Spieler
- [ ] Daily Reward
- [ ] Leaderboard
- [ ] Rollen-Einkommen (Polizei 2.500 € etc.)

---

## 🔨 Moderation (GalaxyBot)

- [ ] `/warn` + Verwarnungs-Log
- [ ] `/timeout` (Dauerformate 10m/1h/2h30m/1d)
- [ ] `/kick`
- [ ] `/ban`
- [ ] AutoMod: Spam
- [ ] AutoMod: Mention-Spam
- [ ] AutoMod: Link-/Einladungs-Schutz
- [ ] Punishment-Logs

---

## 🛡️ Sicherheit (Wick + GalaxyBot)

- [ ] Spam-Angriff simulieren → Wick/GalaxyBot reagiert
- [ ] Mention-Spam → Timeout
- [ ] Raid-Simulation (viele Joins) → Anti-Raid greift
- [ ] Rollenänderung an geschützter Rolle → blockiert
- [ ] Channel-Löschung → Channel-Schutz greift
- [ ] Massenaktionen → Anti-Nuke greift

---

## 🎫 Tickets & Community (GalaxyBot)

- [ ] Ticket erstellen (alle 6 Arten)
- [ ] Ticket nur für Ersteller + Team sichtbar
- [ ] Ticket schließen
- [ ] Vorschlag einreichen + abstimmen
- [ ] Vorschlag annehmen/ablehnen
- [ ] Umfrage starten + abstimmen (kein Double-Vote)
- [ ] Umfrage läuft ab und wird ausgezählt

---

## 📊 Übrige Systeme

- [ ] Welcome: Join → Rolle 🆕 Neuer Bürger + Willkommensnachricht
- [ ] Levelsystem: XP/Level + Level-Rollen (Arcane)
- [ ] Statistiken: Dashboards (Statbot)
- [ ] TempVoice: Raum erstellen + verwalten
- [ ] MonitoRSS: YouTube/Twitch/RSS-Feeds
- [ ] Carl-bot: Reaction Roles funktionieren

---

## 🚀 Soft Launch (§35)

- [ ] Kleine Testgruppe einladen
- [ ] Alle Systeme testen
- [ ] Fehler dokumentieren & beheben
- [ ] Berechtigungen prüfen (jede Rolle nur das Nötigste)
- [ ] Bewerbungen/Economy/Tickets/Abwesenheit im Echtbetrieb testen

**Erst danach:** Server öffentlich machen (§36).
