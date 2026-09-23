"""
Abmelden-System (nur für Teammitglieder):

- Ein Admin legt per /abmelden setup fest, WELCHE Rollen sich abmelden dürfen
  (mehrere Rollen gleichzeitig wählbar - entweder per Select-Menü oder per Rollen-ID).
- Wer eine dieser Rollen hat, kann sich mit /abmelden für einige Tage abmelden.
- Es wird ein Embed im Abmeldungen-Channel gepostet, das Mitglied erhält die
  Rolle "Abgemeldet" und nach Ablauf der Zeit wird diese Rolle automatisch wieder
  entfernt (Background-Task prüft alle 30 Minuten).
"""

import datetime
import logging

import discord
from discord import app_commands
from discord.ext import commands, tasks

from database import get_connection
from settings import get_setting

log = logging.getLogger("bot.abmelden")


# --------------------------------------------------------------------------------------
# Hilfsfunktionen
# --------------------------------------------------------------------------------------

def parse_datum(eingabe: str) -> datetime.date | None:
    """Parst DD.MM.YYYY oder DD.MM (aktuelles Jahr). Bei Fehler None."""
    eingabe = (eingabe or "").strip()
    for fmt in ("%d.%m.%Y", "%d.%m", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(eingabe, fmt).date()
        except ValueError:
            continue
    return None


def erlaube_rollen() -> list[int]:
    """Liefert die IDs aller Rollen, die sich abmelden dürfen."""
    conn = get_connection()
    rows = conn.execute("SELECT rolle_id FROM abmelden_rollen").fetchall()
    conn.close()
    return [int(r["rolle_id"]) for r in rows]


def darf_abmelden(member: discord.Member) -> bool:
    if member.guild_permissions.administrator:
        return True
    erlaubt = set(erlaube_rollen())
    return erlaubt.intersection({r.id for r in member.roles})


async def abgemeldete_rolle(guild: discord.Guild) -> discord.Role | None:
    return discord.utils.get(guild.roles, name=get_setting("rolle_abgemeldet"))


def _embed_base(title: str, farbe: int) -> discord.Embed:
    return discord.Embed(title=title, color=farbe)


# --------------------------------------------------------------------------------------
# Setup: Rollen auswählen, die sich abmelden dürfen (mehrere möglich)
# --------------------------------------------------------------------------------------

class AbmeldenRollenSelect(discord.ui.RoleSelect):
    def __init__(self, aktuelle: list[int]):
        super().__init__(
            placeholder="Wähle alle Rollen, die sich abmelden dürfen ...",
            min_values=0,
            max_values=25,
            default_values=[discord.Object(id=rid) for rid in aktuelle[:25]],
        )

    async def callback(self, interaction: discord.Interaction):
        gewaehlt = [r.id for r in self.values]
        conn = get_connection()
        conn.execute("DELETE FROM abmelden_rollen")
        conn.executemany(
            "INSERT INTO abmelden_rollen (rolle_id) VALUES (?)", [(rid,) for rid in gewaehlt]
        )
        conn.commit()
        conn.close()

        if gewaehlt:
            namen = [f"• <@&{rid}>" for rid in gewaehlt]
            text = "\n".join(namen)
            titel = "✅ Berechtigte Rollen aktualisiert"
            farbe = 0x2ecc71
        else:
            text = "Es sind **keine** Rollen berechtigt. Bitte wähle mindestens eine Rolle aus."
            titel = "⚠️ Keine Rollen ausgewählt"
            farbe = 0xf1c40f

        embed = _embed_base(titel, farbe)
        embed.description = text
        embed.set_footer(text=f"{len(gewaehlt)} Rolle(n) berechtigt")
        await interaction.response.edit_message(embed=embed, view=None)


class AbmeldenSetupView(discord.ui.View):
    def __init__(self, aktuelle: list[int]):
        super().__init__(timeout=300)
        self.add_item(AbmeldenRollenSelect(aktuelle))


# --------------------------------------------------------------------------------------
# Abmelden-Modal
# --------------------------------------------------------------------------------------

class AbmeldenModal(discord.ui.Modal, title="🚪 Abmelden - einige Tage abwesend"):
    grund = discord.ui.TextInput(
        label="Grund (kurz)",
        placeholder="z. B. Urlaub, Krankheit, Prüfungen ...",
        required=True,
        max_length=200,
    )
    von = discord.ui.TextInput(
        label="Von (TT.MM.JJJJ)",
        placeholder="z. B. 24.09.2026",
        required=True,
        max_length=20,
    )
    bis = discord.ui.TextInput(
        label="Bis (TT.MM.JJJJ)",
        placeholder="z. B. 28.09.2026",
        required=True,
        max_length=20,
    )
    vertretung = discord.ui.TextInput(
        label="Vertretung (optional)",
        placeholder="Wer übernimmt deine Aufgaben?",
        required=False,
        max_length=200,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await handle_abmelden(interaction, self)


async def handle_abmelden(interaction: discord.Interaction, modal: AbmeldenModal):
    member = interaction.user
    if not darf_abmelden(member):
        await interaction.response.send_message(
            "⚠️ Du bist nicht berechtigt, dich abzumelden. Nur ausgewählte Team-Rollen können das.",
            ephemeral=True,
        )
        return

    von = parse_datum(str(modal.von.value))
    bis = parse_datum(str(modal.bis.value))

    if not von or not bis:
        await interaction.response.send_message(
            "⚠️ Datumsformat ungültig. Bitte TT.MM.JJJJ verwenden, z. B. `24.09.2026`.",
            ephemeral=True,
        )
        return

    if bis < von:
        await interaction.response.send_message(
            "⚠️ Das Enddatum liegt vor dem Startdatum.", ephemeral=True
        )
        return

    # Laufende Abmeldung desselben Users blockieren
    conn = get_connection()
    vorhanden = conn.execute(
        "SELECT id FROM abmeldungen WHERE user_id = ? AND aktiv = 1", (member.id,)
    ).fetchone()
    if vorhanden:
        conn.close()
        await interaction.response.send_message(
            "⚠️ Du bist bereits abgemeldet. Beende die aktuelle Abmeldung erst mit "
            "`/abmelden entfernen`.",
            ephemeral=True,
        )
        return

    jetzt = datetime.datetime.now().isoformat()
    conn.execute(
        """INSERT INTO abmeldungen
           (user_id, von_datum, bis_datum, grund, vertretung, erstellt_am, aktiv)
           VALUES (?, ?, ?, ?, ?, ?, 1)""",
        (member.id, von.isoformat(), bis.isoformat(),
         str(modal.grund.value), str(modal.vertretung.value or "-"), jetzt),
    )
    conn.commit()
    conn.close()

    # Rolle vergeben
    rolle = await abgemeldete_rolle(interaction.guild)
    if rolle and rolle not in member.roles:
        try:
            await member.add_roles(rolle, reason="Abmeldung")
        except discord.Forbidden:
            log.warning("Keine Rechte, die Abgemeldet-Rolle zu vergeben.")

    # Embed in den Abmeldungen-Channel posten
    channel = discord.utils.get(
        interaction.guild.text_channels, name=get_setting("channel_abmeldungen")
    )
    if channel:
        embed = _embed_base("🚪 Team-Mitglied abgemeldet", 0xf39c12)
        embed.add_field(name="👤 Mitglied", value=member.mention, inline=True)
        embed.add_field(name="📅 Von", value=von.strftime("%d.%m.%Y"), inline=True)
        embed.add_field(name="📅 Bis", value=bis.strftime("%d.%m.%Y"), inline=True)
        embed.add_field(name="📝 Grund", value=str(modal.grund.value), inline=False)
        embed.add_field(
            name="🤝 Vertretung", value=str(modal.vertretung.value or "-"), inline=False
        )
        embed.set_footer(text="Das Team wurde automatisch informiert")
        nachricht = await channel.send(embed=embed)

        conn = get_connection()
        conn.execute(
            "UPDATE abmeldungen SET message_id = ?, channel_id = ? WHERE user_id = ? AND aktiv = 1",
            (nachricht.id, channel.id, member.id),
        )
        conn.commit()
        conn.close()

    tage = (bis - von).days + 1
    await interaction.response.send_message(
        f"✅ Du bist ab sofort für **{tage} Tag(e)** (bis {bis.strftime('%d.%m.%Y')}) abgemeldet. "
        "Das Team wurde informiert.",
        ephemeral=True,
    )


# --------------------------------------------------------------------------------------
# Cog
# --------------------------------------------------------------------------------------

class Abmelden(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        self.ablauf_check.start()

    async def cog_unload(self):
        self.ablauf_check.cancel()

    # --- Setup: berechtigte Rollen festlegen (Admin) -----------------------------------

    abmelden_group = app_commands.Group(name="abmelden", description="Team-Abmeldungen verwalten")

    @abmelden_group.command(name="setup", description="Legt fest, welche Rollen sich abmelden dürfen (mehrere möglich)")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction):
        aktuelle = erlaube_rollen()
        view = AbmeldenSetupView(aktuelle)
        embed = _embed_base("🚪 Abmelden-Setup", 0x3498db)
        embed.description = (
            "Wähle unten **alle Rollen**, die sich abmelden dürfen.\n"
            "Du kannst mehrere Rollen gleichzeitig auswählen.\n\n"
            f"Aktuell berechtigt: **{len(aktuelle)}** Rolle(n)."
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @abmelden_group.command(name="rolle_hinzufuegen", description="Fügt eine berechtigte Rolle per ID hinzu")
    @app_commands.describe(rolle_id="Die Discord-Rollen-ID (Rechtsklick auf die Rolle → ID kopieren)")
    @app_commands.checks.has_permissions(administrator=True)
    async def rolle_hinzufuegen(self, interaction: discord.Interaction, rolle_id: str):
        try:
            rid = int(rolle_id.strip().replace("<@&", "").replace(">", ""))
        except ValueError:
            await interaction.response.send_message("⚠️ Ungültige Rollen-ID.", ephemeral=True)
            return

        rolle = interaction.guild.get_role(rid)
        if rolle is None:
            await interaction.response.send_message(
                "⚠️ Rolle auf diesem Server nicht gefunden.", ephemeral=True
            )
            return

        conn = get_connection()
        conn.execute(
            "INSERT OR IGNORE INTO abmelden_rollen (rolle_id) VALUES (?)", (rid,)
        )
        conn.commit()
        conn.close()

        await interaction.response.send_message(
            f"✅ Rolle {rolle.mention} wurde zur Abmelden-Berechtigung hinzugefügt.",
            ephemeral=True,
        )

    @abmelden_group.command(name="rolle_entfernen", description="Entfernt eine berechtigte Rolle per ID")
    @app_commands.describe(rolle_id="Die Discord-Rollen-ID")
    @app_commands.checks.has_permissions(administrator=True)
    async def rolle_entfernen(self, interaction: discord.Interaction, rolle_id: str):
        try:
            rid = int(rolle_id.strip().replace("<@&", "").replace(">", ""))
        except ValueError:
            await interaction.response.send_message("⚠️ Ungültige Rollen-ID.", ephemeral=True)
            return

        conn = get_connection()
        conn.execute("DELETE FROM abmelden_rollen WHERE rolle_id = ?", (rid,))
        conn.commit()
        conn.close()

        await interaction.response.send_message("✅ Rolle entfernt.", ephemeral=True)

    @abmelden_group.command(name="berechtigt", description="Zeigt alle Rollen, die sich abmelden dürfen")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def berechtigt(self, interaction: discord.Interaction):
        ids = erlaube_rollen()
        embed = _embed_base("🚪 Berechtigte Rollen", 0x3498db)
        if ids:
            embed.description = "\n".join(f"• <@&{rid}> (`{rid}`)" for rid in ids)
        else:
            embed.description = "Es sind aktuell **keine** Rollen berechtigt.\nNutze `/abmelden setup`."
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # --- Abmelden / Abmeldung beenden ---------------------------------------------------

    @abmelden_group.command(name="jetzt", description="Melde dich für einige Tage ab (nur berechtigte Team-Rollen)")
    async def jetzt(self, interaction: discord.Interaction):
        if not darf_abmelden(interaction.user):
            await interaction.response.send_message(
                "⚠️ Du bist nicht berechtigt, dich abzumelden.", ephemeral=True
            )
            return
        await interaction.response.send_modal(AbmeldenModal())

    @abmelden_group.command(name="entfernen", description="Beendet deine aktuelle Abmeldung vorzeitig")
    @app_commands.describe(mitglied="Nur Admins: Abmeldung eines anderen Mitglieds beenden")
    async def entfernen(self, interaction: discord.Interaction, mitglied: discord.Member = None):
        ziel = mitglied or interaction.user
        ist_admin = interaction.user.guild_permissions.administrator

        if mitglied and not ist_admin:
            await interaction.response.send_message(
                "⚠️ Du darfst nur deine eigene Abmeldung beenden.", ephemeral=True
            )
            return

        conn = get_connection()
        row = conn.execute(
            "SELECT id, message_id, channel_id FROM abmeldungen WHERE user_id = ? AND aktiv = 1",
            (ziel.id,),
        ).fetchone()
        if not row:
            conn.close()
            await interaction.response.send_message(
                "⚠️ Es gibt keine aktive Abmeldung.", ephemeral=True
            )
            return

        conn.execute("UPDATE abmeldungen SET aktiv = 0, beendet_am = ? WHERE id = ?",
                     (datetime.datetime.now().isoformat(), row["id"]))
        conn.commit()
        conn.close()

        rolle = await abgemeldete_rolle(interaction.guild)
        if rolle and rolle in ziel.roles:
            try:
                await ziel.remove_roles(rolle, reason="Abmeldung beendet")
            except discord.Forbidden:
                pass

        # Ursprüngliche Nachricht aktualisieren
        if row["channel_id"] and row["message_id"]:
            channel = interaction.guild.get_channel(int(row["channel_id"]))
            if channel:
                try:
                    nachricht = await channel.fetch_message(int(row["message_id"]))
                    await nachricht.edit(content=f"~~Abmeldung~~ **Beendet** von {interaction.user.mention}.",
                                         embeds=[])
                except (discord.NotFound, discord.Forbidden):
                    pass

        await interaction.response.send_message(
            f"✅ Abmeldung von {ziel.mention} wurde beendet. Die Rolle wurde entfernt.",
            ephemeral=True,
        )

    @abmelden_group.command(name="liste", description="Zeigt alle aktuell abgemeldeten Teammitglieder")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def liste(self, interaction: discord.Interaction):
        conn = get_connection()
        rows = conn.execute(
            "SELECT user_id, von_datum, bis_datum, grund FROM abmeldungen WHERE aktiv = 1 "
            "ORDER BY bis_datum ASC"
        ).fetchall()
        conn.close()

        embed = _embed_base("🚪 Aktuelle Abmeldungen", 0xf39c12)
        if not rows:
            embed.description = "Aktuell ist niemand abgemeldet. ✅"
        else:
            embed.description = f"**{len(rows)}** Teammitglied(er) aktuell abgemeldet:"
            for r in rows:
                bis = datetime.date.fromisoformat(r["bis_datum"])
                verbleib = (bis - datetime.date.today()).days
                embed.add_field(
                    name=f"<@{r['user_id']}>",
                    value=f"📅 bis **{bis.strftime('%d.%m.%Y')}** "
                          f"({verbleib} Tag(e) verbleibend)\n📝 {r['grund']}",
                    inline=False,
                )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # --- Background-Task: abgelaufene Abmeldungen automatisch beenden -------------------

    @tasks.loop(minutes=30)
    async def ablauf_check(self):
        conn = get_connection()
        rows = conn.execute(
            "SELECT id, user_id, bis_datum, message_id, channel_id FROM abmeldungen WHERE aktiv = 1"
        ).fetchall()
        conn.close()

        heute = datetime.date.today()
        for r in rows:
            bis = datetime.date.fromisoformat(r["bis_datum"])
            if bis >= heute:
                continue

            for guild in self.bot.guilds:
                member = guild.get_member(int(r["user_id"]))
                if member is None:
                    continue

                rolle = await abgemeldete_rolle(guild)
                if rolle and rolle in member.roles:
                    try:
                        await member.remove_roles(rolle, reason="Abmeldung abgelaufen")
                    except discord.Forbidden:
                        pass

                if r["channel_id"] and r["message_id"]:
                    channel = guild.get_channel(int(r["channel_id"]))
                    if channel:
                        try:
                            nachricht = await channel.fetch_message(int(r["message_id"]))
                            await nachricht.edit(
                                content=f"✅ **Abmeldung abgelaufen** - {member.mention} ist wieder da.",
                                embeds=[],
                            )
                        except (discord.NotFound, discord.Forbidden):
                            pass
                break

        conn = get_connection()
        conn.execute(
            "UPDATE abmeldungen SET aktiv = 0, beendet_am = ? WHERE aktiv = 1 AND bis_datum < ?",
            (datetime.datetime.now().isoformat(), heute.isoformat()),
        )
        conn.commit()
        conn.close()

    @ablauf_check.before_loop
    async def vor_ablauf_check(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(Abmelden(bot))
