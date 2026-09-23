# 🚪 Abmelden-System (Team)

Mitglieder ausgewählter Team-Rollen können sich für einige Tage abmelden. Das Team wird automatisch informiert, das Mitglied erhält eine Rolle und nach Ablauf wird alles automatisch zurückgesetzt.

**Bot:** GalaxyBot / eigenen Bot (Cog `abmelden.py`) · **Nur für Team-Rollen**

---

## ⚙️ Berechtigung: welche Rollen dürfen sich abmelden?

Ein Admin legt fest, welche Rollen berechtigt sind. **Mehrere Rollen gleichzeitig möglich.**

| Befehl | Wirkung |
|---|---|
| `/abmelden setup` | Öffnet ein Select-Menü, mehrere Rollen gleichzeitig wählbar |
| `/abmelden rolle_hinzufuegen rolle_id:<ID>` | Einzelne Rolle per ID hinzufügen |
| `/abmelden rolle_entfernen rolle_id:<ID>` | Einzelne Rolle per ID entfernen |
| `/abmelden berechtigt` | Zeigt alle berechtigten Rollen |

**Rollen-ID finden:** Servereinstellungen → Rollen → Rolle rechtsklicken → ID kopieren.
Berechtigung gilt, wenn ein Mitglied **eine** der hinterlegten Rollen hat (oder Administrator ist).

---

## 📝 Abmelden

| Befehl | Wirkung |
|---|---|
| `/abmelden jetzt` | Öffnet das Abmelde-Modal |
| `/abmelden entfernen` | Eigene Abmeldung vorzeitig beenden (Admins auch für andere) |
| `/abmelden liste` | Zeigt alle aktuell Abgemeldeten (Team) |

### Modal-Felder

| Feld | Pflicht | Hinweis |
|---|---|---|
| Grund | ✅ | z. B. Urlaub, Krankheit, Prüfungen |
| Von | ✅ | `TT.MM.JJJJ` |
| Bis | ✅ | `TT.MM.JJJJ` |
| Vertretung | – | wer übernimmt die Aufgaben |

---

## 🔄 Ablauf

```
1. Teammitglied führt /abmelden jetzt aus
2. Modal ausfüllen (Grund, Von, Bis, Vertretung)
3. Bot prüft Berechtigung + Datum
4. Bot postet Embed in 🚪・abmeldungen (Team wird informiert)
5. Rolle "Abgemeldet" wird vergeben
6. Bot prüft alle 30 Minuten auf Ablauf
7. Bei Ablauf: Rolle automatisch entfernt + Nachricht aktualisiert
   "✅ Abmeldung abgelaufen - <user> ist wieder da."
8. Abmeldung wird als inaktiv markiert (Archiv)
```

---

## 🎛️ Benötigte Server-Einrichtung

1. **Rolle erstellen:** `Abgemeldet` (Farbe z. B. `#95A5A6`)
   - Keine besonderen Rechte – nur ein sichtbarer Indikator
   - Bot-Rolle muss **über** dieser Rolle stehen (sonst kann er sie nicht vergeben/entfernen)
2. **Channel erstellen:** `🚪・abmeldungen` (Kategorie `🔐 TEAM`, nur Team sichtbar)
3. Bot-Rechte: `Manage Roles`, `Send Messages`, `Embed Links`, `Read Message History`
4. `/abmelden setup` ausführen → Rollen auswählen
5. Fertig – Teammitglieder können `/abmelden jetzt` nutzen

---

## 🔒 Hinweise

- Doppelte Abmeldungen werden blockiert (erst alte beenden)
- `Bis` muss nach `Von` liegen
- Abwesenheitsnotiz ist **nur für das Team sichtbar** (Privatsphäre)
- Neue Abmeldungen überschreiben keine alten – pro Mitglied ist nur eine aktiv
- Bei vorzeitigem Ende (`/abmelden entfernen`) wird die Rolle sofort entfernt
