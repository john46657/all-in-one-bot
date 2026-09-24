"""
Moderation: Verwarnungen, Timeout, Kick, Ban.

Berechtigungen (nach Team-Hierarchie, siehe checks.py):
- /warn, /warnungen, /timeout  → ab 🔨 Moderation
- /kick, /ban                   → ab 🔧 Administration

Alle Aktionen landen in den Punishment-Logs, Verwarnungen zusätzlich im
internen Verwarnungen-Channel des Teams.
"""

import datetime
import logging

import discord
from discord import app_commands
from discord.ext import commands

import config
from checks import benoetigt_moderation, benoetigt_administration
from database import get_connection
from settings import get_setting
from logging_utils import log_punishment, log_mod

log = logging.getLogger("galaxy.moderation")


def _jetzt() -> str:
    return datetime.datetime.now().isoformat()


def _darf_bestaft_werden(moderator: discord.Member, ziel: discord.Member) -> bool:
    """Niemand darf jemanden mit höherem Rang bestrafen (Hierarchie-Schutz)."""
    if ziel.bot:
        return False
    if ziel.guild_permissions.administrator and not moderator.guild_permissions.owner:
        # Admins können nur vom Besitzer bestraft werden
        return moderator.id == ziel.guild.owner_id
    return moderator.top_role > ziel.top_role


async def _benachrichtige_user(ziel: discord.Member, titel: str, text: str):
    try:
        await ziel.send(embed=discord.Embed(title=titel, description=text, color=config.FARBE_FEHLER))
    except discord.Forbidden:
        pass  # DMs geschlossen – ignorieren


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    moderations_group = app_commands.Group(name="moderation", description="Moderations-Befehle")

    # --- Verwarnung --------------------------------------------------------

    @moderations_group.command(name="warn", description="Verwarnt ein Mitglied (ab 🔨 Moderation)")
    @app_commands.describe(mitglied="Das Mitglied", grund="Grund der Verwarnung")
    @benoetigt_moderation
    async def warn(self, interaction: discord.Interaction, mitglied: discord.Member, grund: str):
        if mitglied.id == interaction.user.id:
            await interaction.response.send_message("⚠️ Du kannst dich nicht selbst verwarnen.", ephemeral=True)
            return
        if not _darf_bestaft_werden(interaction.user, mitglied):
            await interaction.response.send_message(
                "⚠️ Du kannst dieses Mitglied nicht verwarnen (Rang zu hoch).", ephemeral=True
            )
            return

        conn = get_connection()
        cur = conn.execute(
            "INSERT INTO warnungen (user_id, moderator_id, grund, erstellt_am) VALUES (?, ?, ?, ?)",
            (mitglied.id, interaction.user.id, grund, _jetzt()),
        )
        anzahl = conn.execute(
            "SELECT COUNT(*) AS c FROM warnungen WHERE user_id = ?", (mitglied.id,)
        ).fetchone()["c"]
        conn.commit()
        conn.close()

        await _benachrichtige_user(
            mitglied,
            "⚠️ Verwarnung",
            f"Du wurdest auf **{interaction.guild.name}** verwarnt.\n**Grund:** {grund}\n"
            f"Aktuelle Verwarnungen: **{anzahl}**",
        )

        await log_punishment(
            interaction.guild,
            title="⚠️ Verwarnung",
            description=f"{mitglied.mention} wurde von {interaction.user.mention} verwarnt.",
            fields=[("Grund", grund, False), ("Verwarnungen gesamt", str(anzahl), True)],
        )

        await interaction.response.send_message(
            f"⚠️ {mitglied.mention} wurde verwarnt. (**{anzahl}** Verwarnung(en) insgesamt)", ephemeral=True
        )

    @moderations_group.command(name="warnungen", description="Zeigt alle Verwarnungen eines Mitglieds")
    @app_commands.describe(mitglied="Das Mitglied")
    @benoetigt_moderation
    async def warnungen(self, interaction: discord.Interaction, mitglied: discord.Member):
        conn = get_connection()
        rows = conn.execute(
            "SELECT grund, moderator_id, erstellt_am FROM warnungen WHERE user_id = ? ORDER BY erstellt_am DESC",
            (mitglied.id,),
        ).fetchall()
        conn.close()

        embed = discord.Embed(
            title=f"⚠️ Verwarnungen – {mitglied.display_name}",
            color=config.FARBE_WARNUNG,
        )
        if not rows:
            embed.description = "Keine Verwarnungen. ✅"
        else:
            embed.description = f"**{len(rows)}** Verwarnung(en):"
            for i, r in enumerate(rows, 1):
                datum = discord.utils.format_dt(discord.utils.parse_time(r["erstellt_am"]), "d")
                mod = interaction.guild.get_member(r["moderator_id"])
                embed.add_field(
                    name=f"#{i} – {datum}",
                    value=f"**Grund:** {r['grund']}\n**Von:** {mod or r['moderator_id']}",
                    inline=False,
                )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # --- Timeout -----------------------------------------------------------

    @moderations_group.command(name="timeout", description="Schickt ein Mitglied in den Timeout (ab 🔨 Moderation)")
    @app_commands.describe(
        mitglied="Das Mitglied",
        dauer="Dauer, z. B. '10m', '1h', '2h30m', '1d'",
        grund="Grund (optional)",
    )
    @benoetigt_moderation
    async def timeout(self, interaction: discord.Interaction, mitglied: discord.Member, dauer: str, grund: str = ""):
        if not _darf_bestaft_werden(interaction.user, mitglied):
            await interaction.response.send_message(
                "⚠️ Du kannst dieses Mitglied nicht timeouten (Rang zu hoch).", ephemeral=True
            )
            return

        sekunden = _parse_dauer(dauer)
        if sekunden is None or sekunden < 1 or sekunden > 2419200:  # max 28 Tage
            await interaction.response.send_message(
                "⚠️ Ungültige Dauer. Beispiele: `10m`, `1h`, `2h30m`, `1d` (max. 28 Tage).", ephemeral=True
            )
            return

        bis = discord.utils.utcnow() + datetime.timedelta(seconds=sekunden)
        try:
            await mitglied.timeout(bis, reason=f"{interaction.user}: {grund}")
        except discord.Forbidden:
            await interaction.response.send_message("⚠️ Keine Rechte für einen Timeout.", ephemeral=True)
            return

        conn = get_connection()
        conn.execute(
            "INSERT INTO moderation_aktionen (typ, user_id, moderator_id, grund, dauer, erstellt_am) "
            "VALUES ('timeout', ?, ?, ?, ?, ?)",
            (mitglied.id, interaction.user.id, grund, dauer, _jetzt()),
        )
        conn.commit()
        conn.close()

        await _benachrichtige_user(
            mitglied,
            "🔇 Timeout",
            f"Du wurdest für **{dauer}** auf **{interaction.guild.name}** in den Timeout geschickt.\n"
            f"**Grund:** {grund or 'Keine Angabe'}",
        )

        await log_punishment(
            interaction.guild,
            title="🔇 Timeout",
            description=f"{mitglied.mention} wurde von {interaction.user.mention} timeout.",
            fields=[("Dauer", dauer, True), ("Grund", grund or "Keine Angabe", False)],
        )
        await interaction.response.send_message(
            f"🔇 {mitglied.mention} ist für **{dauer}** im Timeout.", ephemeral=True
        )

    # --- Kick --------------------------------------------------------------

    @moderations_group.command(name="kick", description="Kickt ein Mitglied (ab 🔧 Administration)")
    @app_commands.describe(mitglied="Das Mitglied", grund="Grund (optional)")
    @benoetigt_administration
    async def kick(self, interaction: discord.Interaction, mitglied: discord.Member, grund: str = ""):
        if not _darf_bestaft_werden(interaction.user, mitglied):
            await interaction.response.send_message(
                "⚠️ Du kannst dieses Mitglied nicht kicken (Rang zu hoch).", ephemeral=True
            )
            return

        await _benachrichtige_user(
            mitglied,
            "👢 Kick",
            f"Du wurdest von **{interaction.guild.name}** gekickt.\n**Grund:** {grund or 'Keine Angabe'}",
        )

        try:
            await mitglied.kick(reason=f"{interaction.user}: {grund}")
        except discord.Forbidden:
            await interaction.response.send_message("⚠️ Keine Rechte zum Kicken.", ephemeral=True)
            return

        conn = get_connection()
        conn.execute(
            "INSERT INTO moderation_aktionen (typ, user_id, moderator_id, grund, dauer, erstellt_am) "
            "VALUES ('kick', ?, ?, ?, NULL, ?)",
            (mitglied.id, interaction.user.id, grund, _jetzt()),
        )
        conn.commit()
        conn.close()

        await log_punishment(
            interaction.guild,
            title="👢 Kick",
            description=f"{mitglied.mention} wurde von {interaction.user.mention} gekickt.",
            fields=[("Grund", grund or "Keine Angabe", False)],
        )
        await interaction.response.send_message(f"👢 {mitglied.mention} wurde gekickt.", ephemeral=True)

    # --- Ban ---------------------------------------------------------------

    @moderations_group.command(name="ban", description="Bannt ein Mitglied (ab 🔧 Administration)")
    @app_commands.describe(
        mitglied="Das Mitglied",
        grund="Grund (optional)",
        nachrichten_loeschen="Nachrichten der letzten Tage löschen (0-7)",
    )
    @benoetigt_administration
    async def ban(
        self,
        interaction: discord.Interaction,
        mitglied: discord.Member,
        grund: str = "",
        nachrichten_loeschen: app_commands.Range[int, 0, 7] = 0,
    ):
        if not _darf_bestaft_werden(interaction.user, mitglied):
            await interaction.response.send_message(
                "⚠️ Du kannst dieses Mitglied nicht bannen (Rang zu hoch).", ephemeral=True
            )
            return

        await _benachrichtige_user(
            mitglied,
            "🔨 Ban",
            f"Du wurdest von **{interaction.guild.name}** gebannt.\n**Grund:** {grund or 'Keine Angabe'}",
        )

        try:
            await mitglied.ban(
                reason=f"{interaction.user}: {grund}",
                delete_message_days=nachrichten_loeschen,
            )
        except discord.Forbidden:
            await interaction.response.send_message("⚠️ Keine Rechte zum Bannen.", ephemeral=True)
            return

        conn = get_connection()
        conn.execute(
            "INSERT INTO moderation_aktionen (typ, user_id, moderator_id, grund, dauer, erstellt_am) "
            "VALUES ('ban', ?, ?, ?, NULL, ?)",
            (mitglied.id, interaction.user.id, grund, _jetzt()),
        )
        conn.commit()
        conn.close()

        await log_punishment(
            interaction.guild,
            title="🔨 Ban",
            description=f"{mitglied.mention} wurde von {interaction.user.mention} gebannt.",
            fields=[("Grund", grund or "Keine Angabe", False)],
        )
        await interaction.response.send_message(f"🔨 {mitglied.mention} wurde gebannt.", ephemeral=True)


def _parse_dauer(eingabe: str) -> int | None:
    """Parst Angaben wie '10m', '1h', '2h30m', '1d' in Sekunden. None bei Fehler."""
    eingabe = (eingabe or "").strip().lower()
    if not eingabe:
        return None

    gesamt = 0
    rest = eingabe
    einheiten = {"d": 86400, "h": 3600, "m": 60, "s": 1}
    gefunden = False

    while rest:
        for einheit, faktor in einheiten.items():
            if einheit in rest:
                index = rest.index(einheit)
                try:
                    wert = int(rest[:index])
                except ValueError:
                    return None
                gesamt += wert * faktor
                rest = rest[index + 1:].strip()
                gefunden = True
                break
        else:
            return None  # keine bekannte Einheit mehr
    return gesamt if gefunden else None


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
