"""
Zentrale Logging-Helfer für GalaxyBot.

Alle Log-Einträge laufen hier zusammen, damit jede Cog dieselben Farben und
Channels nutzt. Channels werden über settings.py aufgelöst (DB-Override oder
config.py-Standard).
"""

import logging

import discord

import config
from settings import get_setting

log = logging.getLogger("galaxy.logging")


def _finde_channel(guild: discord.Guild, name: str) -> discord.TextChannel | None:
    """Findet einen Text-Channel per Name. Zurückgefallen wird auf None."""
    if not name:
        return None
    channel = discord.utils.get(guild.text_channels, name=name)
    if channel is None:
        log.warning("Log-Channel nicht gefunden: %s", name)
    return channel


async def _log(
    guild: discord.Guild,
    channel_key: str,
    *,
    title: str,
    description: str = "",
    farbe: int = config.FARBE_INFO,
    fields: list[tuple[str, str, bool]] | None = None,
    footer: str = "",
):
    """Schreibt einen Embed in den Log-Channel hinter `channel_key`."""
    channel = _finde_channel(guild, get_setting(channel_key))
    if channel is None:
        return
    embed = discord.Embed(title=title, description=description, color=farbe)
    for name, value, inline in (fields or []):
        embed.add_field(name=name, value=value, inline=inline)
    embed.set_footer(text=footer or "GalaxyBot Logging")
    embed.timestamp = discord.utils.utcnow()
    try:
        await channel.send(embed=embed)
    except discord.Forbidden:
        log.warning("Keine Rechte für Log-Channel %s", channel.name)


# --- Konkrete Logger -------------------------------------------------------

async def log_member(guild, *, title, description="", fields=None):
    await _log(guild, "channel_member_logs", title=title, description=description,
               farbe=config.FARBE_INFO, fields=fields)


async def log_mod(guild, *, title, description="", fields=None):
    await _log(guild, "channel_mod_logs", title=title, description=description,
               farbe=config.FARBE_INFO, fields=fields)


async def log_punishment(guild, *, title, description="", fields=None):
    await _log(guild, "channel_punishment_logs", title=title, description=description,
               farbe=config.FARBE_FEHLER, fields=fields)


async def log_role(guild, *, title, description="", fields=None):
    await _log(guild, "channel_role_logs", title=title, description=description,
               farbe=config.STATUS_FARBEN["🟣"], fields=fields)


async def log_message(guild, *, title, description="", fields=None):
    await _log(guild, "channel_message_logs", title=title, description=description,
               farbe=config.FARBE_WARNUNG, fields=fields)


async def log_voice(guild, *, title, description="", fields=None):
    await _log(guild, "channel_voice_logs", title=title, description=description,
               farbe=config.FARBE_INFO, fields=fields)


async def log_bot(guild, *, title, description="", fields=None):
    await _log(guild, "channel_bot_logs", title=title, description=description,
               farbe=config.FARBE_INFO, fields=fields)


async def log_abwesenheit(guild, *, title, description="", fields=None, farbe=None):
    await _log(guild, "channel_abwesenheits_logs", title=title, description=description,
               farbe=farbe or config.FARBE_INFO, fields=fields)
