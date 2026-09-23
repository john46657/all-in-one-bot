"""
Teamliste: feste, automatisch aktualisierte Nachricht, Rangreihenfolge aus Discord-Rollen.
Zusätzlich: automatische Beförderungs-/Entlassungs-Nachrichten bei Rollenänderungen.
"""

from __future__ import annotations


import discord
from discord import app_commands
from discord.ext import commands

import config
from database import get_config, set_config, get_connection
from settings import get_setting


def rang_index(rollen_namen: set[str]) -> int:
    """Gibt den Index der höchsten Rang-Rolle in RANG_REIHENFOLGE zurück (0 = höchster Rang)."""
    for i, rang in enumerate(config.RANG_REIHENFOLGE):
        if rang in rollen_namen:
            return i
    return len(config.RANG_REIHENFOLGE)  # kein bekannter Rang -> ganz unten


def hoechster_rang(rollen_namen: set[str]) -> str | None:
    for rang in config.RANG_REIHENFOLGE:
        if rang in rollen_namen:
            return rang
    return None


class Teamliste(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _teamliste_channel(self, guild: discord.Guild):
        return discord.utils.get(guild.text_channels, name=get_setting("channel_teamliste"))

    async def build_embed(self, guild: discord.Guild) -> discord.Embed:
        embed = discord.Embed(title="📋 Teamliste - Emden RP", color=0x2c3e50)

        gruppiert: dict[str, list[discord.Member]] = {rang: [] for rang in config.RANG_REIHENFOLGE}
        for member in guild.members:
            if member.bot:
                continue
            rollen_namen = {r.name for r in member.roles}
            rang = hoechster_rang(rollen_namen)
            if rang:
                gruppiert[rang].append(member)

        gesamt = 0
        for rang in config.RANG_REIHENFOLGE:
            mitglieder = gruppiert[rang]
            if not mitglieder:
                continue
            gesamt += len(mitglieder)
            wert = "\n".join(f"• {m.mention}" for m in mitglieder)
            embed.add_field(name=f"{rang} ({len(mitglieder)})", value=wert, inline=False)

        embed.set_footer(text=f"Insgesamt {gesamt} Teammitglieder • wird automatisch aktualisiert")
        return embed

    async def update_teamliste(self, guild: discord.Guild):
        channel = await self._teamliste_channel(guild)
        if channel is None:
            return

        embed = await self.build_embed(guild)
        message_id = get_config(f"teamliste_message_id_{guild.id}")

        message = None
        if message_id:
            try:
                message = await channel.fetch_message(int(message_id))
            except (discord.NotFound, discord.HTTPException):
                message = None

        if message:
            await message.edit(embed=embed)
        else:
            new_message = await channel.send(embed=embed)
            set_config(f"teamliste_message_id_{guild.id}", new_message.id)

    @app_commands.command(name="teamliste_aktualisieren", description="Aktualisiert die Teamliste manuell")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def teamliste_aktualisieren(self, interaction: discord.Interaction):
        await self.update_teamliste(interaction.guild)
        await interaction.response.send_message("✅ Teamliste aktualisiert.", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.roles == after.roles:
            return

        vorher_rollen = {r.name for r in before.roles}
        nachher_rollen = {r.name for r in after.roles}

        vorher_rang = hoechster_rang(vorher_rollen)
        nachher_rang = hoechster_rang(nachher_rollen)

        # Teamliste immer aktualisieren, wenn sich rangrelevante Rollen ändern
        if vorher_rang != nachher_rang:
            await self.update_teamliste(after.guild)
            await self._befoerderung_oder_entlassung(after, vorher_rang, nachher_rang, vorher_rollen)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        # Falls jemand mit Rang-Rolle den Server verlässt -> Teamliste aktualisieren
        rollen_namen = {r.name for r in member.roles}
        if hoechster_rang(rollen_namen):
            await self.update_teamliste(member.guild)

    async def _befoerderung_oder_entlassung(
        self,
        member: discord.Member,
        vorher_rang: str | None,
        nachher_rang: str | None,
        vorher_rollen: set[str],
    ):
        guild = member.guild

        # Komplett entlassen: hatte einen Rang, hat jetzt keinen mehr
        if vorher_rang and not nachher_rang:
            channel = discord.utils.get(guild.text_channels, name=get_setting("channel_entlassungen"))
            if channel:
                embed = discord.Embed(
                    description=f"❌ {member.mention} wurde aus dem Polizeidienst entlassen.",
                    color=0xe74c3c,
                )
                embed.set_footer(text=f"Letzter Rang: {vorher_rang}")
                await channel.send(embed=embed)
            return

        # Neuer Rang vergeben (auch für neue Mitglieder ohne vorherigen Rang)
        if nachher_rang and nachher_rang != vorher_rang:
            vorher_idx = rang_index(vorher_rollen) if vorher_rang else len(config.RANG_REIHENFOLGE)
            nachher_idx = config.RANG_REIHENFOLGE.index(nachher_rang)

            channel = discord.utils.get(guild.text_channels, name=get_setting("channel_befoerderungen"))
            if channel is None:
                return

            if nachher_idx < vorher_idx:
                # niedrigerer Index = höherer Rang in der Liste -> Beförderung
                text = f"🎉 {member.mention} wurde"
                if vorher_rang:
                    text += f" von *{vorher_rang}* zu *{nachher_rang}* befördert!"
                else:
                    text += f" zum Rang *{nachher_rang}* ernannt!"
                embed = discord.Embed(description=text, color=0xf1c40f)
            else:
                # höherer Index = niedrigerer Rang -> Degradierung
                embed = discord.Embed(
                    description=f"⬇️ {member.mention} wurde von *{vorher_rang}* zu *{nachher_rang}* degradiert.",
                    color=0x95a5a6,
                )
            await channel.send(embed=embed)


    @app_commands.command(
        name="entlassen_roblox",
        description="Entlässt jemanden per Roblox-Namen aus dem Team (auch wenn nicht mehr im Discord)",
    )
    @app_commands.describe(roblox_name="Roblox-Benutzername der Person", grund="Grund der Entlassung (optional)")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def entlassen_roblox(self, interaction: discord.Interaction, roblox_name: str, grund: str = None):
        conn = get_connection()
        row = conn.execute(
            "SELECT user_id, letzter_discord_name FROM roblox_verknuepfungen WHERE LOWER(roblox_name) = LOWER(?)",
            (roblox_name.lstrip("@"),),
        ).fetchone()
        conn.close()

        if not row:
            await interaction.response.send_message(
                f"Kein Discord-User mit dem Roblox-Namen **@{roblox_name.lstrip('@')}** verknüpft. "
                "Erst mit `/roblox verknuepfen` verknüpfen.",
                ephemeral=True,
            )
            return

        guild = interaction.guild
        member = guild.get_member(row["user_id"])
        letzter_rang = None

        if member:
            rollen_namen = {r.name for r in member.roles}
            letzter_rang = hoechster_rang(rollen_namen)
            rang_rollen = [r for r in member.roles if r.name in config.RANG_REIHENFOLGE]
            if rang_rollen:
                await member.remove_roles(*rang_rollen, reason=f"Entlassung (Roblox) durch {interaction.user}")

        channel = discord.utils.get(guild.text_channels, name=get_setting("channel_entlassungen"))
        if channel:
            wer = member.mention if member else f"`{row['letzter_discord_name']}`"
            beschreibung = f"❌ **@{roblox_name.lstrip('@')}** ({wer}) wurde aus dem Polizeidienst entlassen."
            if grund:
                beschreibung += f"\nGrund: {grund}"
            embed = discord.Embed(description=beschreibung, color=0xe74c3c)
            if letzter_rang:
                embed.set_footer(text=f"Letzter Rang: {letzter_rang}")
            elif not member:
                embed.set_footer(text="Person war beim Entlassen nicht mehr auf dem Server")
            await channel.send(embed=embed)

        if member:
            await self.update_teamliste(guild)

        await interaction.response.send_message(
            f"✅ **@{roblox_name.lstrip('@')}** wurde entlassen."
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Teamliste(bot))
