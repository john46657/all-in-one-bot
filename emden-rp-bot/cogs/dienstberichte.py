"""
Dienstberichte: /dienstbericht öffnet ein Formular, der Bericht wird gespeichert
und als Embed im Log-Channel gepostet. /dienstberichte zeigt die Historie eines Mitglieds.
"""

import datetime

import discord
from discord import app_commands
from discord.ext import commands

import config
from database import get_connection
from settings import get_setting


class DienstberichtModal(discord.ui.Modal, title="Dienstbericht"):
    datum = discord.ui.TextInput(label="Datum", placeholder="z.B. 25.07.2026", max_length=20)
    dauer = discord.ui.TextInput(label="Dauer der Schicht", placeholder="z.B. 2h 30min", max_length=20)
    taetigkeiten = discord.ui.TextInput(
        label="Was wurde gemacht?",
        style=discord.TextStyle.paragraph,
        placeholder="Streifenfahrten, Kontrollen, Einsätze ...",
        max_length=1000,
    )
    besonderheiten = discord.ui.TextInput(
        label="Besonderheiten (optional)",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=500,
    )

    async def on_submit(self, interaction: discord.Interaction):
        conn = get_connection()
        conn.execute(
            "INSERT INTO dienstberichte (user_id, datum, dauer, taetigkeiten, besonderheiten, erstellt_am) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                interaction.user.id,
                str(self.datum),
                str(self.dauer),
                str(self.taetigkeiten),
                str(self.besonderheiten) if self.besonderheiten.value else None,
                datetime.datetime.now().isoformat(),
            ),
        )
        conn.commit()
        conn.close()

        embed = discord.Embed(title="📝 Dienstbericht", color=0x3498db, timestamp=datetime.datetime.now())
        embed.add_field(name="Beamter", value=interaction.user.mention, inline=True)
        embed.add_field(name="Datum", value=str(self.datum), inline=True)
        embed.add_field(name="Dauer", value=str(self.dauer), inline=True)
        embed.add_field(name="Tätigkeiten", value=str(self.taetigkeiten), inline=False)
        if self.besonderheiten.value:
            embed.add_field(name="Besonderheiten", value=str(self.besonderheiten), inline=False)

        channel = discord.utils.get(interaction.guild.text_channels, name=get_setting("channel_dienstberichte"))
        if channel:
            await channel.send(embed=embed)

        await interaction.response.send_message("✅ Dienstbericht wurde eingereicht.", ephemeral=True)


class Dienstberichte(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="dienstbericht", description="Reiche einen Dienstbericht ein")
    async def dienstbericht(self, interaction: discord.Interaction):
        await interaction.response.send_modal(DienstberichtModal())

    @app_commands.command(name="dienstberichte", description="Zeigt die letzten Dienstberichte eines Mitglieds")
    @app_commands.describe(mitglied="Für wen? (leer lassen für dich selbst)")
    async def dienstberichte(self, interaction: discord.Interaction, mitglied: discord.Member = None):
        ziel = mitglied or interaction.user
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM dienstberichte WHERE user_id = ? ORDER BY id DESC LIMIT 5",
            (ziel.id,),
        ).fetchall()
        conn.close()

        if not rows:
            await interaction.response.send_message(
                f"Keine Dienstberichte für {ziel.display_name} gefunden.", ephemeral=True
            )
            return

        embed = discord.Embed(title=f"Letzte Dienstberichte - {ziel.display_name}", color=0x3498db)
        for row in rows:
            embed.add_field(
                name=f"{row['datum']} ({row['dauer']})",
                value=row["taetigkeiten"][:200],
                inline=False,
            )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Dienstberichte(bot))
