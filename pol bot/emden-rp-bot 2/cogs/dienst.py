"""
Dienstzeiten-Tracking: /dienst start und /dienst ende, Zeit wird in der Datenbank
gespeichert und aufsummiert.
"""

import datetime

import discord
from discord import app_commands
from discord.ext import commands

from database import get_connection


def format_dauer(sekunden: int) -> str:
    stunden = sekunden // 3600
    minuten = (sekunden % 3600) // 60
    return f"{stunden}h {minuten}min"


class Dienst(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    dienst_group = app_commands.Group(name="dienst", description="Dienstzeiten verwalten")

    @dienst_group.command(name="start", description="Startet deine Dienstzeit")
    async def start(self, interaction: discord.Interaction):
        conn = get_connection()
        laufend = conn.execute(
            "SELECT id FROM dienstzeiten WHERE user_id = ? AND ende_zeit IS NULL",
            (interaction.user.id,),
        ).fetchone()

        if laufend:
            conn.close()
            await interaction.response.send_message(
                "⚠️ Du hast bereits eine laufende Schicht. Beende sie erst mit `/dienst ende`.",
                ephemeral=True,
            )
            return

        jetzt = datetime.datetime.now().isoformat()
        conn.execute(
            "INSERT INTO dienstzeiten (user_id, start_zeit) VALUES (?, ?)",
            (interaction.user.id, jetzt),
        )
        conn.commit()
        conn.close()

        await interaction.response.send_message("🟢 Dienst gestartet. Bleib sicher da draußen!")

    @dienst_group.command(name="ende", description="Beendet deine Dienstzeit")
    async def ende(self, interaction: discord.Interaction):
        conn = get_connection()
        laufend = conn.execute(
            "SELECT id, start_zeit FROM dienstzeiten WHERE user_id = ? AND ende_zeit IS NULL "
            "ORDER BY id DESC LIMIT 1",
            (interaction.user.id,),
        ).fetchone()

        if not laufend:
            conn.close()
            await interaction.response.send_message(
                "⚠️ Du hast aktuell keine laufende Schicht.", ephemeral=True
            )
            return

        start_zeit = datetime.datetime.fromisoformat(laufend["start_zeit"])
        ende_zeit = datetime.datetime.now()
        dauer_sekunden = int((ende_zeit - start_zeit).total_seconds())

        conn.execute(
            "UPDATE dienstzeiten SET ende_zeit = ?, dauer_sekunden = ? WHERE id = ?",
            (ende_zeit.isoformat(), dauer_sekunden, laufend["id"]),
        )
        conn.commit()
        conn.close()

        await interaction.response.send_message(
            f"🔴 Dienst beendet. Dauer dieser Schicht: **{format_dauer(dauer_sekunden)}**"
        )

    @dienst_group.command(name="stunden", description="Zeigt die Gesamtdienstzeit eines Mitglieds")
    @app_commands.describe(mitglied="Für wen? (leer lassen für dich selbst)")
    async def stunden(self, interaction: discord.Interaction, mitglied: discord.Member = None):
        ziel = mitglied or interaction.user
        conn = get_connection()
        row = conn.execute(
            "SELECT SUM(dauer_sekunden) as gesamt FROM dienstzeiten WHERE user_id = ? AND ende_zeit IS NOT NULL",
            (ziel.id,),
        ).fetchone()
        conn.close()

        gesamt = row["gesamt"] or 0
        embed = discord.Embed(
            title=f"Dienstzeit von {ziel.display_name}",
            description=f"Gesamte abgeschlossene Dienstzeit: **{format_dauer(gesamt)}**",
            color=0x3498db,
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Dienst(bot))
