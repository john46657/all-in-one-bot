# 💤 Team-Abwesenheitssystem

Mitglieder aller Team-Rollen können Abwesenheiten melden. Die Teamleitung
genehmigt oder lehnt ab; zum Start wird die Abwesenheit automatisch aktiv und
die Rolle `💤 Abwesend` vergeben, am Ende automatisch entfernt.

**Bot:** GalaxyBot (Cog `cogs/absence.py`) · **Panel-Channel:** `📅・team-abwesenheit`
**Übersicht:** `📅・abwesenheitsübersicht` (nur Team) · **Logs:** `💤・abwesenheits-logs`

---

## 🎛️ Panel (5 Buttons)

Das Panel wird einmalig gepostet:

| Befehl | Wirkung |
|---|---|
| `/abwesenheit panel` | Postet das Panel in `📅・team-abwesenheit` |
| `/abwesenheit übersicht` | Aktualisiert die Abwesenheitsübersicht |

| Button | Funktion |
|---|---|
| 💤 **Abwesenheit melden** | Mehrstufiges Formular (Grund → Zeitraum → Übergabe → Erreichbarkeit) |
| 📅 **Meine Abwesenheit** | Zeigt die eigenen Abwesenheiten an |
| 🔄 **Abwesenheit verlängern** | Neues Enddatum + optionaler Hinweis – Teamleitung muss bestätigen |
| ✅ **Rückkehr melden** | Beendet die Abwesenheit vorzeitig, Rolle wird entfernt |
| 🚨 **Kurzfristig abmelden** | Beginn + Dauer + Erreichbarkeit – sofort aktiv, keine Freigabe nötig |

---

## 📝 Formular (normale Abwesenheit)

Automatisch erfasst: Discord-Name, Discord-ID, Team-Rolle, Antragstellungsdatum.

| Feld | Pflicht | Hinweis |
|---|---|---|
| Grund | ✅ | Auswahl: Urlaub, Schule/Ausbildung, Arbeit, Private Gründe, Gesundheitliche Gründe, Technische Probleme, Sonstiges, **Privater Grund** |
| Beginn | ✅ | `TT.MM.JJJJ` |
| Ende | ✅ | `TT.MM.JJJJ` |
| Voraussichtliche Rückkehr | ✅ | `TT.MM.JJJJ` |
| Aufgabenübergabe erforderlich? | ✅ | Ja/Nein |
| → Übergabe-Text | nur bei Ja | **50–250 Wörter**: Aufgaben, Fristen, Vertretung, wichtige Infos |
| Erreichbarkeit | ✅ | 🟢 Erreichbar · 🟡 Eingeschränkt erreichbar · 🔴 Nicht erreichbar |

Kurzfristige Abwesenheit: Beginn, voraussichtliche Dauer, Erreichbarkeit,
optionaler Hinweis. **Keine** detaillierte private Begründung erforderlich.

---

## 🔖 Status

| Status | Bedeutung |
|---|---|
| 🟡 Eingereicht | Antrag liegt vor, wartet auf Entscheidung |
| 🟢 Genehmigt | Teamleitung hat genehmigt, noch nicht gestartet |
| 🔴 Abgelehnt | Teamleitung hat abgelehnt |
| 🔵 Verlängert | Verlängerung wurde bestätigt |
| 🟣 Aktiv | Abwesenheit läuft, Rolle `💤 Abwesend` ist vergeben |
| ⚫ Beendet | Rückkehr gemeldet oder Zeitraum abgelaufen, Rolle entfernt |

---

## 🔄 Ablauf

```
Teammitglied meldet Abwesenheit
        ↓
System erstellt ID (ABW-0001)
        ↓
Status 🟡 Eingereicht  →  Panel-Nachricht mit ✅/✖️ Buttons
        ↓
Teamleitung entscheidet: 🟢 Genehmigt / 🔴 Abgelehnt
        ↓
Zum Startdatum: 🟣 Aktiv + Rolle 💤 Abwesend (automatisch)
        ↓
Erinnerung 1 Tag vor Ende (per DM)
        ↓
Rückkehr ✅ oder Ablauf: ⚫ Beendet + Rolle entfernt (automatisch)
        ↓
Jeder Schritt wird in 💤・abwesenheits-logs protokolliert
```

---

## 📅 Regeln

- Ab **3 Kalendertagen** soll eine Abwesenheit grundsätzlich gemeldet werden.
- Kürzere Abwesenheiten können freiwillig oder auf Wunsch der Teamleitung gemeldet werden.
- Ungeplante Abwesenheiten können nachträglich eingetragen werden (🚨 Kurzfristig).
- Pro Mitglied ist nur eine aktive Abwesenheit möglich.

---

## 🔐 Datenschutz

Das System arbeitet datensparsam. **Nicht** erfragt werden:

- Gesundheitsdaten / medizinische Informationen
- private Dokumente
- persönliche Details

**„Privater Grund" muss immer akzeptiert werden** und ist eine voll gültige Angabe.

---

## 🎛️ Server-Einrichtung

1. **Rolle:** `💤 Abwesend` (Farbe z. B. `#95A5A6`) – reine Indikator-Rolle,
   **keine** permanenten Berechtigungsänderungen.
2. **Channels:** `📅・team-abwesenheit` + `📅・abwesenheitsübersicht` (Kategorie `🔐 TEAM`),
   `💤・abwesenheits-logs` (Kategorie `📊 LOGS`).
   → Alles wird vom `setup/setup_server.py`-Skript automatisch angelegt.
3. Bot-Rechte: `Manage Roles` (für `💤 Abwesend`), `Send Messages`, `Embed Links`,
   `Read Message History`. Bot-Rolle muss über `💤 Abwesend` stehen.
4. `/abwesenheit panel` einmal ausführen. Teammitglieder (alle Team-Rollen) können
   das Panel sofort nutzen; genehmigen/ablehnen darf die Serverleitung.
