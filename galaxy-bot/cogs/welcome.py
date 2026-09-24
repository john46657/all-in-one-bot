"""
Welcome-System.

- Neue Mitglieder erhalten die Rolle "🆕 Neuer Bürger" (konfigurierbar).
- Willkommensnachricht im Willkommens-Channel (Text konfigurierbar).
- Join/Leave werden in den Member-Logs protokolliert.
"""

import logging

import discord
from discord.ext import commands

import config
import server_config as sc
from logging_utils import log_member

log = logging.getLogger("galaxy.welcome")


class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _rolle(self, guild: discord.Guild, key: str) -> discord.Role | None:
        name = sc.rolle(key)
        rolle = discord.utils.get(guild.roles, name=name)
        if rolle is None:
            log.warning("Rolle nicht gefunden: %s", name)
        return rolle

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild

        # Neuer-Bürger-Rolle vergeben
        rolle = await self._rolle(guild, "neuer_buerger")
        if rolle:
            try:
                await member.add_roles(rolle, reason="Neues Mitglied beigetreten")
            except discord.Forbidden:
                log.warning("Keine Rechte, %s zu vergeben.", rolle.name)

        # Willkommensnachricht
        channel = discord.utils.get(guild.text_channels, name=sc.channel("willkommen"))
        if channel:
            embed = discord.Embed(
                title=f"👋 Willkommen, {member.display_name}!",
                description=sc.wert("willkommen", "text") or config.WILLKOMMENS_TEXT,
                color=sc.farbe("info"),
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"{member.guild.member_count} Mitglieder")
            try:
                await channel.send(content=member.mention, embed=embed)
            except discord.Forbidden:
                log.warning("Keine Rechte im Willkommens-Channel.")

        await log_member(
            guild,
            title="👋 Mitglied beigetreten",
            description=f"{member.mention} (`{member.id}`)",
            fields=[("Account erstellt", discord.utils.format_dt(member.created_at, "R"), True)],
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await log_member(
            member.guild,
            title="👋 Mitglied verlassen",
            description=f"**{member}** (`{member.id}`)",
            fields=[("Rollen", ", ".join(r.name for r in member.roles if not r.is_default()) or "–", False)],
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))
