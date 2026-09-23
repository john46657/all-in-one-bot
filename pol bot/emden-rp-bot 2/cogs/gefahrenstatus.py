"""
Gefahrenstatus: Button-Panel zum Setzen des aktuellen Gefahrenlevels (Grün/Gelb/Rot).
Aktualisiert eine feste Status-Nachricht und pingt bei Änderung die Dienst-Rolle.
"""

from __future__ import annotations


import datetime

import discord
from discord import app_commands
from discord.ext import commands

import config
from database import get_config, set_config, get_connection
from settings import get_setting


class GrundModal(discord.ui.Modal, title="Grund für Statusänderung"):
    grund = discord.ui.TextInput(
        label="Grund (optional)",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=200,
    )

    def __init__(self, stufe_key: str, cog: "Gefahrenstatus"):
        super().__init__()
        self.stufe_key = stufe_key
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        await self.cog.status_setzen(interaction, self.stufe_key, str(self.grund) or None)


class GefahrenstatusPanel(discord.ui.View):
    def __init__(self, cog: "Gefahrenstatus"):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="Grün", emoji="🟢", style=discord.ButtonStyle.success, custom_id="status_gruen")
    async def gruen(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(GrundModal("gruen", self.cog))

    @discord.ui.button(label="Gelb", emoji="🟡", style=discord.ButtonStyle.primary, custom_id="status_gelb")
    async def gelb(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(GrundModal("gelb", self.cog))

    @discord.ui.button(label="Rot", emoji="🔴", style=discord.ButtonStyle.danger, custom_id="status_rot")
    async def rot(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(GrundModal("rot", self.cog))


class Gefahrenstatus(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.add_view(GefahrenstatusPanel(self))

    def _berechtigt(self, member: discord.Member) -> bool:
        return any(r.name == get_setting("rolle_leitung") for r in member.roles) or member.guild_permissions.administrator

    async def status_setzen(self, interaction: discord.Interaction, stufe_key: str, grund: str | None):
        if not self._berechtigt(interaction.user):
            await interaction.response.send_message(
                "⛔ Du hast keine Berechtigung, den Gefahrenstatus zu ändern.", ephemeral=True
            )
            return

        stufe = config.GEFAHRENSTUFEN[stufe_key]
        jetzt = datetime.datetime.now()

        conn = get_connection()
        conn.execute(
            "INSERT INTO gefahrenstatus_verlauf (status, grund, gesetzt_von, gesetzt_am) VALUES (?, ?, ?, ?)",
            (stufe_key, grund, interaction.user.id, jetzt.isoformat()),
        )
        conn.commit()
        conn.close()
        set_config("gefahrenstatus_aktuell", stufe_key)

        channel = discord.utils.get(interaction.guild.text_channels, name=get_setting("channel_gefahrenstatus"))
        if channel is None:
            await interaction.response.send_message(
                f"Fehler: Channel '#{get_setting('channel_gefahrenstatus')}' nicht gefunden.", ephemeral=True
            )
            return

        embed = self._build_status_embed(stufe_key, grund, interaction.user, jetzt)

        message_id = get_config(f"gefahrenstatus_message_id_{interaction.guild.id}")
        message = None
        if message_id:
            try:
                message = await channel.fetch_message(int(message_id))
            except (discord.NotFound, discord.HTTPException):
                message = None

        if message:
            await message.edit(embed=embed, view=GefahrenstatusPanel(self))
        else:
            new_message = await channel.send(embed=embed, view=GefahrenstatusPanel(self))
            set_config(f"gefahrenstatus_message_id_{interaction.guild.id}", new_message.id)

        # Dienst-Rolle bei Statusänderung informieren
        dienst_rolle = discord.utils.get(interaction.guild.roles, name=get_setting("rolle_im_dienst"))
        if dienst_rolle:
            hinweis = f"{stufe['emoji']} Gefahrenstatus geändert zu **{stufe['label']}**"
            if grund:
                hinweis += f"\nGrund: {grund}"
            await channel.send(content=dienst_rolle.mention, embed=discord.Embed(description=hinweis, color=stufe["farbe"]))

        await interaction.response.send_message(f"✅ Status wurde auf **{stufe['label']}** gesetzt.", ephemeral=True)

    def _build_status_embed(self, stufe_key: str, grund: str | None, setzer: discord.Member, zeit: datetime.datetime):
        stufe = config.GEFAHRENSTUFEN[stufe_key]
        embed = discord.Embed(
            title=f"{stufe['emoji']} Aktueller Gefahrenstatus: {stufe['label']}",
            color=stufe["farbe"],
            timestamp=zeit,
        )
        embed.add_field(name="Gesetzt von", value=setzer.mention, inline=True)
        if grund:
            embed.add_field(name="Grund", value=grund, inline=False)
        embed.set_footer(text="Klicke unten, um den Status zu ändern (nur Leitung)")
        return embed

    @app_commands.command(name="gefahrenstatus_panel", description="Postet das Gefahrenstatus-Panel in diesen Channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def panel_posten(self, interaction: discord.Interaction):
        aktuell = get_config("gefahrenstatus_aktuell", "gruen")
        embed = self._build_status_embed(aktuell, None, interaction.user, datetime.datetime.now())
        message = await interaction.channel.send(embed=embed, view=GefahrenstatusPanel(self))
        set_config(f"gefahrenstatus_message_id_{interaction.guild.id}", message.id)
        await interaction.response.send_message("✅ Panel gepostet.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Gefahrenstatus(bot))
