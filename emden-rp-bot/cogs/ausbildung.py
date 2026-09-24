"""
Ausbildungssystem: Ausbilder-Zuweisung, Modul-Checkliste pro Rekrut, Prüfungsberichte.
"""

import datetime

import discord
from discord import app_commands
from discord.ext import commands

import config
from database import get_connection
from settings import get_setting
from checks import benoetigt_rolle


class Ausbildungsbericht(discord.ui.Modal, title="Ausbildungsbericht"):
    def __init__(self, rekrut: discord.Member):
        super().__init__()
        self.rekrut = rekrut

    datum = discord.ui.TextInput(label="Datum", placeholder="z.B. 25.07.2026", max_length=20)
    dauer = discord.ui.TextInput(label="Dauer", placeholder="z.B. 1h", max_length=20)
    themen = discord.ui.TextInput(
        label="Behandelte Themen",
        style=discord.TextStyle.paragraph,
        max_length=500,
    )
    bewertung = discord.ui.TextInput(
        label="Bewertung / Anmerkungen",
        style=discord.TextStyle.paragraph,
        max_length=500,
    )
    bestanden = discord.ui.TextInput(label="Bestanden? (ja/nein)", max_length=5)

    async def on_submit(self, interaction: discord.Interaction):
        bestanden_bool = str(self.bestanden).strip().lower() in ("ja", "j", "yes", "y")

        conn = get_connection()
        conn.execute(
            "INSERT INTO ausbildungsberichte "
            "(rekrut_id, ausbilder_id, datum, dauer, themen, bewertung, bestanden, erstellt_am) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                self.rekrut.id,
                interaction.user.id,
                str(self.datum),
                str(self.dauer),
                str(self.themen),
                str(self.bewertung),
                int(bestanden_bool),
                datetime.datetime.now().isoformat(),
            ),
        )
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="🎓 Ausbildungsbericht",
            color=0x2ecc71 if bestanden_bool else 0xe74c3c,
            timestamp=datetime.datetime.now(),
        )
        embed.add_field(name="Rekrut", value=self.rekrut.mention, inline=True)
        embed.add_field(name="Ausbilder", value=interaction.user.mention, inline=True)
        embed.add_field(name="Datum", value=str(self.datum), inline=True)
        embed.add_field(name="Themen", value=str(self.themen), inline=False)
        embed.add_field(name="Bewertung", value=str(self.bewertung), inline=False)
        embed.add_field(name="Bestanden", value="✅ Ja" if bestanden_bool else "❌ Nein", inline=True)

        channel = discord.utils.get(interaction.guild.text_channels, name=get_setting("channel_ausbildungsberichte"))
        if channel:
            await channel.send(embed=embed)

        await interaction.response.send_message("✅ Ausbildungsbericht gespeichert.", ephemeral=True)


class Ausbildung(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    ausbildung_group = app_commands.Group(name="ausbildung", description="Ausbildungssystem verwalten")

    @ausbildung_group.command(name="zuweisen", description="Weist einem Rekruten einen Ausbilder zu")
    @benoetigt_rolle("rolle_ausbilder")
    async def zuweisen(self, interaction: discord.Interaction, rekrut: discord.Member, ausbilder: discord.Member):
        conn = get_connection()
        conn.execute(
            "INSERT INTO ausbildung (rekrut_id, ausbilder_id, start_datum) VALUES (?, ?, ?) "
            "ON CONFLICT(rekrut_id) DO UPDATE SET ausbilder_id = excluded.ausbilder_id",
            (rekrut.id, ausbilder.id, datetime.datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()
        await interaction.response.send_message(
            f"✅ {rekrut.mention} wird jetzt von {ausbilder.mention} ausgebildet."
        )

    @ausbildung_group.command(name="modul", description="Trägt ein bestandenes/nicht bestandenes Modul ein")
    @benoetigt_rolle("rolle_ausbilder")
    async def modul(
        self,
        interaction: discord.Interaction,
        rekrut: discord.Member,
        modul_name: str,
        bestanden: bool,
    ):
        conn = get_connection()
        conn.execute(
            "INSERT INTO ausbildung_module (rekrut_id, modul_name, bestanden, abgenommen_von, datum) "
            "VALUES (?, ?, ?, ?, ?)",
            (rekrut.id, modul_name, int(bestanden), interaction.user.id, datetime.datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()

        status = "✅ bestanden" if bestanden else "❌ nicht bestanden"
        await interaction.response.send_message(
            f"Modul **{modul_name}** für {rekrut.mention}: {status}"
        )

    @ausbildung_group.command(name="fortschritt", description="Zeigt den Ausbildungsfortschritt eines Rekruten")
    async def fortschritt(self, interaction: discord.Interaction, rekrut: discord.Member):
        conn = get_connection()
        module = conn.execute(
            "SELECT modul_name, bestanden FROM ausbildung_module WHERE rekrut_id = ? ORDER BY id",
            (rekrut.id,),
        ).fetchall()
        zuweisung = conn.execute(
            "SELECT ausbilder_id FROM ausbildung WHERE rekrut_id = ?", (rekrut.id,)
        ).fetchone()
        conn.close()

        embed = discord.Embed(title=f"Ausbildungsfortschritt - {rekrut.display_name}", color=0x3498db)
        if zuweisung:
            ausbilder = interaction.guild.get_member(zuweisung["ausbilder_id"])
            embed.add_field(
                name="Ausbilder",
                value=ausbilder.mention if ausbilder else "Unbekannt",
                inline=False,
            )

        if module:
            text = "\n".join(
                f"{'✅' if m['bestanden'] else '❌'} {m['modul_name']}" for m in module
            )
        else:
            text = "Noch keine Module eingetragen."
        embed.add_field(name="Module", value=text, inline=False)

        await interaction.response.send_message(embed=embed)

    @ausbildung_group.command(name="bericht", description="Erstellt einen Ausbildungs-/Prüfungsbericht")
    @benoetigt_rolle("rolle_ausbilder")
    async def bericht(self, interaction: discord.Interaction, rekrut: discord.Member):
        await interaction.response.send_modal(Ausbildungsbericht(rekrut))

    @ausbildung_group.command(name="abschliessen", description="Schließt die Ausbildung eines Rekruten ab")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def abschliessen(self, interaction: discord.Interaction, rekrut: discord.Member):
        conn = get_connection()
        conn.execute("UPDATE ausbildung SET abgeschlossen = 1 WHERE rekrut_id = ?", (rekrut.id,))
        conn.commit()
        conn.close()

        await interaction.response.send_message(
            f"🎉 {rekrut.mention} hat die Ausbildung abgeschlossen! Denk daran, die Rang-Rolle anzupassen."
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Ausbildung(bot))
