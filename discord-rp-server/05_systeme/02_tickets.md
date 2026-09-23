# 🎫 Ticket-System (GalaxyBot)

Tickets sind **nur für den Ersteller und das zuständige Team** sichtbar.

---

## 🎛️ Kategorien

| Button | Zweck | Zuständig |
|---|---|---|
| 🎫 Support | Allgemeine Fragen & Hilfe | 🎫 Support |
| 📋 Bewerbung | Fragen zu Bewerbungen | 📋 Bewerbungsteam |
| ⚠️ Spieler melden | Regelverstöße melden | 🔨 Moderation |
| 🐛 Bug melden | Fehler melden | 🔧 Administration |
| 💡 Vorschlag | Verbesserungen | 💼 Management |
| 🤝 Partnerschaft | Partner-Anfragen | 💼 Management |

Panel-Channel: `🎫・ticket-erstellen`

---

## 🔄 Ablauf

1. Mitglied klickt im Panel auf eine Kategorie
2. GalaxyBot erstellt einen Channel `ticket-<name>` in der Kategorie `🎫 TICKETS`
3. Nur Ersteller + Team sehen den Channel
4. Bei Abschluss: `🔒 Schließen` → archiviert in `🗄️ Ticket-Archiv` (nur Serverleitung)

---

## ⚙️ Einstellungen

- Ticket-Claim: Teammitglied kann sich ein Ticket zuweisen
- Transkript: wird beim Schließen im Log gespeichert
- Inaktivität: 48 h keine Antwort → automatischer Hinweis, 72 h → geschlossen
- Panel-Nachricht: siehe `04_panels/10_ticket-erstellen.json`
