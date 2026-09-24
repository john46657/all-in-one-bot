"""
GSG9-Modul: eigenes Roster, eigene Einsatzberichte, getrennt von der normalen Teamliste.
Bewerbung für GSG9 läuft über dieselbe Modal-Logik wie das normale Bewerbungssystem.
"""

import datetime

import discord
from discord import app_commands
from discord.ext import commands

import config
from database import get_connection
from settings import get_setting
from checks import benoetigt_rolle


class GSG9BewerbungsModal(discord.ui.Modal, title="Bewerbung - GSG9"):
    dienstzeit = discord.ui.TextInput(label="Wie lange bist du schon im Polizeidienst?", max_length=50)
    motivation = discord.ui.TextInput(
        label="Warum möchtest du zur GSG9?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    erfahrung = discord.ui.TextInput(
        label="Besondere Erfahrung/Qualifikation",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=500,
    )

    async def on_submit(self, interaction: discord.Interaction):
        channel = discord.utils.get(interaction.guild.text_channels, name=get_setting("channel_gsg9_log"))
        if channel is None:
            await interaction.response.send_message(
                f"Fehler: Channel '#{get_setting('channel_gsg9_log')}' nicht gefunden.", ephemeral=True
            )
            return

        embed = discord.Embed(title="🎯 Neue GSG9-Bewerbung", color=0x34495e, timestamp=datetime.datetime.now())
        embed.add_field(name="Bewerber", value=interaction.user.mention, inline=True)
        embed.add_field(name="Dienstzeit", value=str(self.dienstzeit), inline=True)
        embed.add_field(name="Motivation", value=str(self.motivation), inline=False)
        if self.erfahrung.value:
            embed.add_field(name="Erfahrung", value=str(self.erfahrung), inline=False)
        embed.set_footer(text=f"User-ID: {interaction.user.id}")

        await channel.send(embed=embed)
        await interaction.response.send_message("✅ Deine GSG9-Bewerbung wurde eingereicht.", ephemeral=True)


class GSG9EinsatzberichtModal(discord.ui.Modal, title="GSG9 Einsatzbericht"):
    datum = discord.ui.TextInput(label="Datum", max_length=20)
    einsatzart = discord.ui.TextInput(label="Art des Einsatzes", placeholder="z.B. Geiselnahme, Zugriff", max_length=100)
    beschreibung = discord.ui.TextInput(
        label="Beschreibung",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        conn = get_connection()
        conn.execute(
            "INSERT INTO gsg9_einsatzberichte (user_id, datum, einsatzart, beschreibung, erstellt_am) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                interaction.user.id,
                str(self.datum),
                str(self.einsatzart),
                str(self.beschreibung),
                datetime.datetime.now().isoformat(),
            ),
        )
        conn.commit()
        conn.close()

        embed = discord.Embed(title="🎯 GSG9 Einsatzbericht", color=0x34495e, timestamp=datetime.datetime.now())
        embed.add_field(name="Beamter", value=interaction.user.mention, inline=True)
        embed.add_field(name="Datum", value=str(self.datum), inline=True)
        embed.add_field(name="Einsatzart", value=str(self.einsatzart), inline=True)
        embed.add_field(name="Beschreibung", value=str(self.beschreibung), inline=False)

        channel = discord.utils.get(interaction.guild.text_channels, name=get_setting("channel_gsg9_log"))
        if channel:
            await channel.send(embed=embed)

        await interaction.response.send_message("✅ Einsatzbericht gespeichert.", ephemeral=True)


class GSG9(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    gsg9_group = app_commands.Group(name="gsg9", description="GSG9-Spezialeinheit")

    @gsg9_group.command(name="bewerbung", description="Bewirb dich für die GSG9")
    async def bewerbung(self, interaction: discord.Interaction):
        await interaction.response.send_modal(GSG9BewerbungsModal())

    @gsg9_group.command(name="einsatzbericht", description="Erstellt einen GSG9-Einsatzbericht")
    @benoetigt_rolle("rolle_gsg9")
    async def einsatzbericht(self, interaction: discord.Interaction):
        await interaction.response.send_modal(GSG9EinsatzberichtModal())

    @gsg9_group.command(name="liste", description="Zeigt alle aktuellen GSG9-Mitglieder")
    async def liste(self, interaction: discord.Interaction):
        rolle = discord.utils.get(interaction.guild.roles, name=get_setting("rolle_gsg9"))
        if rolle is None:
            await interaction.response.send_message("GSG9-Rolle nicht gefunden.", ephemeral=True)
            return

        mitglieder = [m for m in rolle.members if not m.bot]
        embed = discord.Embed(title="🎯 GSG9 - Mitgliederliste", color=0x34495e)
        if mitglieder:
            embed.description = "\n".join(f"• {m.mention}" for m in mitglieder)
        else:
            embed.description = "Aktuell keine Mitglieder."
        embed.set_footer(text=f"{len(mitglieder)} Mitglieder")

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(GSG9(bot))
