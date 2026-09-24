"""
Roblox-Verknüpfung: speichert, welcher Discord-User zu welchem Roblox-Namen gehört.
Wird von funk.py und teamliste.py genutzt, um Personen auch nach einem Bann oder
Server-Verlassen noch per Roblox-Namen identifizieren zu können (z.B. für
Funk-Entzug oder Entlassung).
"""

import datetime

import discord
from discord import app_commands
from discord.ext import commands

from database import get_connection


class Roblox(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    roblox_group = app_commands.Group(name="roblox", description="Roblox-Verknüpfung verwalten")

    @roblox_group.command(name="verknuepfen", description="Verknüpft einen Discord-User mit seinem Roblox-Namen")
    @app_commands.describe(mitglied="Discord-Mitglied", roblox_name="Roblox-Benutzername (z.B. @Name im Spiel)")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def verknuepfen(self, interaction: discord.Interaction, mitglied: discord.Member, roblox_name: str):
        conn = get_connection()
        conn.execute(
            "INSERT INTO roblox_verknuepfungen "
            "(user_id, roblox_name, letzter_discord_name, verknuepft_von, verknuepft_am) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET roblox_name = excluded.roblox_name, "
            "letzter_discord_name = excluded.letzter_discord_name",
            (mitglied.id, roblox_name.lstrip("@"), str(mitglied), interaction.user.id, datetime.datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()

        await interaction.response.send_message(
            f"✅ {mitglied.mention} wurde mit dem Roblox-Namen **@{roblox_name.lstrip('@')}** verknüpft."
        )

    @roblox_group.command(name="info", description="Zeigt die Roblox-Verknüpfung eines Discord-Mitglieds")
    async def info(self, interaction: discord.Interaction, mitglied: discord.Member):
        conn = get_connection()
        row = conn.execute(
            "SELECT roblox_name FROM roblox_verknuepfungen WHERE user_id = ?", (mitglied.id,)
        ).fetchone()
        conn.close()

        if row:
            await interaction.response.send_message(f"{mitglied.mention} ist verknüpft mit **@{row['roblox_name']}**.")
        else:
            await interaction.response.send_message(f"Für {mitglied.mention} ist kein Roblox-Name hinterlegt.", ephemeral=True)

    @roblox_group.command(name="suchen", description="Sucht einen Discord-User anhand des Roblox-Namens")
    async def suchen(self, interaction: discord.Interaction, roblox_name: str):
        conn = get_connection()
        row = conn.execute(
            "SELECT user_id, letzter_discord_name FROM roblox_verknuepfungen WHERE LOWER(roblox_name) = LOWER(?)",
            (roblox_name.lstrip("@"),),
        ).fetchone()
        conn.close()

        if not row:
            await interaction.response.send_message(
                f"Kein Eintrag für **@{roblox_name.lstrip('@')}** gefunden.", ephemeral=True
            )
            return

        member = interaction.guild.get_member(row["user_id"])
        if member:
            await interaction.response.send_message(
                f"**@{roblox_name.lstrip('@')}** ist aktuell {member.mention} auf diesem Server."
            )
        else:
            await interaction.response.send_message(
                f"**@{roblox_name.lstrip('@')}** war zuletzt als `{row['letzter_discord_name']}` bekannt, "
                "ist aber aktuell nicht (mehr) auf dem Server."
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Roblox(bot))
