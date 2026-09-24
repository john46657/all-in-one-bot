"""
Vorschläge & Umfragen.

💡 Vorschläge: Panel in 💡・vorschläge, Button öffnet ein Modal → Embed mit
   👍/👎 Abstimmung. Das Team kann den Status setzen (Offen/Angenommen/Abgelehnt).
🗳️ Umfragen: /umfrage mit bis zu 8 Optionen, automatischer Laufzeit-Countdown,
   Double-Vote-Schutz und Auswertung nach Ablauf.
"""

import datetime
import json
import logging
import random
import string

import discord
from discord import app_commands
from discord.ext import commands, tasks

import config
from checks import hat_mindestens, IDX_ADMINISTRATION, IDX_MODERATION
from database import get_connection

log = logging.getLogger("galaxy.vorschlaege")

VORSCHLAG_STATUS = {
    "offen": ("🟡 Offen", config.FARBE_WARNUNG),
    "angenommen": ("🟢 Angenommen", config.FARBE_ERFOLG),
    "abgelehnt": ("🔴 Abgelehnt", config.FARBE_FEHLER),
}
UMFRAGEN_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]


def _jetzt() -> str:
    return datetime.datetime.now().isoformat()


# ---------------------------------------------------------------------------
# Vorschläge
# ---------------------------------------------------------------------------

class VorschlagModal(discord.ui.Modal, title="💡 Vorschlag einreichen"):
    titel = discord.ui.TextInput(label="Titel", placeholder="Worum geht es?", required=True, max_length=100)
    beschreibung = discord.ui.TextInput(
        label="Beschreibung", placeholder="Beschreibe deinen Vorschlag ...",
        style=discord.TextStyle.paragraph, required=True, max_length=1000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await _vorschlag_speichern(interaction, str(self.titel.value), str(self.beschreibung.value))


async def _vorschlag_speichern(interaction: discord.Interaction, titel: str, beschreibung: str):
    channel = interaction.channel
    embed = discord.Embed(title=f"💡 {titel}", description=beschreibung, color=config.FARBE_WARNUNG)
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
    embed.set_footer(text="Vorschlag – stimme mit 👍 / 👎 ab")
    nachricht = await channel.send(embed=embed, view=VorschlagAbstimmungView())

    conn = get_connection()
    conn.execute(
        "INSERT INTO vorschlaege (user_id, message_id, channel_id, titel, beschreibung, status, erstellt_am) "
        "VALUES (?, ?, ?, ?, ?, 'offen', ?)",
        (interaction.user.id, nachricht.id, channel.id, titel, beschreibung, _jetzt()),
    )
    conn.commit()
    conn.close()

    await interaction.response.send_message(
        "✅ Dein Vorschlag wurde gepostet. Das Team wird sich dazu äußern.", ephemeral=True
    )


class VorschlagAbstimmungView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(emoji="👍", style=discord.ButtonStyle.success, custom_id="vorschlag_hoch")
    async def hoch(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

    @discord.ui.button(emoji="👎", style=discord.ButtonStyle.danger, custom_id="vorschlag_runter")
    async def runter(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

    @discord.ui.button(label="Annehmen", style=discord.ButtonStyle.primary, custom_id="vorschlag_annehmen")
    async def annehmen(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _vorschlag_status_setzen(interaction, "angenommen")

    @discord.ui.button(label="Ablehnen", style=discord.ButtonStyle.secondary, custom_id="vorschlag_ablehnen")
    async def ablehnen(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _vorschlag_status_setzen(interaction, "abgelehnt")


async def _vorschlag_status_setzen(interaction: discord.Interaction, status: str):
    if not hat_mindestens(interaction.user, IDX_ADMINISTRATION):
        await interaction.response.send_message(
            "⚠️ Nur Team-Mitglieder ab 🔧 Administration können Vorschläge bewerten.", ephemeral=True
        )
        return

    label, farbe = VORSCHLAG_STATUS[status]
    conn = get_connection()
    conn.execute("UPDATE vorschlaege SET status = ? WHERE message_id = ?", (status, interaction.message.id))
    conn.commit()
    conn.close()

    embed = interaction.message.embeds[0]
    embed.color = farbe
    embed.set_footer(text=f"Vorschlag – {label}")
    await interaction.message.edit(embed=embed)
    await interaction.response.send_message(f"✅ Vorschlag als **{label}** markiert.", ephemeral=True)


class VorschlagPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Vorschlag einreichen", emoji="💡", style=discord.ButtonStyle.primary,
                       custom_id="vorschlag_eroeffnen")
    async def eroeffnen(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(VorschlagModal())


# ---------------------------------------------------------------------------
# Umfragen
# ---------------------------------------------------------------------------

def _umfrage_id() -> str:
    return "UMF-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


class UmfrageView(discord.ui.View):
    """Eine View pro Umfrage: Abstimmungs-Buttons + Beenden-Button."""

    def __init__(self, umfrage_id: str, optionen: list[dict]):
        super().__init__(timeout=None)
        self.umfrage_id = umfrage_id
        for i, opt in enumerate(optionen):
            button = discord.ui.Button(
                label=opt["label"][:80],
                emoji=opt.get("emoji") or UMFRAGEN_EMOJIS[i],
                style=discord.ButtonStyle.secondary,
                custom_id=f"umfrage_abstimmung:{umfrage_id}:{i}",
            )
            button.callback = self._stimme
            self.add_item(button)
        self.beenden_button = discord.ui.Button(
            label="Umfrage beenden", emoji="🏁", style=discord.ButtonStyle.danger,
            custom_id=f"umfrage_beenden:{umfrage_id}",
        )
        self.beenden_button.callback = self._beenden
        self.add_item(self.beenden_button)

    async def _stimme(self, interaction: discord.Interaction):
        # custom_id Format: umfrage_abstimmung:<UMF-ID>:<option_index>
        _, umfrage_id, option_index = interaction.custom_id.split(":")

        conn = get_connection()
        umfrage = conn.execute("SELECT aktiv FROM umfragen WHERE umfrage_id = ?", (umfrage_id,)).fetchone()
        if not umfrage or not umfrage["aktiv"]:
            conn.close()
            await interaction.response.send_message("⚠️ Diese Umfrage ist bereits beendet.", ephemeral=True)
            return

        vorhanden = conn.execute(
            "SELECT option_index FROM umfragen_stimmen WHERE umfrage_id = ? AND user_id = ?",
            (umfrage_id, interaction.user.id),
        ).fetchone()
        if vorhanden:
            conn.close()
            await interaction.response.send_message(
                "⚠️ Du hast schon abgestimmt. Mehrfachabstimmungen sind nicht erlaubt.", ephemeral=True
            )
            return

        conn.execute(
            "INSERT INTO umfragen_stimmen (umfrage_id, user_id, option_index, abgegeben_am) VALUES (?, ?, ?, ?)",
            (umfrage_id, interaction.user.id, int(option_index), _jetzt()),
        )
        conn.commit()
        conn.close()

        await interaction.response.send_message("✅ Deine Stimme wurde gezählt.", ephemeral=True)

    async def _beenden(self, interaction: discord.Interaction):
        if not hat_mindestens(interaction.user, IDX_MODERATION):
            await interaction.response.send_message(
                "⚠️ Nur Team-Mitglieder ab 🔨 Moderation können Umfragen beenden.", ephemeral=True
            )
            return
        await _umfrage_beenden(interaction.guild, interaction, self.umfrage_id)


async def _umfrage_beenden(guild: discord.Guild, interaction: discord.Interaction | None, umfrage_id: str):
    conn = get_connection()
    umfrage = conn.execute("SELECT * FROM umfragen WHERE umfrage_id = ?", (umfrage_id,)).fetchone()
    if not umfrage or not umfrage["aktiv"]:
        conn.close()
        if interaction:
            await interaction.response.send_message(
                "⚠️ Umfrage nicht gefunden oder bereits beendet.", ephemeral=True
            )
        return

    ergebnisse: dict[str, int] = json.loads(umfrage["ergebnisse"])
    optionen: list[dict] = json.loads(umfrage["optionen"])
    stimmen = conn.execute(
        "SELECT option_index, COUNT(*) AS c FROM umfragen_stimmen WHERE umfrage_id = ? GROUP BY option_index",
        (umfrage_id,),
    ).fetchall()
    conn.close()

    for s in stimmen:
        ergebnisse[str(s["option_index"])] = s["c"]

    gesamt = sum(ergebnisse.values())
    text = "\n".join(
        f"{optionen[i].get('emoji') or UMFRAGEN_EMOJIS[i]} **{optionen[i]['label']}** – "
        f"{ergebnisse.get(str(i), 0)} Stimme(n)"
        for i in range(len(optionen))
    )

    embed = discord.Embed(
        title=f"🏁 Umfrage beendet: {umfrage['frage']}",
        description=f"**{gesamt}** Stimme(n) insgesamt:\n\n{text}",
        color=config.FARBE_ERFOLG,
    )
    embed.set_footer(text=f"Umfrage-ID: {umfrage_id}")

    channel = guild.get_channel(int(umfrage["channel_id"] or 0))
    if channel:
        try:
            nachricht = await channel.fetch_message(int(umfrage["message_id"]))
            await nachricht.edit(embed=embed, view=None)
        except (discord.NotFound, discord.Forbidden):
            pass

    conn = get_connection()
    conn.execute(
        "UPDATE umfragen SET aktiv = 0, ergebnisse = ? WHERE umfrage_id = ?",
        (json.dumps(ergebnisse), umfrage_id),
    )
    conn.commit()
    conn.close()

    if interaction:
        await interaction.response.send_message("🏁 Umfrage beendet und ausgezählt.", ephemeral=True)


class Vorschlaege(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        # Persistente Views (funktionieren auch nach Neustart)
        self.bot.add_view(VorschlagAbstimmungView())
        self.bot.add_view(VorschlagPanelView())

        conn = get_connection()
        rows = conn.execute("SELECT umfrage_id, optionen FROM umfragen WHERE aktiv = 1").fetchall()
        conn.close()
        for r in rows:
            self.bot.add_view(UmfrageView(r["umfrage_id"], json.loads(r["optionen"])))

        self.umfrage_check.start()

    async def cog_unload(self):
        self.umfrage_check.cancel()

    vorschlag_group = app_commands.Group(name="vorschlag", description="Vorschlags-System")

    @vorschlag_group.command(name="panel", description="Postet das Vorschlags-Panel in diesen Channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="💡 Vorschläge",
            description=(
                "Du hast eine Idee, wie wir den Server besser machen können?\n\n"
                "Klicke auf den Button unten, reiche deinen Vorschlag ein und die Community "
                "kann mit 👍 / 👎 abstimmen. Das Team entscheidet dann über die Umsetzung."
            ),
            color=config.FARBE_INFO,
        )
        await interaction.channel.send(embed=embed, view=VorschlagPanelView())
        await interaction.response.send_message("✅ Vorschlags-Panel gepostet.", ephemeral=True)

    @app_commands.command(name="umfrage", description="Startet eine Umfrage mit bis zu 8 Antwortmöglichkeiten")
    @app_commands.describe(
        frage="Die Umfragefrage",
        optionen="Antworten, getrennt durch | (z. B. 'Ja|Nein|Vielleicht')",
        laufzeit_stunden="Wie lange läuft die Umfrage? (Standard 24)",
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def umfrage(
        self,
        interaction: discord.Interaction,
        frage: str,
        optionen: str,
        laufzeit_stunden: app_commands.Range[int, 1, 168] = 24,
    ):
        liste = [o.strip() for o in optionen.split("|") if o.strip()]
        if len(liste) < 2:
            await interaction.response.send_message(
                "⚠️ Mindestens 2 Antwortmöglichkeiten, getrennt durch `|`.", ephemeral=True
            )
            return
        if len(liste) > 8:
            await interaction.response.send_message("⚠️ Maximal 8 Antwortmöglichkeiten.", ephemeral=True)
            return

        umfrage_id = _umfrage_id()
        option_objekte = [{"label": o, "emoji": None} for o in liste]
        ablauf = discord.utils.utcnow() + datetime.timedelta(hours=laufzeit_stunden)

        embed = discord.Embed(
            title=f"🗳️ {frage}",
            description=(
                "\n".join(f"{UMFRAGEN_EMOJIS[i]} **{o}**" for i, o in enumerate(liste))
                + f"\n\n⏱️ Läuft bis {discord.utils.format_dt(ablauf, 'R')}"
            ),
            color=config.FARBE_INFO,
        )
        embed.set_footer(text=f"Umfrage-ID: {umfrage_id}")
        nachricht = await interaction.channel.send(embed=embed, view=UmfrageView(umfrage_id, option_objekte))

        conn = get_connection()
        conn.execute(
            "INSERT INTO umfragen (umfrage_id, user_id, message_id, channel_id, frage, optionen, ergebnisse, "
            "ablauf, aktiv, erstellt_am) VALUES (?, ?, ?, ?, ?, ?, '{}', ?, 1, ?)",
            (umfrage_id, interaction.user.id, nachricht.id, interaction.channel.id, frage,
             json.dumps(option_objekte), ablauf.isoformat(), _jetzt()),
        )
        conn.commit()
        conn.close()

        await interaction.response.send_message(
            f"✅ Umfrage gestartet (ID: `{umfrage_id}`), läuft {laufzeit_stunden} Stunde(n).", ephemeral=True
        )

    @tasks.loop(minutes=1)
    async def umfrage_check(self):
        """Beendet abgelaufene Umfragen automatisch und zählt sie aus."""
        conn = get_connection()
        rows = conn.execute(
            "SELECT umfrage_id, channel_id FROM umfragen WHERE aktiv = 1 AND ablauf <= ?",
            (discord.utils.utcnow().isoformat(),),
        ).fetchall()
        conn.close()

        for r in rows:
            for guild in self.bot.guilds:
                if guild.get_channel(int(r["channel_id"] or 0)):
                    await _umfrage_beenden(guild, None, r["umfrage_id"])
                    break

    @umfrage_check.before_loop
    async def vor_umfrage_check(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(Vorschlaege(bot))
