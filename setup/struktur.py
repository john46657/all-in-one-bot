"""
Serverstruktur für das Setup-Skript.

Alle Rollen, Kategorien und Channels aus dem Master-Prompt, zentral an einer
Stelle, damit setup_server.py und Doku immer synchron sind.
"""

# ---------------------------------------------------------------------------
# Rollen: (Name, Farbe als Hex-Int, Discord-Permissions oder None)
# Reihenfolge = gewünschte Hierarchie von oben (höchste Rechte) nach unten.
# ---------------------------------------------------------------------------
ROLLEN = [
    # --- Team ---
    ("🤖 Bots", 0x99AAB5, []),
    ("👑 Serverleitung", 0xFFD700, ["administrator"]),
    ("🛡️ Stellvertretende Serverleitung", 0xFF8C00, ["administrator"]),
    ("💼 Management", 0x9B59B6, ["manage_guild", "manage_roles", "manage_channels",
                                 "manage_messages", "view_audit_log"]),
    ("🔧 Administration", 0xE91E63, ["moderate_members", "kick_members", "ban_members",
                                     "manage_messages", "view_audit_log"]),
    ("🔨 Moderation", 0x3498DB, ["moderate_members", "manage_messages", "view_audit_log"]),
    ("🎫 Support", 0x1ABC9C, ["view_audit_log"]),
    ("📋 Bewerbungsteam", 0xF1C40F, []),
    ("🎭 Fraktionsverwaltung", 0x2ECC71, ["manage_channels"]),
    ("🎮 Event-Team", 0xE67E22, []),
    ("📢 Social-Media-Team", 0xFF69B4, []),
    ("🎥 Content Creator", 0x00B0F4, []),
    # --- Community ---
    ("💎 Booster", 0xF47FFF, []),
    ("⭐ VIP", 0xFFD700, []),
    ("👤 Mitglied", 0x5865F2, []),
    ("🆕 Neuer Bürger", 0x95A5A6, []),
    # --- RP-Fraktionen ---
    ("👮 Polizei", 0x0044CC, []),
    ("🚒 Feuerwehr", 0xCC3300, []),
    ("🚑 Rettungsdienst", 0xFF0000, []),
    ("⚖️ Justiz", 0x8B0000, []),
    ("🏛️ Regierung", 0xFFD700, []),
    ("💼 Unternehmen", 0x2ECC71, []),
    # --- Abwesenheit ---
    ("💤 Abwesend", 0x95A5A6, []),
]

# Team-Rollen (für Berechtigungen in TEAM/LOGS-Kategorien)
TEAM_ROLLEN = [
    "👑 Serverleitung", "🛡️ Stellvertretende Serverleitung", "💼 Management",
    "🔧 Administration", "🔨 Moderation", "🎫 Support", "📋 Bewerbungsteam",
    "🎭 Fraktionsverwaltung", "🎮 Event-Team", "📢 Social-Media-Team", "🎥 Content Creator",
]

# Rollen, die Logs sehen dürfen (Master-Prompt: Serverleitung + Administration)
LOG_ROLLEN = ["👑 Serverleitung", "🛡️ Stellvertretende Serverleitung",
              "💼 Management", "🔧 Administration"]

# ---------------------------------------------------------------------------
# Kategorien & Channels
# sichtbar: "alle" | "team" | "logs" | "fraktion:<rollenname>"
# schreiben: "alle" | "team"
# ---------------------------------------------------------------------------

_KATEGORIEN = [
    {
        "name": "📌 START",
        "sichtbar": "alle", "schreiben": "team",
        "channels": [
            ("👋・willkommen", "text"), ("📜・regeln", "text"),
            ("📢・ankündigungen", "text"), ("📋・server-informationen", "text"),
            ("🆕・changelog", "text"), ("❓・faq", "text"), ("🔗・links", "text"),
        ],
    },
    {
        "name": "🎭 ROLEPLAY",
        "sichtbar": "alle", "schreiben": "team",
        "channels": [
            ("🎭・rp-informationen", "text"), ("📖・rp-regeln", "text"),
            ("📝・charakter-erstellung", "text"), ("📰・rp-news", "text"),
            ("📅・rp-events", "text"), ("💼・fraktionen", "text"),
            ("🏠・immobilien", "text"), ("🚗・fahrzeuge", "text"),
        ],
    },
    {
        "name": "📋 BEWERBUNGEN",
        "sichtbar": "alle", "schreiben": "team",
        "channels": [
            ("📋・bewerbungen", "text"), ("📥・bewerbungs-status", "text"),
            ("📊・bewerbungs-info", "text"),
        ],
    },
    {
        "name": "💰 ECONOMY",
        "sichtbar": "alle", "schreiben": "team",
        "channels": [
            ("💰・economy-info", "text"), ("💼・jobs", "text"),
            ("🏪・shop", "text"), ("💸・überweisungen", "text"),
            ("🏆・economy-ranking", "text"),
        ],
    },
    {
        "name": "💬 COMMUNITY",
        "sichtbar": "alle", "schreiben": "alle",
        "channels": [
            ("💬・allgemein", "text"), ("😂・memes", "text"),
            ("📸・bilder", "text"), ("🎮・gaming", "text"),
            ("🎵・musik", "text"), ("💡・vorschläge", "text"),
            ("🗳️・umfragen", "text"), ("🎁・giveaways", "text"),
        ],
    },
    {
        "name": "🎫 SUPPORT",
        "sichtbar": "alle", "schreiben": "team",
        "channels": [
            ("🎫・ticket-erstellen", "text"), ("🆘・support", "text"),
            ("⚠️・spieler-meldung", "text"), ("🐛・bug-meldung", "text"),
            ("💡・vorschlag", "text"),
        ],
    },
    {
        "name": "👮 FRAKTIONEN",
        "sichtbar": "alle", "schreiben": "team",
        "channels": [
            ("👮・polizei", "text"), ("🚒・feuerwehr", "text"),
            ("🚑・rettungsdienst", "text"), ("⚖️・justiz", "text"),
            ("🏛️・regierung", "text"), ("💼・unternehmen", "text"),
        ],
    },
    {
        "name": "🔊 VOICE",
        "sichtbar": "alle", "schreiben": "alle",
        "channels": [
            ("🔊・Lobby", "voice"), ("🎮・Gaming", "voice"),
            ("💬・Talk", "voice"), ("🎵・Musik", "voice"),
            ("➕・Raum-erstellen", "voice"),
        ],
    },
    {
        "name": "🔐 TEAM",
        "sichtbar": "team", "schreiben": "team",
        "channels": [
            ("💬・team-chat", "text"), ("📢・team-news", "text"),
            ("📋・team-aufgaben", "text"), ("📋・bewerbungen-team", "text"),
            ("📅・team-abwesenheit", "text"), ("📅・abwesenheitsübersicht", "text"),
            ("⚠️・verwarnungen", "text"), ("📁・team-dokumente", "text"),
            ("🔊・team-besprechung", "voice"),
        ],
    },
    {
        "name": "📊 LOGS",
        "sichtbar": "logs", "schreiben": "logs",
        "channels": [
            ("📜・mod-logs", "text"), ("👤・member-logs", "text"),
            ("🔨・punishment-logs", "text"), ("🎭・role-logs", "text"),
            ("💬・message-logs", "text"), ("🎙️・voice-logs", "text"),
            ("🤖・bot-logs", "text"), ("📋・bewerbungs-logs", "text"),
            ("💰・economy-logs", "text"), ("💤・abwesenheits-logs", "text"),
        ],
    },
]

# Private Fraktionsbereiche (Master-Prompt: je Fraktion 5 Channels)
FRAKTION_CHANNEL_TEMPLATE = [
    ("📢・dienst-news", "text"),
    ("💬・dienst-chat", "text"),
    ("📋・dienstplan", "text"),
    ("📁・dokumente", "text"),
    ("🎙️・besprechung", "voice"),
]

FRAKTIONEN = [
    ("👮 POLIZEI", "👮 Polizei"),
    ("🚒 FEUERWEHR", "🚒 Feuerwehr"),
    ("🚑 RETTUNGSDIENST", "🚑 Rettungsdienst"),
    ("⚖️ JUSTIZ", "⚖️ Justiz"),
    ("🏛️ REGIERUNG", "🏛️ Regierung"),
    ("💼 UNTERNEHMEN", "💼 Unternehmen"),
]


def kategorien() -> list[dict]:
    """Liefert die komplette Kategorien-Liste inkl. privater Fraktionsbereiche."""
    ergebnis = list(_KATEGORIEN)
    for kategoriename, rollenname in FRAKTIONEN:
        ergebnis.append({
            "name": kategoriename,
            "sichtbar": f"fraktion:{rollenname}",
            "schreiben": "fraktion",
            "channels": list(FRAKTION_CHANNEL_TEMPLATE),
        })
    return ergebnis
