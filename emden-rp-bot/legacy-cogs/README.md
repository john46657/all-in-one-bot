# legacy-cogs – inaktive Module

Diese Cogs waren früher Teil des Emden RP Bots und sind mittlerweile von
anderen Bots übernommen worden (Master-Prompt §1: **keine Überschneidungen**
zwischen Bots).

| Datei | Neuer Zuständiger | Ersatz |
|---|---|---|
| `bewerbungen.py` | 📋 **Appy** | Bewerbungssystem für alle 10 Bereiche (Polizei, Feuerwehr, Justiz, Support, …) |
| `tickets.py` | 🌌 **GalaxyBot** | `cogs/tickets.py` – 6 Ticketarten (Support, Bewerbung, Spieler melden, Bug, Vorschlag, Partnerschaft) |
| `abmelden.py` | 🌌 **GalaxyBot** | `cogs/absence.py` – Team-Abwesenheit mit Genehmigungsworkflow, Statusfarben, Verlängerung, Übersicht |

Sie werden in `bot.py` **nicht** geladen und dienen nur als Referenz bzw.
Fallback, solange GalaxyBot/Appy noch nicht eingerichtet sind.

## Wieder aktivieren (Fallback)

Falls GalaxyBot oder Appy (noch) nicht laufen, können die Cogs kurzfristig
wieder eingebunden werden:

1. Datei aus `legacy-cogs/` nach `cogs/` verschieben
2. In `bot.py` im `cogs`-Listen-Eintrag ergänzen (z. B. `"cogs.tickets"`)
3. Bot neu starten

**Aber Achtung:** läuft GalaxyBot parallel, gibt es doppelte Ticket-Panels und
zwei Systeme für Abwesenheiten – genau das, was der Master-Prompt vermeiden will.
