"""
Ticket-System.

Panel in 🎫・ticket-erstellen mit einem Auswahlmenü für die Ticketarten
(konfigurierbar in server_config.json, Abschnitt "tickets").

Tickets sind ausschließlich für den Ersteller und das zuständige Team sichtbar.
"""

import datetime
import logging

import discord
from discord import app_commands
from discord.ext import commands

import server_config as sc
from checks import benoetigt_befehl
from config import IDX_SUPPORT
from database import get_connection
from logging_utils import log_mod

log = logging.getLogger("galaxy.tickets")

# Ticketarten aus server_config.json (farbe als int).
TICKET_TYPEN = {
    t["id"]: {
        "emoji": t["emoji"],
        "label": t["label"],
        "farbe": sc.hex_zu_int(t.get("farbe")),
    }
    for t in sc.ticket_typen()
}


def _ticket_id() -> str:
    """Erzeugt eine fortlaufende Ticket-ID: TKT-0001."""
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) AS c FROM tickets").fetchone()
    conn.close()
    return f"TKT-{row['c'] + 1:04d}"


class TicketSelect(discord.ui.Select):
    def __init__(self):
        optionen = [
            discord.SelectOption(
                label=v["label"], value=k, emoji=v["emoji"],
                description=f"Ein {v['label']}-Ticket erstellen",
            )
            for k, v in TICKET_TYPEN.items()
        ]
        super().__init__(
            placeholder="Wähle, worum es in deinem Ticket geht ...",
            min_values=1,
            max_values=1,
            options=optionen,
            custom_id="ticket_typ_auswahl",
        )

    async def callback(self, interaction: discord.Interaction):
        await _ticket_erstellen(interaction, self.values[0])


async def _ticket_erstellen(interaction: discord.Interaction, typ_key: str):
    guild = interaction.guild
    typ = TICKET_TYPEN.get(typ_key, TICKET_TYPEN["support"])
    user = interaction.user

    # Maximal ein offenes Ticket pro User
    conn = get_connection()
    vorhanden = conn.execute(
        "SELECT ticket_id, channel_id FROM tickets WHERE user_id = ? AND status = 'offen'", (user.id,)
    ).fetchone()
    if vorhanden:
        conn.close()
        kanal = guild.get_channel(int(vorhanden["channel_id"] or 0))
        hinweis = f"Du hast bereits ein offenes Ticket: {kanal.mention}" if kanal else \
                  f"Du hast bereits ein offenes Ticket: `{vorhanden['ticket_id']}`"
        await interaction.response.send_message(hinweis, ephemeral=True)
        return

    ticket_id = _ticket_id()
    conn.execute(
        "INSERT INTO tickets (ticket_id, user_id, typ, status, erstellt_am) VALUES (?, ?, ?, 'offen', ?)",
        (ticket_id, user.id, typ_key, datetime.datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()

    kategorie = discord.utils.get(guild.categories, name=sc.channel("kategorie_tickets"))
    support_rolle = discord.utils.get(guild.roles, name=sc.rolle_by_index(IDX_SUPPORT))

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, send_messages=True,
                                          attach_files=True, embed_links=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True,
                                              manage_channels=True, read_message_history=True),
    }
    if support_rolle:
        overwrites[support_rolle] = discord.PermissionOverwrite(
            view_channel=True, send_messages=True, manage_messages=True, read_message_history=True
        )

    kanal_name = f"ticket-{typ['emoji']}-{user.name}".lower()[:100]
    ticket_channel = await guild.create_text_channel(
        name=kanal_name, category=kategorie, overwrites=overwrites,
        topic=f"Ticket {ticket_id} – {typ['label']} – {user}",
    )

    conn = get_connection()
    conn.execute("UPDATE tickets SET channel_id = ? WHERE ticket_id = ?", (ticket_channel.id, ticket_id))
    conn.commit()
    conn.close()

    embed = discord.Embed(
        title=f"{typ['emoji']} Ticket {ticket_id} – {typ['label']}",
        description=(
            f"Hallo {user.mention}!\n\n"
            "Beschreibe bitte dein Anliegen so genau wie möglich. "
            "Ein Teammitglied meldet sich gleich bei dir.\n\n"
            "Nutze den Button unten, um das Ticket zu schließen, sobald dein Anliegen gelöst ist."
        ),
        color=typ["farbe"],
    )
    if support_rolle:
        embed.set_footer(text=f"Zuständig: {support_rolle.name}")
    await ticket_channel.send(content=user.mention, embed=embed, view=TicketSchliessenView())

    await log_mod(
        guild,
        title=f"{typ['emoji']} Ticket erstellt",
        description=f"{user.mention} hat ein **{typ['label']}**-Ticket erstellt: {ticket_channel.mention}",
        fields=[("Ticket-ID", ticket_id, True)],
    )

    await interaction.response.send_message(
        f"✅ Dein Ticket wurde erstellt: {ticket_channel.mention}", ephemeral=True
    )


class TicketSchliessenView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Ticket schließen", emoji="🔒", style=discord.ButtonStyle.danger,
        custom_id="ticket_schliessen",
    )
    async def schliessen(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            embed=discord.Embed(
                title="🔒 Ticket wird geschlossen",
                description="Dieses Ticket wird in 5 Sekunden geschlossen.",
                color=sc.farbe("neutral"),
            )
        )
        await _ticket_schliessen(interaction.channel, interaction.user)

    @discord.ui.button(
        label="Nutzer hinzufügen", emoji="➕", style=discord.ButtonStyle.secondary,
        custom_id="ticket_nutzer_hinzufuegen",
    )
    async def nutzer_hinzufuegen(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Gebe `/ticket hinzufuegen <nutzer>` ein, um jemanden zu diesem Ticket hinzuzufügen.",
            ephemeral=True,
        )


async def _ticket_schliessen(channel: discord.TextChannel, geschlossen_von: discord.Member):
    conn = get_connection()
    row = conn.execute("SELECT ticket_id, user_id FROM tickets WHERE channel_id = ?", (channel.id,)).fetchone()
    if row:
        conn.execute(
            "UPDATE tickets SET status = 'geschlossen', geschlossen_am = ? WHERE ticket_id = ?",
            (datetime.datetime.now().isoformat(), row["ticket_id"]),
        )
        conn.commit()
    conn.close()

    await channel.send(f"🔒 Ticket geschlossen von {geschlossen_von.mention}.")
    import asyncio
    await asyncio.sleep(5)
    try:
        await channel.delete(reason=f"Ticket geschlossen von {geschlossen_von}")
    except discord.NotFound:
        pass


class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        # Persistente Views: damit funktionieren die Buttons auch nach einem Bot-Neustart
        self.bot.add_view(TicketPanelView())
        self.bot.add_view(TicketSchliessenView())

    ticket_group = app_commands.Group(name="ticket", description="Ticket-System")

    @ticket_group.command(name="panel", description="Postet das Ticket-Panel in diesen Channel")
    @benoetigt_befehl("ticket.panel")
    async def panel(self, interaction: discord.Interaction):
        auswahl = "\n".join(
            f"{t['emoji']} **{t['label']}**" for t in TICKET_TYPEN.values()
        )
        embed = discord.Embed(
            title="🎫 Brauchst du Hilfe?",
            description=(
                "Wähle unten aus, worum es geht, und wir erstellen dir einen **privaten Channel**, "
                "in dem nur du und das zuständige Team schreiben können.\n\n"
                + auswahl
            ),
            color=sc.farbe("info"),
        )
        await interaction.channel.send(embed=embed, view=TicketPanelView())
        await interaction.response.send_message("✅ Ticket-Panel gepostet.", ephemeral=True)

    @ticket_group.command(name="hinzufuegen", description="Fügt einen Nutzer zum aktuellen Ticket hinzu")
    @benoetigt_befehl("ticket.hinzufuegen")
    async def hinzufuegen(self, interaction: discord.Interaction, nutzer: discord.Member):
        conn = get_connection()
        row = conn.execute("SELECT ticket_id FROM tickets WHERE channel_id = ?", (interaction.channel.id,)).fetchone()
        conn.close()
        if not row:
            await interaction.response.send_message("⚠️ Dieser Channel ist kein Ticket.", ephemeral=True)
            return
        await interaction.channel.set_permissions(
            nutzer, view_channel=True, send_messages=True, reason="Zum Ticket hinzugefügt"
        )
        await interaction.response.send_message(f"✅ {nutzer.mention} wurde zum Ticket hinzugefügt.", ephemeral=True)


class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))
