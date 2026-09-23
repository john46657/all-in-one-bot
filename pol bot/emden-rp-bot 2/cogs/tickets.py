"""
Ticket-System: Button erstellt einen privaten Channel für den User, nur er und Staff
(Rolle Leitung) können ihn sehen. Mit "Schließen"-Button.
"""

import discord
from discord import app_commands
from discord.ext import commands

import config
from settings import get_setting


class TicketErstellenView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ticket erstellen", emoji="🎫", style=discord.ButtonStyle.primary, custom_id="ticket_erstellen")
    async def erstellen(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        kategorie = discord.utils.get(guild.categories, name=get_setting("channel_ticket_kategorie"))

        kanal_name = f"ticket-{interaction.user.name}".lower()
        vorhanden = discord.utils.get(guild.text_channels, name=kanal_name)
        if vorhanden:
            await interaction.response.send_message(
                f"Du hast bereits ein offenes Ticket: {vorhanden.mention}", ephemeral=True
            )
            return

        leitung_rolle = discord.utils.get(guild.roles, name=get_setting("rolle_leitung"))

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }
        if leitung_rolle:
            overwrites[leitung_rolle] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        ticket_channel = await guild.create_text_channel(
            name=kanal_name,
            category=kategorie,
            overwrites=overwrites,
        )

        embed = discord.Embed(
            title="🎫 Neues Ticket",
            description=f"Hallo {interaction.user.mention}! Beschreibe kurz dein Anliegen, "
            "ein Teammitglied meldet sich gleich bei dir.",
            color=0x3498db,
        )
        await ticket_channel.send(embed=embed, view=TicketSchliessenView())

        await interaction.response.send_message(f"✅ Ticket erstellt: {ticket_channel.mention}", ephemeral=True)


class TicketSchliessenView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ticket schließen", emoji="🔒", style=discord.ButtonStyle.danger, custom_id="ticket_schliessen")
    async def schliessen(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Dieses Ticket wird in 5 Sekunden geschlossen...")
        await interaction.channel.send("🔒 Ticket wird geschlossen.")
        import asyncio
        await asyncio.sleep(5)
        await interaction.channel.delete()


class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.add_view(TicketErstellenView())
        self.bot.add_view(TicketSchliessenView())

    @app_commands.command(name="ticket_panel", description="Postet das Ticket-Erstellen-Panel in diesen Channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎫 Support / Bewerbungsrückfragen",
            description="Klicke auf den Button unten, um ein privates Ticket zu erstellen.",
            color=0x3498db,
        )
        await interaction.channel.send(embed=embed, view=TicketErstellenView())
        await interaction.response.send_message("✅ Panel gepostet.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))
