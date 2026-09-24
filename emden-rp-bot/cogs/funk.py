"""
Funk-Whitelist: Nur wer auf der Whitelist steht, gilt als offiziell funkberechtigt.
Aufnahme/Entfernung vergibt automatisch die Rolle "Funkberechtigt" (config.ROLLE_FUNKBERECHTIGT).
"""

from __future__ import annotations


import datetime

import discord
from discord import app_commands
from discord.ext import commands

import config
from database import get_connection
from settings import get_setting


def _finde_user_id_per_roblox(roblox_name: str):
    """Sucht die gespeicherte Discord-User-ID zu einem Roblox-Namen (case-insensitive)."""
    conn = get_connection()
    row = conn.execute(
        "SELECT user_id, letzter_discord_name FROM roblox_verknuepfungen WHERE LOWER(roblox_name) = LOWER(?)",
        (roblox_name.lstrip("@"),),
    ).fetchone()
    conn.close()
    return row


class Funk(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    funk_group = app_commands.Group(name="funk", description="Funk-Whitelist verwalten")
    whitelist_group = app_commands.Group(
        name="whitelist", description="Funk-Whitelist", parent=funk_group
    )

    async def _funk_rolle(self, guild: discord.Guild) -> discord.Role | None:
        rolle = discord.utils.get(guild.roles, name=get_setting("rolle_funkberechtigt"))
        return rolle

    @whitelist_group.command(name="hinzufuegen", description="Setzt ein Mitglied auf die Funk-Whitelist")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def hinzufuegen(self, interaction: discord.Interaction, mitglied: discord.Member):
        conn = get_connection()
        bereits = conn.execute(
            "SELECT 1 FROM funk_whitelist WHERE user_id = ?", (mitglied.id,)
        ).fetchone()

        if bereits:
            conn.close()
            await interaction.response.send_message(
                f"{mitglied.mention} steht bereits auf der Funk-Whitelist.", ephemeral=True
            )
            return

        conn.execute(
            "INSERT INTO funk_whitelist (user_id, hinzugefuegt_von, hinzugefuegt_am) VALUES (?, ?, ?)",
            (mitglied.id, interaction.user.id, datetime.datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()

        rolle = await self._funk_rolle(interaction.guild)
        rollen_hinweis = ""
        if rolle:
            await mitglied.add_roles(rolle, reason=f"Funk-Whitelist durch {interaction.user}")
        else:
            rollen_hinweis = f"\n⚠️ Rolle '{get_setting('rolle_funkberechtigt')}' wurde nicht gefunden - bitte manuell anlegen."

        log_channel = discord.utils.get(interaction.guild.text_channels, name=get_setting("channel_funk_log"))
        if log_channel:
            embed = discord.Embed(
                description=f"📻 {mitglied.mention} wurde von {interaction.user.mention} auf die "
                "Funk-Whitelist gesetzt.",
                color=0x2ecc71,
                timestamp=datetime.datetime.now(),
            )
            await log_channel.send(embed=embed)

        await interaction.response.send_message(
            f"✅ {mitglied.mention} wurde auf die Funk-Whitelist gesetzt und die Rolle "
            f"**{get_setting('rolle_funkberechtigt')}** vergeben.{rollen_hinweis}"
        )

    @whitelist_group.command(name="entfernen", description="Entfernt ein Mitglied von der Funk-Whitelist")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def entfernen(self, interaction: discord.Interaction, mitglied: discord.Member):
        conn = get_connection()
        vorhanden = conn.execute(
            "SELECT 1 FROM funk_whitelist WHERE user_id = ?", (mitglied.id,)
        ).fetchone()

        if not vorhanden:
            conn.close()
            await interaction.response.send_message(
                f"{mitglied.mention} steht nicht auf der Funk-Whitelist.", ephemeral=True
            )
            return

        conn.execute("DELETE FROM funk_whitelist WHERE user_id = ?", (mitglied.id,))
        conn.commit()
        conn.close()

        rolle = await self._funk_rolle(interaction.guild)
        if rolle and rolle in mitglied.roles:
            await mitglied.remove_roles(rolle, reason=f"Funk-Whitelist entfernt durch {interaction.user}")

        log_channel = discord.utils.get(interaction.guild.text_channels, name=get_setting("channel_funk_log"))
        if log_channel:
            embed = discord.Embed(
                description=f"📻 {mitglied.mention} wurde von {interaction.user.mention} von der "
                "Funk-Whitelist entfernt.",
                color=0xe74c3c,
                timestamp=datetime.datetime.now(),
            )
            await log_channel.send(embed=embed)

        await interaction.response.send_message(
            f"✅ {mitglied.mention} wurde von der Funk-Whitelist entfernt und die Rolle "
            f"**{get_setting('rolle_funkberechtigt')}** entzogen."
        )

    @whitelist_group.command(
        name="entfernen_roblox",
        description="Entfernt jemanden per Roblox-Namen von der Funk-Whitelist (auch wenn nicht mehr im Discord)",
    )
    @app_commands.describe(roblox_name="Roblox-Benutzername der Person")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def entfernen_roblox(self, interaction: discord.Interaction, roblox_name: str):
        row = _finde_user_id_per_roblox(roblox_name)
        if not row:
            await interaction.response.send_message(
                f"Kein Discord-User mit dem Roblox-Namen **@{roblox_name.lstrip('@')}** verknüpft. "
                "Erst mit `/roblox verknuepfen` verknüpfen.",
                ephemeral=True,
            )
            return

        user_id = row["user_id"]

        conn = get_connection()
        vorhanden = conn.execute("SELECT 1 FROM funk_whitelist WHERE user_id = ?", (user_id,)).fetchone()
        if not vorhanden:
            conn.close()
            await interaction.response.send_message(
                f"**@{roblox_name.lstrip('@')}** steht nicht auf der Funk-Whitelist.", ephemeral=True
            )
            return

        conn.execute("DELETE FROM funk_whitelist WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

        # Rolle nur entziehen, falls die Person noch auf dem Server ist
        member = interaction.guild.get_member(user_id)
        if member:
            rolle = await self._funk_rolle(interaction.guild)
            if rolle and rolle in member.roles:
                await member.remove_roles(rolle, reason=f"Funk-Whitelist entfernt (Roblox) durch {interaction.user}")

        log_channel = discord.utils.get(interaction.guild.text_channels, name=get_setting("channel_funk_log"))
        if log_channel:
            hinweis = member.mention if member else f"`{row['letzter_discord_name']}` (nicht mehr im Server)"
            embed = discord.Embed(
                description=f"📻 **@{roblox_name.lstrip('@')}** ({hinweis}) wurde von "
                f"{interaction.user.mention} von der Funk-Whitelist entfernt.",
                color=0xe74c3c,
                timestamp=datetime.datetime.now(),
            )
            await log_channel.send(embed=embed)

        await interaction.response.send_message(
            f"✅ **@{roblox_name.lstrip('@')}** wurde von der Funk-Whitelist entfernt."
        )

    @whitelist_group.command(name="liste", description="Zeigt alle Mitglieder auf der Funk-Whitelist")
    async def liste(self, interaction: discord.Interaction):
        conn = get_connection()
        rows = conn.execute("SELECT user_id FROM funk_whitelist ORDER BY hinzugefuegt_am").fetchall()
        conn.close()

        embed = discord.Embed(title="📻 Funk-Whitelist", color=0x3498db)
        if rows:
            mitglieder = []
            for row in rows:
                member = interaction.guild.get_member(row["user_id"])
                if member:
                    mitglieder.append(f"• {member.mention}")
            embed.description = "\n".join(mitglieder) if mitglieder else "Keine aktuellen Mitglieder gefunden."
        else:
            embed.description = "Die Funk-Whitelist ist aktuell leer."
        embed.set_footer(text=f"{len(rows)} Einträge")

        await interaction.response.send_message(embed=embed)

    @whitelist_group.command(name="check", description="Prüft, ob ein Mitglied auf der Funk-Whitelist steht")
    async def check(self, interaction: discord.Interaction, mitglied: discord.Member):
        conn = get_connection()
        vorhanden = conn.execute(
            "SELECT 1 FROM funk_whitelist WHERE user_id = ?", (mitglied.id,)
        ).fetchone()
        conn.close()

        status = "✅ steht auf der Funk-Whitelist" if vorhanden else "❌ steht NICHT auf der Funk-Whitelist"
        await interaction.response.send_message(f"{mitglied.mention} {status}.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Funk(bot))
