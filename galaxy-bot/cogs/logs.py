"""
Log-System: protokolliert alle relevanten Server-Ereignisse.

Ereignisse:
- Member Join/Leave          → 👤・member-logs
- Rollenänderungen           → 🎭・role-logs
- Nachrichtenlöschung/-änderung → 💬・message-logs
- Voice Join/Leave/Mute      → 🎙️・voice-logs
- Bot-Aktivität (ready)      → 🤖・bot-logs

Moderations-Logs (warn/timeout/kick/ban, AutoMod) werden direkt von den
jeweiligen Cogs geschrieben (siehe logging_utils.py).
"""

import datetime
import logging

import discord
from discord.ext import commands

import config
from logging_utils import log_member, log_role, log_message, log_voice, log_bot

log = logging.getLogger("galaxy.logs")

# Nachrichten-Cache: für Lösch-Logs brauchen wir den Inhalt vor der Löschung
_nachrichten_cache: dict[int, tuple[str, discord.Member]] = {}
_CACHE_MAX = 500


class Logs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        if not self.bot.guilds:
            return
        await log_bot(
            self.bot.guilds[0],
            title="🤖 GalaxyBot gestartet",
            description=f"Eingeloggt als **{self.bot.user}** (`{self.bot.user.id}`)",
        )

    # --- Member ------------------------------------------------------------

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await log_member(
            member.guild,
            title="👋 Mitglied beigetreten",
            description=f"{member.mention} (`{member.id}`)",
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await log_member(
            member.guild,
            title="👋 Mitglied verlassen",
            description=f"**{member}** (`{member.id}`)",
        )

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        before_ids = {r.id for r in before.roles}
        after_ids = {r.id for r in after.roles}
        hinzugefuegt = [r for r in after.roles if r.id not in before_ids]
        entfernt = [r for r in before.roles if r.id not in after_ids]
        if not hinzugefuegt and not entfernt:
            return

        felder = []
        if hinzugefuegt:
            felder.append(("Hinzugefügt", ", ".join(r.name for r in hinzugefuegt), False))
        if entfernt:
            felder.append(("Entfernt", ", ".join(r.name for r in entfernt), False))
        await log_role(
            after.guild,
            title="🎭 Rollen geändert",
            description=f"**{after}** (`{after.id}`)",
            fields=felder,
        )

    # --- Rollen (Server-Ebene) ---------------------------------------------

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        await log_role(role.guild, title="🎭 Rolle erstellt", description=f"**{role.name}** (`{role.id}`)")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        await log_role(role.guild, title="🎭 Rolle gelöscht", description=f"**{role.name}** (`{role.id}`)")

    # --- Nachrichten -------------------------------------------------------

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None or message.author.bot:
            return
        _nachrichten_cache[message.id] = (message.content, message.author)
        # Cache begrenzen
        if len(_nachrichten_cache) > _CACHE_MAX:
            aelteste = next(iter(_nachrichten_cache))
            _nachrichten_cache.pop(aelteste, None)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.guild is None or message.author.bot:
            return
        inhalt, autor = _nachrichten_cache.pop(message.id, (None, None))
        await log_message(
            message.guild,
            title="🗑️ Nachricht gelöscht",
            description=f"**{autor or message.author}** in {message.channel.mention}",
            fields=[("Inhalt", (inhalt or message.content or "*kein Text*")[:1024], False)],
        )

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.guild is None or before.author.bot:
            return
        if before.content == after.content:
            return  # z. B. nur Embed hinzugefügt
        await log_message(
            before.guild,
            title="✏️ Nachricht bearbeitet",
            description=f"**{before.author}** in {before.channel.mention}",
            fields=[
                ("Vorher", (before.content or "*kein Text*")[:1024], False),
                ("Nachher", (after.content or "*kein Text*")[:1024], False),
            ],
        )

    # --- Voice -------------------------------------------------------------

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if before.channel == after.channel:
            return

        if before.channel is None and after.channel is not None:
            await log_voice(
                member.guild,
                title="🎙️ Voice beigetreten",
                description=f"**{member}** → `{after.channel.name}`",
            )
        elif before.channel is not None and after.channel is None:
            await log_voice(
                member.guild,
                title="🎙️ Voice verlassen",
                description=f"**{member}** ← `{before.channel.name}`",
            )
        else:
            await log_voice(
                member.guild,
                title="🎙️ Voice gewechselt",
                description=f"**{member}**: `{before.channel.name}` → `{after.channel.name}`",
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Logs(bot))
