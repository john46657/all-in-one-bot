"""
Bewerbungssystem: /bewerbung startet ein Formular (Modal), Antworten landen als Embed
im Log-Channel, Staff kann per Button annehmen/ablehnen.
"""

import datetime

import discord
from discord import app_commands
from discord.ext import commands

import config
from settings import get_setting
from database import get_connection


class BewerbungsModal(discord.ui.Modal, title="Bewerbung - Emden RP"):
    name = discord.ui.TextInput(label="Dein Name / Alias", max_length=100)
    roblox_name = discord.ui.TextInput(label="Dein Roblox-Benutzername", max_length=50)
    alter = discord.ui.TextInput(label="Wie alt bist du?", max_length=10)
    erfahrung = discord.ui.TextInput(
        label="Roleplay-Erfahrung",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )
    motivation = discord.ui.TextInput(
        label="Warum möchtest du zu uns?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        log_channel = discord.utils.get(
            interaction.guild.text_channels, name=get_setting("channel_bewerbungen_log")
        )
        if log_channel is None:
            await interaction.response.send_message(
                f"Fehler: Log-Channel '#{get_setting('channel_bewerbungen_log')}' wurde nicht gefunden. "
                "Bitte einen Admin informieren.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="📋 Neue Bewerbung",
            color=0x3498db,
            timestamp=datetime.datetime.now(),
        )
        embed.add_field(name="Bewerber", value=interaction.user.mention, inline=True)
        embed.add_field(name="Name/Alias", value=str(self.name), inline=True)
        embed.add_field(name="Roblox-Name", value=str(self.roblox_name), inline=True)
        embed.add_field(name="Alter", value=str(self.alter), inline=True)
        embed.add_field(name="Erfahrung", value=str(self.erfahrung), inline=False)
        embed.add_field(name="Motivation", value=str(self.motivation), inline=False)
        embed.set_footer(text=f"User-ID: {interaction.user.id}")

        await log_channel.send(embed=embed, view=BewerbungsEntscheidungView())
        await interaction.response.send_message(
            "✅ Deine Bewerbung wurde eingereicht! Du bekommst Bescheid, sobald sie geprüft wurde.",
            ephemeral=True,
        )


class BewerbungsEntscheidungView(discord.ui.View):
    """Buttons unter der Bewerbungs-Nachricht im Log-Channel, für Staff."""

    def __init__(self):
        super().__init__(timeout=None)  # persistent - funktioniert auch nach Bot-Neustart

    @discord.ui.button(label="Annehmen", style=discord.ButtonStyle.success, custom_id="bewerbung_annehmen")
    async def annehmen(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._entscheidung(interaction, angenommen=True)

    @discord.ui.button(label="Ablehnen", style=discord.ButtonStyle.danger, custom_id="bewerbung_ablehnen")
    async def ablehnen(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._entscheidung(interaction, angenommen=False)

    async def _entscheidung(self, interaction: discord.Interaction, angenommen: bool):
        embed = interaction.message.embeds[0]
        user_id = int(embed.footer.text.replace("User-ID: ", ""))
        member = interaction.guild.get_member(user_id)

        status_text = "✅ Angenommen" if angenommen else "❌ Abgelehnt"
        embed.color = 0x2ecc71 if angenommen else 0xe74c3c
        embed.add_field(name="Status", value=f"{status_text} von {interaction.user.mention}", inline=False)

        # Buttons deaktivieren, damit nicht doppelt geklickt werden kann
        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

        if member:
            if angenommen:
                roblox_feld = discord.utils.get(embed.fields, name="Roblox-Name")
                if roblox_feld:
                    conn = get_connection()
                    conn.execute(
                        "INSERT INTO roblox_verknuepfungen "
                        "(user_id, roblox_name, letzter_discord_name, verknuepft_von, verknuepft_am) "
                        "VALUES (?, ?, ?, ?, ?) "
                        "ON CONFLICT(user_id) DO UPDATE SET roblox_name = excluded.roblox_name, "
                        "letzter_discord_name = excluded.letzter_discord_name",
                        (
                            member.id,
                            roblox_feld.value.lstrip("@"),
                            str(member),
                            interaction.user.id,
                            datetime.datetime.now().isoformat(),
                        ),
                    )
                    conn.commit()
                    conn.close()

            try:
                if angenommen:
                    await member.send(
                        "🎉 Herzlichen Glückwunsch! Deine Bewerbung beim Emden RP wurde angenommen. "
                        "Ein Teammitglied meldet sich bei dir für die weiteren Schritte."
                    )
                else:
                    await member.send(
                        "Leider müssen wir dir mitteilen, dass deine Bewerbung beim Emden RP "
                        "diesmal nicht angenommen wurde. Du kannst dich gerne später erneut bewerben."
                    )
            except discord.Forbidden:
                pass  # User hat DMs deaktiviert


class Bewerbungen(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        # Persistente View registrieren, damit Buttons auch nach Bot-Neustart funktionieren
        self.bot.add_view(BewerbungsEntscheidungView())

    @app_commands.command(name="bewerbung", description="Bewirb dich beim Emden RP Team")
    async def bewerbung(self, interaction: discord.Interaction):
        await interaction.response.send_modal(BewerbungsModal())


async def setup(bot: commands.Bot):
    await bot.add_cog(Bewerbungen(bot))
