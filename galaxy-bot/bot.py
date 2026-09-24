"""
GalaxyBot - zentraler Server-Bot.

Starten mit: python bot.py
Voraussetzung: .env Datei mit DISCORD_TOKEN=dein_token_hier

Der Bot ist modular aufgebaut: jedes Feature ist eine eigene Cog in cogs/.
Fehlt eine Cog (z. B. weil ein Channel noch nicht existiert), startet der
Bot trotzdem und loggt nur eine Warnung.
"""

import asyncio
import logging

import discord
from discord.ext import commands

import config
from database import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("galaxy")

INTENTS = discord.Intents.default()
INTENTS.members = True          # WICHTIG: im Developer Portal aktivieren (Server Members Intent)
INTENTS.message_content = True  # für AutoMod benötigt (Message Content Intent)


class GalaxyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=INTENTS)

    async def setup_hook(self):
        init_db()
        log.info("Datenbank initialisiert.")

        cogs = [
            "cogs.welcome",
            "cogs.moderation",
            "cogs.automod",
            "cogs.tickets",
            "cogs.suggestions",
            "cogs.absence",
            "cogs.logs",
        ]
        for cog in cogs:
            try:
                await self.load_extension(cog)
                log.info("Cog geladen: %s", cog)
            except Exception as e:
                log.exception("Fehler beim Laden von %s: %s", cog, e)

        try:
            synced = await self.tree.sync()
            log.info("%s Slash-Commands synchronisiert.", len(synced))
        except Exception as e:
            log.exception("Fehler beim Synchronisieren der Slash-Commands: %s", e)

    async def on_ready(self):
        log.info("Eingeloggt als %s (ID: %s)", self.user, self.user.id)
        log.info("GalaxyBot ist bereit. Verbunden mit %s Server(n).", len(self.guilds))


async def main():
    if not config.TOKEN:
        raise RuntimeError(
            "Kein DISCORD_TOKEN gefunden. Bitte eine .env Datei anlegen mit: "
            "DISCORD_TOKEN=dein_token"
        )
    bot = GalaxyBot()
    async with bot:
        await bot.start(config.TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
