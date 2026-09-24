"""
Server-Setup-Skript – legt die komplette Struktur aus dem Master-Prompt an.

Rollen (inkl. Hierarchie), Kategorien, Channels und Berechtigungen werden
1:1 aus setup/struktur.py erstellt. Das Skript ist idempotent: bereits
vorhandene Rollen/Channels werden übersprungen, sodass es gefahrlos mehrfach
ausgeführt werden kann.

Aufruf:
    python setup_server.py --guild-id 123456789          # anwenden
    python setup_server.py --guild-id 123456789 --dry-run  # nur Plan anzeigen

Voraussetzung: .env neben diesem Skript (oder galaxy-bot/.env) mit
    DISCORD_TOKEN=dein_token
Der Bot braucht auf dem Server: Manage Roles + Manage Channels (Administrator
empfohlen, aber nicht nötig). Die Bot-Rolle muss in der Hierarchie über den
Rollen stehen, die sie verwalten soll.
"""

import argparse
import asyncio
import logging
import os
import sys

import discord
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from struktur import ROLLEN, TEAM_ROLLEN, LOG_ROLLEN, kategorien  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("setup")

PERMISSION_FLAGS = {
    "administrator": "administrator",
    "manage_guild": "manage_guild",
    "manage_roles": "manage_roles",
    "manage_channels": "manage_channels",
    "manage_messages": "manage_messages",
    "moderate_members": "moderate_members",
    "kick_members": "kick_members",
    "ban_members": "ban_members",
    "view_audit_log": "view_audit_log",
}


def lade_token() -> str | None:
    """Token aus .env im setup/-Ordner, galaxy-bot/ oder Umgebungsvariablen."""
    hier = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    galaxy = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "galaxy-bot", ".env")
    for pfad in (hier, galaxy):
        if os.path.exists(pfad):
            load_dotenv(pfad)
    return os.getenv("DISCORD_TOKEN")


def rolle_vorhanden(guild: discord.Guild, name: str) -> discord.Role | None:
    return discord.utils.get(guild.roles, name=name)


def kategorie_vorhanden(guild: discord.Guild, name: str) -> discord.CategoryChannel | None:
    return discord.utils.get(guild.categories, name=name)


def channel_vorhanden(kategorie: discord.CategoryChannel, name: str):
    return discord.utils.get(kategorie.text_channels, name=name) or \
           discord.utils.get(kategorie.voice_channels, name=name)


def overwrites_fuer(guild: discord.Guild, kat: dict) -> dict:
    """Baut die Permission-Overwrites für eine Kategorie."""
    overwrites = {}
    sichtbar = kat["sichtbar"]
    schreiben = kat["schreiben"]

    # @everyone: Standard
    overwrites[guild.default_role] = discord.PermissionOverwrite(view_channel=(sichtbar == "alle"))

    def rolle_holen(name):
        return rolle_vorhanden(guild, name)

    if sichtbar == "team":
        for name in TEAM_ROLLEN:
            rolle = rolle_holen(name)
            if rolle:
                overwrites[rolle] = discord.PermissionOverwrite(view_channel=True)
    elif sichtbar == "logs":
        for name in LOG_ROLLEN:
            rolle = rolle_holen(name)
            if rolle:
                overwrites[rolle] = discord.PermissionOverwrite(view_channel=True)
    elif sichtbar.startswith("fraktion:"):
        rollenname = sichtbar.split(":", 1)[1]
        rolle = rolle_holen(rollenname)
        if rolle:
            overwrites[rolle] = discord.PermissionOverwrite(view_channel=True)
        # Fraktionsverwaltung sieht alle Fraktionsbereiche
        fv = rolle_holen("🎭 Fraktionsverwaltung")
        if fv:
            overwrites[fv] = discord.PermissionOverwrite(view_channel=True)

    # Schreibrechte
    if schreiben == "alle":
        overwrites[guild.default_role].send_messages = True
        overwrites[guild.default_role].read_message_history = True
    elif schreiben == "team":
        for name in TEAM_ROLLEN:
            rolle = rolle_holen(name)
            if rolle:
                if rolle not in overwrites:
                    overwrites[rolle] = discord.PermissionOverwrite(view_channel=True)
                overwrites[rolle].send_messages = True
                overwrites[rolle].read_message_history = True
    elif schreiben == "logs":
        for name in LOG_ROLLEN:
            rolle = rolle_holen(name)
            if rolle:
                if rolle not in overwrites:
                    overwrites[rolle] = discord.PermissionOverwrite(view_channel=True)
                overwrites[rolle].send_messages = True
                overwrites[rolle].read_message_history = True
    elif schreiben == "fraktion":
        for rolle in list(overwrites.keys()):
            if rolle != guild.default_role and rolle.name != "🎭 Fraktionsverwaltung" \
                    and not rolle.name.startswith("🤖"):
                # Fraktionsrolle selbst (view wurde oben gesetzt)
                pass
        # Allen sichtbaren Rollen Schreibrechte geben
        for rolle in list(overwrites.keys()):
            if rolle != guild.default_role:
                overwrites[rolle].send_messages = True
                overwrites[rolle].read_message_history = True

    # Bots dürfen (fast) alles sehen – sie brauchen ihre Channels
    bots = rolle_vorhanden(guild, "🤖 Bots")
    if bots:
        overwrites[bots] = discord.PermissionOverwrite(
            view_channel=True, send_messages=True, read_message_history=True
        )

    return overwrites


async def rollen_anlegen(guild: discord.Guild, dry_run: bool) -> list[discord.Role]:
    log.info("=== PHASE 1: Rollen ===")
    angelegt = 0
    for name, farbe, flags in ROLLEN:
        if rolle_vorhanden(guild, name):
            log.info("Rolle existiert bereits: %s", name)
            continue
        if dry_run:
            log.info("[DRY-RUN] Rolle würde angelegt: %s (Farbe #%06X, Rechte: %s)",
                     name, farbe, ", ".join(flags) or "keine")
            angelegt += 1
            continue
        permissions = discord.Permissions(**{PERMISSION_FLAGS[f]: True for f in flags})
        farbe_wert = discord.Color(farbe) if farbe else discord.Color.default()
        await guild.create_role(name=name, color=farbe_wert, permissions=permissions,
                                reason="Setup-Skript")
        log.info("Rolle angelegt: %s", name)
        angelegt += 1
    log.info("Rollen: %s angelegt / %s insgesamt", angelegt, len(ROLLEN))

    # Hierarchie korrigieren: Reihenfolge aus struktur.py (oben = höchste Rechte)
    if dry_run:
        log.info("[DRY-RUN] Hierarchie würde auf die Reihenfolge aus struktur.py gesetzt.")
        return []
    positions = {}
    gewuenscht = [name for name, _, _ in ROLLEN]
    for i, name in enumerate(gewuenscht):
        rolle = rolle_vorhanden(guild, name)
        if rolle:
            positions[rolle] = len(gewuenscht) - i
    if positions:
        await guild.edit_role_positions(positions, reason="Setup-Skript: Hierarchie")
        log.info("Rollen-Hierarchie gesetzt (Top: %s).", gewuenscht[0])
    return [r for r in (rolle_vorhanden(guild, n) for n, _, _ in ROLLEN) if r]


async def kategorien_anlegen(guild: discord.Guild, dry_run: bool):
    log.info("=== PHASE 2: Kategorien & Channels ===")
    kategorie_liste = kategorien()
    angelegt_kat = angelegt_ch = 0

    for kat in kategorie_liste:
        overwrites = overwrites_fuer(guild, kat) if not dry_run else {}
        kategorie = kategorie_vorhanden(guild, kat["name"])
        if kategorie is None:
            if dry_run:
                log.info("[DRY-RUN] Kategorie würde angelegt: %s (%d Channels, sichtbar: %s)",
                         kat["name"], len(kat["channels"]), kat["sichtbar"])
                angelegt_kat += 1
                for ch_name, _ in kat["channels"]:
                    log.info("[DRY-RUN]   -> Channel: %s", ch_name)
                    angelegt_ch += 1
                continue
            kategorie = await guild.create_category(kat["name"], overwrites=overwrites,
                                                    reason="Setup-Skript")
            log.info("Kategorie angelegt: %s", kat["name"])
            angelegt_kat += 1
        else:
            if not dry_run:
                await kategorie.edit(overwrites=overwrites, reason="Setup-Skript: Overwrites")
                log.info("Kategorie Overwrites aktualisiert: %s", kat["name"])

        for ch_name, ch_typ in kat["channels"]:
            if channel_vorhanden(kategorie, ch_name):
                continue
            if dry_run:
                log.info("[DRY-RUN]   Channel würde angelegt: %s (%s)", ch_name, ch_typ)
                angelegt_ch += 1
                continue
            if ch_typ == "voice":
                await kategorie.create_voice_channel(ch_name, reason="Setup-Skript")
            else:
                await kategorie.create_text_channel(ch_name, reason="Setup-Skript")
            log.info("Channel angelegt: %s -> %s", kat["name"], ch_name)
            angelegt_ch += 1

    log.info("Kategorien: %s, Channels: %s", angelegt_kat, angelegt_ch)


async def main():
    parser = argparse.ArgumentParser(description="Legt die Serverstruktur aus dem Master-Prompt an.")
    parser.add_argument("--guild-id", required=True, help="ID des Discord-Servers")
    parser.add_argument("--dry-run", action="store_true",
                        help="Nur anzeigen, was angelegt würde (keine Änderungen)")
    parser.add_argument("--token", default=None, help="Bot-Token (alternativ DISCORD_TOKEN in .env)")
    args = parser.parse_args()

    token = args.token or lade_token()

    if args.dry_run:
        # Dry-Run braucht keinen Token – nur die Struktur zeigen
        log.info("=== DRY-RUN (keine Verbindung zu Discord) ===")
        for kat in kategorien():
            log.info("Kategorie: %s  [sichtbar: %s, schreiben: %s]",
                     kat["name"], kat["sichtbar"], kat["schreiben"])
            for ch_name, ch_typ in kat["channels"]:
                log.info("    %s (%s)", ch_name, ch_typ)
        log.info("=== Ende des Plans: %d Kategorien, %d Rollen ===",
                 len(kategorien()), len(ROLLEN))
        return

    if not token:
        raise SystemExit(
            "Kein DISCORD_TOKEN gefunden. Bitte .env anlegen (DISCORD_TOKEN=...) "
            "oder --token übergeben."
        )

    intents = discord.Intents.default()
    intents.guilds = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        guild = client.get_guild(int(args.guild_id))
        if guild is None:
            raise SystemExit(f"Server mit ID {args.guild_id} nicht gefunden. "
                             f"Der Bot muss auf dem Server sein.")
        log.info("Verbunden als %s mit Server '%s'", client.user, guild.name)
        await rollen_anlegen(guild, dry_run=False)
        await kategorien_anlegen(guild, dry_run=False)
        log.info("=== Setup abgeschlossen! ===")
        log.info("Nächste Schritte: Bots einladen (Wick → GalaxyBot → …), "
                 "dann /abwesenheit panel, /ticket panel und /vorschlag panel ausführen.")
        await client.close()

    try:
        await client.start(token)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
