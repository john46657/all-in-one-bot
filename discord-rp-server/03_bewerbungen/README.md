# 📋 Bewerbungsformulare – Übersicht

10 Formulare, alle als Appy-Vorlage im Ordner. Freitext-Pflichtfelder **immer** 50–250 Wörter.

| Datei | Formular | Rolle bei Annahme | Mindestalter | Gespräch |
|---|---|---|---|---|
| `01_polizei.json` | 👮 Polizei | 👮 Polizei | 16 | – |
| `02_feuerwehr.json` | 🚒 Feuerwehr | 🚒 Feuerwehr | 16 | – |
| `03_rettungsdienst.json` | 🚑 Rettungsdienst | 🚑 Rettungsdienst | 16 | – |
| `04_justiz.json` | ⚖️ Justiz | ⚖️ Justiz | 18 | – |
| `05_support.json` | 🎫 Support | 🎫 Support | 16 | – |
| `06_moderator.json` | 🔨 Moderator | 🔨 Moderation | 16 | – |
| `07_administrator.json` | 🛡️ Administrator | 🔧 Administration | 18 | ✅ |
| `08_teamleitung.json` | 👑 Teamleitung | 💼 Management | 18 | ✅ |
| `09_fraktionsleitung.json` | 🎭 Fraktionsleitung | 🎭 Fraktionsverwaltung | 18 | ✅ |
| `10_unternehmen.json` | 🏢 Unternehmen | 💼 Unternehmen | 16 | – |

## Aufbau jeder JSON

```json
{
  "form_id": "...",
  "title": "...",
  "role_on_accept": "...",
  "min_age": 16,
  "requires_interview": false,
  "status_workflow": [...],
  "requirements": [...],
  "word_limits": { "textarea_min": 50, "textarea_max": 250 },
  "fields": [ ... ]
}
```

## Feldtypen

| Typ | Verwendung |
|---|---|
| `text` | Kurze Eingaben (Discord-Name, ID) – **keine** Wortgrenze |
| `textarea` | Alle Freitext-Pflichtfragen – **50–250 Wörter** |
| `select` | Alter, Zeitzone, Online-Zeit, Verfügbarkeit, Ja/Nein, Multiple Choice |
| `checkbox` | Pflicht-Bestätigungen |

## Reihenfolge der Felder in jedem Formular

1. Allgemeine Pflichtfelder (15)
2. Bereichsspezifische Fragen (6–7)
3. Fallbeispiel (1)
4. Bestätigungs-Checkbox (1)

## Zuordnung zuständiges Team

| Formular | Prüft |
|---|---|
| Polizei / Feuerwehr / Rettungsdienst | Fraktionsverwaltung + Bewerbungsteam |
| Justiz | Fraktionsverwaltung + Management |
| Support / Moderator | Moderation + Bewerbungsteam |
| Administrator / Teamleitung | Serverleitung + Stellvertretende Serverleitung |
| Fraktionsleitung | Serverleitung + Management |
| Unternehmen | Fraktionsverwaltung + Bewerbungsteam |
