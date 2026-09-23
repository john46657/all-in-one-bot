"""
Fahndungssystem: /fahndung erstellen postet eine Fahndung, /fahndung beenden markiert sie
als erledigt, /fahndung liste zeigt alle aktiven Fahndungen.
"""

import datetime
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

import config
from database import get_connection
from settings import get_setting

DRINGLICHKEIT_FARBEN = {
    "normal": 0x3498db,
    "gefaehrlich": 0xf1c40f,
    "bewaffnet_fluechtig": 0xe74c3c,
}
DRINGLICHKEIT_LABEL = {
    "normal": "Normal",
    "gefaehrlich": "⚠️ Gefährlich",
    "bewaffnet_fluechtig": "🚨 Bewaffnet & flüchtig",
}


class Fahndung(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    fahndung_group = app_commands.Group(name="fahndung", description="Fahndungen verwalten")

    @fahndung_group.command(name="erstellen", description="Erstellt eine neue Fahndung")
    @app_commands.describe(
        name="Name/Alias der gesuchten Person",
        grund="Grund der Fahndung",
        beschreibung="Beschreibung (Aussehen, letzter bekannter Ort, etc.)",
        dringlichkeit="Wie dringend/gefährlich ist die Fahndung?",
    )
    async def erstellen(
        self,
        interaction: discord.Interaction,
        name: str,
        grund: str,
        beschreibung: str,
        dringlichkeit: Literal["normal", "gefaehrlich", "bewaffnet_fluechtig"] = "normal",
    ):
        channel = discord.utils.get(interaction.guild.text_channels, name=get_setting("channel_fahndungen"))
        if channel is None:
            await interaction.response.send_message(
                f"Fehler: Channel '#{get_setting('channel_fahndungen')}' nicht gefunden.", ephemeral=True
            )
            return

        jetzt = datetime.datetime.now()
        embed = discord.Embed(
            title=f"🚔 FAHNDUNG: {name}",
            color=DRINGLICHKEIT_FARBEN[dringlichkeit],
            timestamp=jetzt,
        )
        embed.add_field(name="Grund", value=grund, inline=False)
        embed.add_field(name="Beschreibung", value=beschreibung, inline=False)
        embed.add_field(name="Dringlichkeit", value=DRINGLICHKEIT_LABEL[dringlichkeit], inline=True)
        embed.add_field(name="Status", value="🔴 Aktiv", inline=True)
        embed.set_footer(text=f"Erstellt von {interaction.user.display_name}")

        message = await channel.send(embed=embed)

        conn = get_connection()
        conn.execute(
            "INSERT INTO fahndungen (name, grund, beschreibung, dringlichkeit, erstellt_von, "
            "erstellt_am, aktiv, message_id, channel_id) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)",
            (name, grund, beschreibung, dringlichkeit, interaction.user.id, jetzt.isoformat(), message.id, channel.id),
        )
        conn.commit()
        conn.close()

        await interaction.response.send_message(f"✅ Fahndung nach **{name}** wurde veröffentlicht.", ephemeral=True)

    @fahndung_group.command(name="beenden", description="Markiert eine Fahndung als erledigt (z.B. Person gefasst)")
    async def beenden(self, interaction: discord.Interaction, name: str):
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM fahndungen WHERE name = ? AND aktiv = 1 ORDER BY id DESC LIMIT 1",
            (name,),
        ).fetchone()

        if not row:
            conn.close()
            await interaction.response.send_message(f"Keine aktive Fahndung nach **{name}** gefunden.", ephemeral=True)
            return

        conn.execute("UPDATE fahndungen SET aktiv = 0 WHERE id = ?", (row["id"],))
        conn.commit()
        conn.close()

        channel = self.bot.get_channel(row["channel_id"])
        if channel:
            try:
                message = await channel.fetch_message(row["message_id"])
                embed = message.embeds[0]
                # Status-Feld aktualisieren (letztes Feld war "Status")
                embed.set_field_at(3, name="Status", value=f"✅ Erledigt (durch {interaction.user.display_name})", inline=True)
                embed.color = 0x2ecc71
                await message.edit(embed=embed)
            except (discord.NotFound, discord.HTTPException, IndexError):
                pass

        await interaction.response.send_message(f"✅ Fahndung nach **{name}** wurde beendet.", ephemeral=True)

    @fahndung_group.command(name="liste", description="Zeigt alle aktuell aktiven Fahndungen")
    async def liste(self, interaction: discord.Interaction):
        conn = get_connection()
        rows = conn.execute(
            "SELECT name, grund, dringlichkeit FROM fahndungen WHERE aktiv = 1 ORDER BY id DESC"
        ).fetchall()
        conn.close()

        if not rows:
            await interaction.response.send_message("Aktuell liegen keine aktiven Fahndungen vor.")
            return

        embed = discord.Embed(title="🚔 Aktive Fahndungen", color=0xe74c3c)
        for row in rows:
            embed.add_field(
                name=f"{row['name']} - {DRINGLICHKEIT_LABEL[row['dringlichkeit']]}",
                value=row["grund"],
                inline=False,
            )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Fahndung(bot))
