"""
Emden RP Bot - Haupt-Einstiegspunkt.

Starten mit: python bot.py
Voraussetzung: .env Datei mit DISCORD_TOKEN=dein_token_hier
"""

import asyncio
import logging

import discord
from discord.ext import commands

import config
from database import init_db
from api_server import start_api_server

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("bot")

INTENTS = discord.Intents.default()
INTENTS.members = True          # WICHTIG: muss auch im Developer Portal aktiviert werden (Server Members Intent)
INTENTS.message_content = True  # nur falls du auch auf Text-Nachrichten reagieren willst


class EmdenRPBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=INTENTS)

    async def setup_hook(self):
        init_db()
        log.info("Datenbank initialisiert.")

        # Alle Cogs (Module) laden.
        #
        # WICHTIG: Dieser Bot ist jetzt der *Fraktions-Bot* (Polizei/Emden RP).
        # Übergreifende Systeme werden von anderen Bots übernommen (keine
        # Überschneidungen, siehe Master-Prompt §1):
        #   - Bewerbungen   → Appy            (siehe legacy-cogs/bewerbungen.py)
        #   - Tickets       → GalaxyBot       (siehe legacy-cogs/tickets.py)
        #   - Abmelden      → GalaxyBot       (siehe legacy-cogs/abmelden.py)
        # Die Original-Cogs liegen in legacy-cogs/ und werden nicht geladen.
        cogs = [
            "cogs.roblox",
            "cogs.teamliste",
            "cogs.dienst",
            "cogs.dienstberichte",
            "cogs.ausbildung",
            "cogs.gsg9",
            "cogs.gefahrenstatus",
            "cogs.fahndung",
            "cogs.funk",
        ]
        for cog in cogs:
            try:
                await self.load_extension(cog)
                log.info(f"Cog geladen: {cog}")
            except Exception as e:
                log.exception(f"Fehler beim Laden von {cog}: {e}")

        # Slash-Commands mit Discord synchronisieren
        synced = await self.tree.sync()
        log.info(f"{len(synced)} Slash-Commands synchronisiert.")

        # Eingebaute API starten, damit das Dashboard (ggf. auf einem anderen Server) Daten abrufen kann
        await start_api_server()

    async def on_ready(self):
        log.info(f"Eingeloggt als {self.user} (ID: {self.user.id})")
        log.info("Bot ist bereit.")


async def main():
    if not config.TOKEN:
        raise RuntimeError(
            "Kein DISCORD_TOKEN gefunden. Bitte eine .env Datei anlegen mit: DISCORD_TOKEN=dein_token"
        )
    bot = EmdenRPBot()
    async with bot:
        await bot.start(config.TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
