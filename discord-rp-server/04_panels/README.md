# 🎨 Panels (Discohook) – Übersicht

Webhook-JSON-Dateien, kompatibel mit **Discohook**, **hook.gg** und Discord-Webhooks direkt.

## Verwendung

1. In Discord: Channel bearbeiten → **Integrationen** → **Webhook erstellen**
2. Webhook-URL kopieren
3. Auf [discohook.org](https://discohook.org) → **Webhook** → URL einfügen
4. JSON aus dieser Datei in den "JSON laden"-Bereich einfügen (oder Felder manuell übernehmen)
5. **Senden**

Einheitliches Design: Farbe `#5865F2`, Footer `🌌 NovaRP • Community & Roleplay`.

## Dateien

| Datei | Panel | Channel |
|---|---|---|
| `01_willkommen.json` | 👋 Willkommen | 👋・willkommen |
| `02_regeln.json` | 📜 Regeln (13 Regeln) | 📜・regeln |
| `03_server-informationen.json` | 📋 Serverinfo | 📋・server-informationen |
| `04_faq.json` | ❓ FAQ | ❓・faq |
| `05_links.json` | 🔗 Links | 🔗・links |
| `06_rp-informationen.json` | 🎭 RP-Infos | 🎭・rp-informationen |
| `07_rp-regeln.json` | 📖 RP-Regeln | 📖・rp-regeln |
| `08_fraktionen.json` | 💼 Fraktionen | 💼・fraktionen |
| `09_bewerbungen.json` | 📋 Bewerbungen (Select-Menü, 10 Bereiche) | 📋・bewerbungen |
| `10_ticket-erstellen.json` | 🎫 Tickets (Select-Menü, 6 Kategorien) | 🎫・ticket-erstellen |
| `11_economy-info.json` | 💰 Economy-Info | 💰・economy-info |
| `12_vorschlaege.json` | 💡 Vorschläge | 💡・vorschläge |
| `13_abmelden.json` | 🚪 Team-Abmeldung | 🚪・abmeldungen |

## ⚠️ Vor dem Posten

- `<#REGELN>` etc. durch echte Channel-Mentions ersetzen (Channel-ID: `<#123456...>`)
- Platzhalter-Links in `05_links.json` durch echte ersetzen
- Footer-Text `NovaRP` durch euren Servernamen ersetzen
- Timestamp-Feld kann entfernt werden (sonst immer "heute" vorgetäuscht)

## 🎛️ Interaktive Panels

`09_bewerbungen.json` und `10_ticket-erstellen.json` enthalten Select-Menü-Komponenten.
Discos Hook kann diese **anzeigen**, aber die Interaktion muss von einem Bot verarbeitet werden:
- Bewerbungen → **Appy** (custom_id `appy_application_select`)
- Tickets → **GalaxyBot** (custom_id `galaxy_ticket_select`)

Falls Appy/GalaxyBot diese IDs nicht unterstützen: Select-Menü im Bot- eigenen Format nachbauen und nur das Embed über Discohook posten.
