"""
Team-Abwesenheitssystem (nach Master-Prompt).

Panel in 📅・team-abwesenheit mit 5 Buttons:
  💤 Abwesenheit melden · 📅 Meine Abwesenheit · 🔄 Abwesenheit verlängern
  ✅ Rückkehr melden · 🚨 Kurzfristig abmelden

Ablauf: 🟡 Eingereicht → (Teamleitung) 🟢 Genehmigt / 🔴 Abgelehnt →
       zum Start 🟣 Aktiv (+ 💤 Abwesend Rolle) → Erinnerung →
       bei Rückkehr/Ablauf ⚫ Beendet (Rolle entfernt)

Verlängerungen müssen von der Teamleitung bestätigt werden.
Alles wird in 💤・abwesenheits-logs protokolliert, aktive Abwesenheiten
werden in 📅・abwesenheitsübersicht angezeigt (nur Team).

Datenschutz: als Grund genügt "Privater Grund" – es werden keine
gesundheitlichen oder privaten Details abgefragt.
"""

import datetime
import logging
import re

import discord
from discord import app_commands
from discord.ext import commands, tasks

import server_config as sc
from checks import hat_befehl, benoetigt_befehl
from database import get_connection, get_config, set_config
from logging_utils import log_abwesenheit

log = logging.getLogger("galaxy.abwesenheit")

GRUENDE = [(g["label"], g["emoji"]) for g in sc.gruende()]
ERREICHBARKEIT = [(e["label"], e["id"], e["emoji"]) for e in sc.erreichbarkeit()]
STATUS_ANZEIGE = {
    "eingereicht": "🟡 Eingereicht",
    "genehmigt": "🟢 Genehmigt",
    "abgelehnt": "🔴 Abgelehnt",
    "verlaengert": "🔵 Verlängert",
    "aktiv": "🟣 Aktiv",
    "beendet": "⚫ Beendet",
}
_STATUS_FARBEN = {
    "eingereicht": "gelb", "genehmigt": "gruen", "abgelehnt": "rot",
    "verlaengert": "blau", "aktiv": "lila", "beendet": "grau",
}


def _status_farbe(status: str) -> int:
    return sc.status_farbe(_STATUS_FARBEN.get(status, "gelb"))


def _jetzt() -> str:
    return datetime.datetime.now().isoformat()


def _parse_datum(eingabe: str) -> datetime.date | None:
    eingabe = (eingabe or "").strip()
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(eingabe, fmt).date()
        except ValueError:
            continue
    # "DD.MM" ohne Jahr: aktuelles Jahr ergänzen.
    # (Python 3.15+ verbietet %d ohne Jahresangabe, daher explizit ergänzen.)
    if re.fullmatch(r"\d{1,2}\.\d{1,2}", eingabe):
        try:
            return datetime.datetime.strptime(
                f"{eingabe}.{datetime.date.today().year}", "%d.%m.%Y"
            ).date()
        except ValueError:
            return None
    return None


def _format_datum(datum: datetime.date | str | None) -> str:
    if not datum:
        return "–"
    if isinstance(datum, str):
        try:
            datum = datetime.date.fromisoformat(datum)
        except ValueError:
            return str(datum)
    return datum.strftime("%d.%m.%Y")


def _naechste_abwesenheit_id() -> str:
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) AS c FROM abwesenheiten").fetchone()
    conn.close()
    return f"ABW-{row['c'] + 1:04d}"


def _abwesenheit_id_aus_footer(embed: discord.Embed) -> str | None:
    text = embed.footer.text or ""
    match = re.search(r"ABW-\d+", text)
    return match.group(0) if match else None


def _abwesend_rolle(guild: discord.Guild) -> discord.Role | None:
    name = sc.rolle("abwesend")
    rolle = discord.utils.get(guild.roles, name=name)
    if rolle is None:
        log.warning("Abwesenheits-Rolle nicht gefunden: %s", name)
    return rolle


def _team_rolle(member: discord.Member) -> str:
    """Höchste Team-Rolle des Members für die Anzeige."""
    namen = {r.name for r in member.roles}
    for name in sc.hierarchie():
        if name in namen:
            return name
    return "Team"


# ---------------------------------------------------------------------------
# Zwischengespeicherte Daten für den mehrstufigen Dialog
# ---------------------------------------------------------------------------

class AbwesenheitDaten:
    def __init__(self, user: discord.Member, typ: str = "normal"):
        self.user_id = user.id
        self.user_name = user.display_name
        self.team_rolle = _team_rolle(user)
        self.typ = typ
        self.grund = ""
        self.von = None
        self.bis = None
        self.rueckkehr = None
        self.hinweis = ""
        self.uebergabe_erforderlich = False
        self.uebergabe_text = ""
        self.erreichbarkeit = ""
        self.dauer = ""


# ---------------------------------------------------------------------------
# Stufe 1: Grund auswählen (normal)
# ---------------------------------------------------------------------------

class GrundSelect(discord.ui.Select):
    def __init__(self, daten: AbwesenheitDaten):
        optionen = [
            discord.SelectOption(label=label, value=label, emoji=emoji)
            for label, emoji in GRUENDE
        ]
        super().__init__(
            placeholder="Wähle den Grund deiner Abwesenheit ...",
            options=optionen, custom_id="abwesenheit_grund",
        )
        self.daten = daten

    async def callback(self, interaction: discord.Interaction):
        self.daten.grund = self.values[0]
        await interaction.response.send_modal(AbwesenheitDatenModal(self.daten))


# ---------------------------------------------------------------------------
# Stufe 2: Daten eingeben (normal)
# ---------------------------------------------------------------------------

class AbwesenheitDatenModal(discord.ui.Modal, title="💤 Abwesenheit melden"):
    von = discord.ui.TextInput(label="Beginn (TT.MM.JJJJ)", placeholder="z. B. 24.09.2026", required=True, max_length=20)
    bis = discord.ui.TextInput(label="Ende (TT.MM.JJJJ)", placeholder="z. B. 28.09.2026", required=True, max_length=20)
    rueckkehr = discord.ui.TextInput(
        label="Voraussichtliche Rückkehr (TT.MM.JJJJ)", placeholder="z. B. 28.09.2026",
        required=True, max_length=20,
    )
    hinweis = discord.ui.TextInput(
        label="Optionaler Hinweis", placeholder="z. B. Vertretung, wichtige Infos ...",
        required=False, max_length=500,
    )

    def __init__(self, daten: AbwesenheitDaten):
        super().__init__()
        self.daten = daten

    async def on_submit(self, interaction: discord.Interaction):
        daten = self.daten
        daten.von = _parse_datum(str(self.von.value))
        daten.bis = _parse_datum(str(self.bis.value))
        daten.rueckkehr = _parse_datum(str(self.rueckkehr.value))
        daten.hinweis = str(self.hinweis.value or "").strip()

        if not daten.von or not daten.bis or not daten.rueckkehr:
            await interaction.response.send_message(
                "⚠️ Datumsformat ungültig. Bitte TT.MM.JJJJ verwenden (z. B. `24.09.2026`). "
                "Starte bitte neu über 💤 Abwesenheit melden.",
                ephemeral=True,
            )
            return
        if daten.bis < daten.von:
            await interaction.response.send_message(
                "⚠️ Das Enddatum liegt vor dem Startdatum. Bitte neu starten.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            embed=_uebergabe_frage_embed(daten),
            view=UebergabeView(daten),
            ephemeral=True,
        )


def _uebergabe_frage_embed(daten: AbwesenheitDaten) -> discord.Embed:
    min_w = sc.wert("abwesenheit", "min_woerter") or 50
    max_w = sc.wert("abwesenheit", "max_woerter") or 250
    embed = discord.Embed(title="📋 Aufgabenübergabe", color=sc.farbe("info"))
    embed.description = (
        "Ist während deiner Abwesenheit eine **Aufgabenübergabe** erforderlich?\n\n"
        f"Falls ja, beschreibe bitte in **{min_w}–{max_w} Wörtern**:\n"
        "• Welche Aufgaben\n• Bis wann sie erledigt werden müssen\n"
        "• Wer sie übernimmt\n• Wichtige Informationen"
    )
    return embed


class UebergabeView(discord.ui.View):
    def __init__(self, daten: AbwesenheitDaten):
        super().__init__(timeout=600)
        self.daten = daten

    @discord.ui.button(label="Ja, Übergabe erforderlich", emoji="✅",
                       style=discord.ButtonStyle.primary, custom_id="abwesenheit_uebergabe_ja")
    async def ja(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.daten.uebergabe_erforderlich = True
        await interaction.response.send_modal(UebergabeModal(self.daten))

    @discord.ui.button(label="Nein, nicht erforderlich", emoji="❌",
                       style=discord.ButtonStyle.secondary, custom_id="abwesenheit_uebergabe_nein")
    async def nein(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.daten.uebergabe_erforderlich = False
        await interaction.response.send_message(
            embed=_erreichbarkeit_embed(self.daten),
            view=ErreichbarkeitView(self.daten),
            ephemeral=True,
        )


class UebergabeModal(discord.ui.Modal, title="📋 Aufgabenübergabe (50–250 Wörter)"):
    text = discord.ui.TextInput(
        label="Übergabe", placeholder="Aufgaben, Fristen, Vertretung, wichtige Infos ...",
        style=discord.TextStyle.paragraph, required=True, max_length=2000,
    )

    def __init__(self, daten: AbwesenheitDaten):
        super().__init__()
        self.daten = daten

    async def on_submit(self, interaction: discord.Interaction):
        min_w = sc.wert("abwesenheit", "min_woerter") or 50
        max_w = sc.wert("abwesenheit", "max_woerter") or 250
        worte = _zaehle_woerter(str(self.text.value))
        if worte < min_w or worte > max_w:
            await interaction.response.send_message(
                f"⚠️ Dein Übergabe-Text enthält **{worte} Wörter**. "
                f"Erlaubt sind **{min_w}–{max_w} Wörter**. Bitte über den Button erneut versuchen.",
                ephemeral=True,
            )
            return
        self.daten.uebergabe_text = str(self.text.value).strip()
        await interaction.response.send_message(
            embed=_erreichbarkeit_embed(self.daten),
            view=ErreichbarkeitView(self.daten),
            ephemeral=True,
        )


# ---------------------------------------------------------------------------
# Stufe 3: Erreichbarkeit
# ---------------------------------------------------------------------------

def _erreichbarkeit_embed(daten: AbwesenheitDaten) -> discord.Embed:
    embed = discord.Embed(title="📡 Erreichbarkeit", color=sc.farbe("info"))
    embed.description = "Bist du während deiner Abwesenheit erreichbar?"
    return embed


class ErreichbarkeitView(discord.ui.View):
    def __init__(self, daten: AbwesenheitDaten):
        super().__init__(timeout=600)
        self.add_item(ErreichbarkeitSelect(daten))


class ErreichbarkeitSelect(discord.ui.Select):
    def __init__(self, daten: AbwesenheitDaten):
        optionen = [
            discord.SelectOption(label=label, value=value, emoji=emoji)
            for label, value, emoji in ERREICHBARKEIT
        ]
        super().__init__(placeholder="Wie erreichbar bist du?", options=optionen,
                         custom_id="abwesenheit_erreichbarkeit", min_values=1, max_values=1)
        self.daten = daten

    async def callback(self, interaction: discord.Interaction):
        self.daten.erreichbarkeit = self.values[0]
        await _abwesenheit_speichern(interaction, self.daten)


# ---------------------------------------------------------------------------
# Kurzfristige Abwesenheit
# ---------------------------------------------------------------------------

class KurzfristigModal(discord.ui.Modal, title="🚨 Kurzfristig abmelden"):
    von = discord.ui.TextInput(label="Beginn (TT.MM.JJJJ)", placeholder="z. B. 24.09.2026",
                               required=True, max_length=20)
    dauer = discord.ui.TextInput(label="Voraussichtliche Dauer", placeholder="z. B. 2 Tage",
                                 required=True, max_length=50)
    hinweis = discord.ui.TextInput(label="Optionaler Hinweis", required=False, max_length=500)

    def __init__(self, daten: AbwesenheitDaten):
        super().__init__()
        self.daten = daten

    async def on_submit(self, interaction: discord.Interaction):
        daten = self.daten
        daten.von = _parse_datum(str(self.von.value))
        daten.dauer = str(self.dauer.value).strip()
        daten.hinweis = str(self.hinweis.value or "").strip()
        daten.grund = "Kurzfristige Abwesenheit"

        if not daten.von:
            await interaction.response.send_message(
                "⚠️ Datumsformat ungültig. Bitte TT.MM.JJJJ verwenden.", ephemeral=True
            )
            return

        await interaction.response.send_message(
            embed=_erreichbarkeit_embed(daten),
            view=ErreichbarkeitView(daten),
            ephemeral=True,
        )


# ---------------------------------------------------------------------------
# Speichern + Panel-Nachricht
# ---------------------------------------------------------------------------

def _abwesenheit_embed(daten: AbwesenheitDaten, abwesenheit_id: str, status: str) -> discord.Embed:
    embed = discord.Embed(
        title=f"💤 Abwesenheit – {daten.user_name}",
        color=_status_farbe(status),
    )
    embed.add_field(name="👤 Mitglied", value=f"<@{daten.user_id}>", inline=True)
    embed.add_field(name="🏷️ Team", value=daten.team_rolle, inline=True)
    embed.add_field(name="📡 Erreichbarkeit", value=daten.erreichbarkeit or "–", inline=True)
    embed.add_field(name="📅 Von", value=_format_datum(daten.von), inline=True)
    embed.add_field(name="📅 Bis", value=_format_datum(daten.bis), inline=True)
    embed.add_field(name="🔄 Rückkehr", value=_format_datum(daten.rueckkehr), inline=True)
    embed.add_field(name="📝 Grund", value=daten.grund, inline=False)
    if daten.hinweis:
        embed.add_field(name="💬 Hinweis", value=daten.hinweis, inline=False)
    if daten.uebergabe_erforderlich and daten.uebergabe_text:
        embed.add_field(name="📋 Aufgabenübergabe", value=daten.uebergabe_text, inline=False)
    embed.set_footer(text=f"Abwesenheits-ID: {abwesenheit_id} · Status: {STATUS_ANZEIGE[status]}")
    return embed


async def _abwesenheit_speichern(interaction: discord.Interaction, daten: AbwesenheitDaten):
    if not hat_befehl(interaction.user, "abwesenheit.nutzen"):
        await interaction.response.send_message(
            "⚠️ Das Abwesenheitssystem ist nur für Teammitglieder.", ephemeral=True
        )
        return

    guild = interaction.guild
    abwesenheit_id = _naechste_abwesenheit_id()

    # Kurzfristige Abwesenheiten werden direkt aktiv (kein Genehmigungsprozess)
    status = "aktiv" if daten.typ == "kurzfristig" else "eingereicht"

    conn = get_connection()
    conn.execute(
        """INSERT INTO abwesenheiten
           (abwesenheit_id, user_id, team_rolle, typ, von_datum, bis_datum, rueckkehr_datum,
            grund, erreichbarkeit, uebergabe_erforderlich, uebergabe_text, status, erstellt_am)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (abwesenheit_id, daten.user_id, daten.team_rolle, daten.typ,
         daten.von.isoformat(), daten.bis.isoformat() if daten.bis else None,
         daten.rueckkehr.isoformat() if daten.rueckkehr else None,
         daten.grund, daten.erreichbarkeit,
         1 if daten.uebergabe_erforderlich else 0, daten.uebergabe_text or None,
         status, _jetzt()),
    )
    conn.commit()
    conn.close()

    # Bei kurzfristiger Abwesenheit sofort die Rolle vergeben
    if status == "aktiv":
        await _rolle_vergeben(guild, daten.user_id)

    # Panel-Nachricht im Team-Channel (mit Genehmigungs-Buttons bei normalen Anträgen)
    channel = discord.utils.get(guild.text_channels, name=sc.channel("team_abwesenheit"))
    if channel:
        embed = _abwesenheit_embed(daten, abwesenheit_id, status)
        view = AbwesenheitGenehmigungView() if status == "eingereicht" else None
        if view is None:
            embed.description = "Diese Abwesenheit wurde **kurzfristig** gemeldet und ist sofort aktiv."
        nachricht = await channel.send(embed=embed, view=view)

        conn = get_connection()
        conn.execute(
            "UPDATE abwesenheiten SET panel_message_id = ?, panel_channel_id = ? WHERE abwesenheit_id = ?",
            (nachricht.id, channel.id, abwesenheit_id),
        )
        conn.commit()
        conn.close()

    # Log
    tage = (daten.bis - daten.von).days + 1 if daten.bis else None
    meldepflicht_ab = int(sc.wert("abwesenheit", "meldepflicht_ab_tagen") or 3)
    hinweis = ""
    if tage is not None:
        if tage >= meldepflicht_ab:
            hinweis = f"\n\nℹ️ Ab {meldepflicht_ab} Tagen ist eine Abwesenheit grundsätzlich meldepflichtig – danke, dass du dich gemeldet hast!"
        else:
            hinweis = f"\n\nℹ️ Weniger als {meldepflicht_ab} Tage: eine Meldung ist freiwillig, aber willkommen."

    await log_abwesenheit(
        guild,
        title=f"💤 Abwesenheit eingereicht: {abwesenheit_id}",
        description=f"<@{daten.user_id}> hat sich abgemeldet.{hinweis}",
        fields=[
            ("Zeitraum", f"{_format_datum(daten.von)} – {_format_datum(daten.bis)}", True),
            ("Status", STATUS_ANZEIGE[status], True),
            ("Grund", daten.grund, True),
        ],
        farbe=_status_farbe(status),
    )

    await interaction.response.send_message(
        f"✅ Deine Abwesenheit wurde gespeichert (**{abwesenheit_id}**).",
        ephemeral=True,
    )

    # ÜBERSICHT aktualisieren
    await _uebersicht_aktualisieren(guild)


async def _rolle_vergeben(guild: discord.Guild, user_id: int):
    rolle = _abwesend_rolle(guild)
    member = guild.get_member(user_id)
    if rolle and member and rolle not in member.roles:
        try:
            await member.add_roles(rolle, reason="Abwesenheit aktiv")
        except discord.Forbidden:
            log.warning("Keine Rechte, die Abwesenheits-Rolle zu vergeben.")


async def _rolle_entfernen(guild: discord.Guild, user_id: int):
    rolle = _abwesend_rolle(guild)
    member = guild.get_member(user_id)
    if rolle and member and rolle in member.roles:
        try:
            await member.remove_roles(rolle, reason="Abwesenheit beendet")
        except discord.Forbidden:
            log.warning("Keine Rechte, die Abwesenheits-Rolle zu entfernen.")


# ---------------------------------------------------------------------------
# Genehmigung / Ablehnung (Teamleitung)
# ---------------------------------------------------------------------------

class AbwesenheitGenehmigungView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Genehmigen", emoji="✅", style=discord.ButtonStyle.success,
                       custom_id="abwesenheit_genehmigen")
    async def genehmigen(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not hat_befehl(interaction.user, "abwesenheit.genehmigen"):
            await interaction.response.send_message(
                "⚠️ Du darfst keine Abwesenheiten genehmigen.", ephemeral=True
            )
            return
        abwesenheit_id = _abwesenheit_id_aus_footer(interaction.message.embeds[0])
        if not abwesenheit_id:
            await interaction.response.send_message("⚠️ Abwesenheits-ID nicht gefunden.", ephemeral=True)
            return
        await _genehmigen(interaction, abwesenheit_id)

    @discord.ui.button(label="Ablehnen", emoji="✖️", style=discord.ButtonStyle.danger,
                       custom_id="abwesenheit_ablehnen")
    async def ablehnen(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not hat_befehl(interaction.user, "abwesenheit.genehmigen"):
            await interaction.response.send_message(
                "⚠️ Du darfst keine Abwesenheiten ablehnen.", ephemeral=True
            )
            return
        abwesenheit_id = _abwesenheit_id_aus_footer(interaction.message.embeds[0])
        if not abwesenheit_id:
            await interaction.response.send_message("⚠️ Abwesenheits-ID nicht gefunden.", ephemeral=True)
            return
        await _ablehnen(interaction, abwesenheit_id)


def _abwesenheit_laden(abwesenheit_id: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM abwesenheiten WHERE abwesenheit_id = ?", (abwesenheit_id,)).fetchone()
    conn.close()
    return row


def _verlaengerung_laden(abwesenheit_id: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM abwesenheit_verlaengerungen WHERE abwesenheit_id = ? AND status = 'eingereicht' "
        "ORDER BY erstellt_am DESC LIMIT 1",
        (abwesenheit_id,),
    ).fetchone()
    conn.close()
    return row


def _embed_aktualisieren(nachricht: discord.Message, row, zusatz=""):
    embed = nachricht.embeds[0]
    farbe = _status_farbe(row["status"])
    embed.color = farbe
    embed.set_footer(
        text=f"Abwesenheits-ID: {row['abwesenheit_id']} · Status: {STATUS_ANZEIGE[row['status']]}"
    )
    if zusatz:
        embed.description = zusatz
    return embed


async def _genehmigen(interaction: discord.Interaction, abwesenheit_id: str):
    guild = interaction.guild
    row = _abwesenheit_laden(abwesenheit_id)
    if not row:
        await interaction.response.send_message("⚠️ Abwesenheit nicht gefunden.", ephemeral=True)
        return

    # Falls eine Verlängerung aussteht: diese bestätigen
    verlaengerung = _verlaengerung_laden(abwesenheit_id) if row["status"] != "eingereicht" else None
    if verlaengerung:
        conn = get_connection()
        conn.execute("UPDATE abwesenheit_verlaengerungen SET status = 'genehmigt', entschieden_am = ? WHERE id = ?",
                     (_jetzt(), verlaengerung["id"]))
        conn.execute(
            "UPDATE abwesenheiten SET bis_datum = ?, rueckkehr_datum = ?, status = 'verlaengert', "
            "erinnert = 0 WHERE abwesenheit_id = ?",
            (verlaengerung["neues_enddatum"], verlaengerung["neues_enddatum"], abwesenheit_id),
        )
        conn.commit()
        conn.close()

        await log_abwesenheit(
            guild,
            title=f"🔄 Verlängerung genehmigt: {abwesenheit_id}",
            description=f"Neues Enddatum: **{_format_datum(verlaengerung['neues_enddatum'])}** "
                        f"(genehmigt von {interaction.user.mention})",
            farbe=_status_farbe("verlaengert"),
        )
        await _user_benachrichtigen(guild, row["user_id"],
                                    f"🔄 Deine Abwesenheit **{abwesenheit_id}** wurde verlängert bis "
                                    f"**{_format_datum(verlaengerung['neues_enddatum'])}**.")
        await interaction.response.send_message("✅ Verlängerung genehmigt.", ephemeral=True)
    elif row["status"] == "eingereicht":
        conn = get_connection()
        conn.execute(
            "UPDATE abwesenheiten SET status = 'genehmigt', genehmigt_von = ?, genehmigt_am = ? "
            "WHERE abwesenheit_id = ?",
            (interaction.user.id, _jetzt(), abwesenheit_id),
        )
        conn.commit()
        conn.close()

        await log_abwesenheit(
            guild,
            title=f"✅ Abwesenheit genehmigt: {abwesenheit_id}",
            description=f"Genehmigt von {interaction.user.mention}.",
            farbe=_status_farbe("genehmigt"),
        )
        await _user_benachrichtigen(
            guild, row["user_id"],
            f"✅ Deine Abwesenheit **{abwesenheit_id}** wurde genehmigt. "
            f"Sie wird am {_format_datum(row['von_datum'])} automatisch aktiv.",
        )
        await interaction.response.send_message("✅ Abwesenheit genehmigt.", ephemeral=True)
    else:
        await interaction.response.send_message(
            "⚠️ Diese Abwesenheit kann nicht mehr genehmigt werden (Status: "
            f"{STATUS_ANZEIGE[row['status']]}).", ephemeral=True
        )
        return

    # Panel-Nachricht aktualisieren (Buttons entfernen)
    await _panel_nachricht_aktualisieren(guild, row, interaktion=interaction)

    # Sofort aktiv, wenn der Start in der Vergangenheit liegt
    await _uebersicht_aktualisieren(guild)


async def _ablehnen(interaction: discord.Interaction, abwesenheit_id: str):
    guild = interaction.guild
    row = _abwesenheit_laden(abwesenheit_id)
    if not row:
        await interaction.response.send_message("⚠️ Abwesenheit nicht gefunden.", ephemeral=True)
        return

    conn = get_connection()
    conn.execute("UPDATE abwesenheiten SET status = 'abgelehnt' WHERE abwesenheit_id = ?", (abwesenheit_id,))
    conn.execute("UPDATE abwesenheit_verlaengerungen SET status = 'abgelehnt', entschieden_am = ? "
                 "WHERE abwesenheit_id = ? AND status = 'eingereicht'", (_jetzt(), abwesenheit_id))
    conn.commit()
    conn.close()

    await log_abwesenheit(
        guild,
        title=f"🔴 Abwesenheit abgelehnt: {abwesenheit_id}",
        description=f"Abgelehnt von {interaction.user.mention}.",
        farbe=_status_farbe("abgelehnt"),
    )
    await _user_benachrichtigen(
        guild, row["user_id"],
        f"🔴 Deine Abwesenheit **{abwesenheit_id}** wurde leider abgelehnt. "
        "Bitte melde dich bei der Serverleitung, falls es Fragen gibt.",
    )

    await _panel_nachricht_aktualisieren(guild, row, interaktion=interaction)
    await _uebersicht_aktualisieren(guild)
    await interaction.response.send_message("🔴 Abwesenheit abgelehnt.", ephemeral=True)


async def _panel_nachricht_aktualisieren(guild: discord.Guild, row, interaktion: discord.Interaction):
    """Aktualisiert die Panel-Nachricht einer Abwesenheit und entfernt die Buttons."""
    if not row["panel_channel_id"] or not row["panel_message_id"]:
        return
    channel = guild.get_channel(int(row["panel_channel_id"]))
    if not channel:
        return
    try:
        nachricht = await channel.fetch_message(int(row["panel_message_id"]))
        _embed_aktualisieren(nachricht, row)
        await nachricht.edit(embed=nachricht.embeds[0], view=None)
    except (discord.NotFound, discord.Forbidden):
        pass


async def _user_benachrichtigen(guild: discord.Guild, user_id: int, text: str):
    member = guild.get_member(user_id)
    if not member:
        return
    try:
        await member.send(embed=discord.Embed(description=text, color=sc.farbe("info")))
    except discord.Forbidden:
        pass


# ---------------------------------------------------------------------------
# Verlängerung
# ---------------------------------------------------------------------------

class VerlaengerungModal(discord.ui.Modal, title="🔄 Abwesenheit verlängern"):
    neues_ende = discord.ui.TextInput(
        label="Neues Enddatum (TT.MM.JJJJ)", placeholder="z. B. 30.09.2026", required=True, max_length=20,
    )
    hinweis = discord.ui.TextInput(
        label="Optionaler Hinweis", required=False, max_length=500,
    )

    def __init__(self, abwesenheit_id: str):
        super().__init__()
        self.abwesenheit_id = abwesenheit_id

    async def on_submit(self, interaction: discord.Interaction):
        neues_ende = _parse_datum(str(self.neues_ende.value))
        if not neues_ende:
            await interaction.response.send_message(
                "⚠️ Datumsformat ungültig. Bitte TT.MM.JJJJ verwenden.", ephemeral=True
            )
            return

        row = _abwesenheit_laden(self.abwesenheit_id)
        if not row or row["status"] in ("beendet", "abgelehnt"):
            await interaction.response.send_message(
                "⚠️ Diese Abwesenheit kann nicht verlängert werden.", ephemeral=True
            )
            return
        if neues_ende <= datetime.date.fromisoformat(row["bis_datum"]):
            await interaction.response.send_message(
                "⚠️ Das neue Enddatum muss nach dem aktuellen Enddatum liegen.", ephemeral=True
            )
            return

        conn = get_connection()
        conn.execute(
            "INSERT INTO abwesenheit_verlaengerungen (abwesenheit_id, neues_enddatum, hinweis, status, erstellt_am) "
            "VALUES (?, ?, ?, 'eingereicht', ?)",
            (self.abwesenheit_id, neues_ende.isoformat(), str(self.hinweis.value or "").strip(), _jetzt()),
        )
        conn.commit()
        conn.close()

        # Neue Panel-Nachricht mit Genehmigungs-Buttons
        channel = discord.utils.get(
            interaction.guild.text_channels, name=sc.channel("team_abwesenheit")
        )
        if channel:
            embed = discord.Embed(
                title=f"🔄 Verlängerung beantragt: {self.abwesenheit_id}",
                description=(
                    f"<@{row['user_id']}> möchte seine Abwesenheit verlängern.\n\n"
                    f"**Aktuelles Ende:** {_format_datum(row['bis_datum'])}\n"
                    f"**Neues Ende:** {neues_ende.strftime('%d.%m.%Y')}"
                ),
                color=_status_farbe("verlaengert"),
            )
            if self.hinweis.value:
                embed.add_field(name="Hinweis", value=str(self.hinweis.value), inline=False)
            embed.set_footer(text=f"Abwesenheits-ID: {self.abwesenheit_id}")
            await channel.send(embed=embed, view=AbwesenheitGenehmigungView())

        await log_abwesenheit(
            interaction.guild,
            title=f"🔄 Verlängerung beantragt: {self.abwesenheit_id}",
            description=f"<@{row['user_id']}> → neues Enddatum **{neues_ende.strftime('%d.%m.%Y')}** "
                        f"(wartet auf Bestätigung durch die Serverleitung)",
            farbe=_status_farbe("verlaengert"),
        )
        await interaction.response.send_message(
            "✅ Verlängerung beantragt. Die Serverleitung muss sie bestätigen.", ephemeral=True
        )


def _zaehle_woerter(text: str) -> int:
    return len([w for w in (text or "").split() if w])


# ---------------------------------------------------------------------------
# Haupt-Panel
# ---------------------------------------------------------------------------

class AbwesenheitPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Abwesenheit melden", emoji="💤", style=discord.ButtonStyle.primary,
                       custom_id="abwesenheit_melden")
    async def melden(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not hat_befehl(interaction.user, "abwesenheit.nutzen"):
            await interaction.response.send_message(
                "⚠️ Das Abwesenheitssystem ist nur für Teammitglieder.", ephemeral=True
            )
            return
        embed = discord.Embed(title="💤 Grund auswählen", color=sc.farbe("info"))
        embed.description = "Warum bist du abwesend? Dein Grund wird nicht öffentlich angezeigt."
        await interaction.response.send_message(
            embed=embed, view=GrundSelectView(AbwesenheitDaten(interaction.user)), ephemeral=True
        )

    @discord.ui.button(label="Meine Abwesenheit", emoji="📅", style=discord.ButtonStyle.secondary,
                       custom_id="abwesenheit_meine")
    async def meine(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _meine_abwesenheit(interaction)

    @discord.ui.button(label="Abwesenheit verlängern", emoji="🔄", style=discord.ButtonStyle.secondary,
                       custom_id="abwesenheit_verlaengern")
    async def verlaengern(self, interaction: discord.Interaction, button: discord.ui.Button):
        conn = get_connection()
        row = conn.execute(
            "SELECT abwesenheit_id, von_datum, bis_datum FROM abwesenheiten "
            "WHERE user_id = ? AND status IN ('genehmigt', 'aktiv', 'verlaengert') "
            "ORDER BY erstellt_am DESC LIMIT 1",
            (interaction.user.id,),
        ).fetchone()
        conn.close()

        if not row:
            await interaction.response.send_message(
                "⚠️ Du hast keine aktive Abwesenheit, die verlängert werden könnte.", ephemeral=True
            )
            return
        await interaction.response.send_modal(VerlaengerungModal(row["abwesenheit_id"]))

    @discord.ui.button(label="Rückkehr melden", emoji="✅", style=discord.ButtonStyle.success,
                       custom_id="abwesenheit_rueckkehr")
    async def rueckkehr(self, interaction: discord.Interaction, button: discord.ui.Button):
        await _rueckkehr_melden(interaction)

    @discord.ui.button(label="Kurzfristig abmelden", emoji="🚨", style=discord.ButtonStyle.danger,
                       custom_id="abwesenheit_kurzfristig")
    async def kurzfristig(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not hat_befehl(interaction.user, "abwesenheit.nutzen"):
            await interaction.response.send_message(
                "⚠️ Das Abwesenheitssystem ist nur für Teammitglieder.", ephemeral=True
            )
            return
        await interaction.response.send_modal(
            KurzfristigModal(AbwesenheitDaten(interaction.user, typ="kurzfristig"))
        )


class GrundSelectView(discord.ui.View):
    def __init__(self, daten: AbwesenheitDaten):
        super().__init__(timeout=600)
        self.add_item(GrundSelect(daten))


async def _meine_abwesenheit(interaction: discord.Interaction):
    conn = get_connection()
    aktiv = conn.execute(
        "SELECT * FROM abwesenheiten WHERE user_id = ? AND status NOT IN ('beendet', 'abgelehnt') "
        "ORDER BY erstellt_am DESC",
        (interaction.user.id,),
    ).fetchall()
    conn.close()

    embed = discord.Embed(title="📅 Meine Abwesenheiten", color=sc.farbe("info"))
    if not aktiv:
        embed.description = "Du hast aktuell keine aktive Abwesenheit. 🎉"
    else:
        embed.description = f"**{len(aktiv)}** aktive Abwesenheit(en):"
        for r in aktiv:
            embed.add_field(
                name=f"{r['abwesenheit_id']} – {STATUS_ANZEIGE[r['status']]}",
                value=(f"📅 {_format_datum(r['von_datum'])} – {_format_datum(r['bis_datum'])}\n"
                       f"📝 {r['grund']} · 📡 {r['erreichbarkeit'] or '–'}"),
                inline=False,
            )
    await interaction.response.send_message(embed=embed, ephemeral=True)


async def _rueckkehr_melden(interaction: discord.Interaction):
    guild = interaction.guild
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM abwesenheiten WHERE user_id = ? AND status IN ('aktiv', 'genehmigt', 'verlaengert') "
        "ORDER BY erstellt_am DESC LIMIT 1",
        (interaction.user.id,),
    ).fetchone()
    if not row:
        conn.close()
        await interaction.response.send_message(
            "⚠️ Du hast keine aktive Abwesenheit, die beendet werden könnte.", ephemeral=True
        )
        return

    conn.execute("UPDATE abwesenheiten SET status = 'beendet', beendet_am = ? WHERE id = ?",
                 (_jetzt(), row["id"]))
    conn.commit()
    conn.close()

    await _rolle_entfernen(guild, interaction.user.id)

    # Teamleitung informieren
    channel = discord.utils.get(guild.text_channels, name=sc.channel("team_abwesenheit"))
    if channel:
        embed = discord.Embed(
            title=f"✅ Rückkehr gemeldet: {row['abwesenheit_id']}",
            description=f"{interaction.user.mention} ist wieder da! "
                        f"Die Abwesenheit wurde beendet und die Rolle entfernt.",
            color=_status_farbe("beendet"),
        )
        embed.set_footer(text=f"Abwesenheits-ID: {row['abwesenheit_id']}")
        await channel.send(embed=embed)

    await log_abwesenheit(
        guild,
        title=f"✅ Rückkehr gemeldet: {row['abwesenheit_id']}",
        description=f"{interaction.user.mention} hat seine Abwesenheit vorzeitig beendet.",
        farbe=_status_farbe("beendet"),
    )

    await _panel_nachricht_aktualisieren(guild, row, None)
    await _uebersicht_aktualisieren(guild)
    await interaction.response.send_message(
        "✅ Willkommen zurück! Deine Abwesenheit wurde beendet und die Rolle entfernt.", ephemeral=True
    )


# ---------------------------------------------------------------------------
# Abwesenheitsübersicht (nur Team)
# ---------------------------------------------------------------------------

async def _uebersicht_aktualisieren(guild: discord.Guild):
    channel = discord.utils.get(
        guild.text_channels, name=sc.channel("abwesenheitsuebersicht")
    )
    if not channel:
        return

    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM abwesenheiten WHERE status IN ('aktiv', 'genehmigt', 'verlaengert') "
        "ORDER BY von_datum ASC"
    ).fetchall()
    conn.close()

    embed = discord.Embed(title="💤 Aktuelle Abwesenheiten", color=sc.farbe("info"))
    if not rows:
        embed.description = "Aktuell ist niemand abwesend. 🎉"
    else:
        embed.description = f"**{len(rows)}** Abwesenheit(en) aktiv:"
        for r in rows:
            member = guild.get_member(int(r["user_id"]))
            name = member.display_name if member else f"<@{r['user_id']}>"
            embed.add_field(
                name=f"{name} – {STATUS_ANZEIGE[r['status']]}",
                value=(f"Team: {r['team_rolle']}\n"
                       f"Von: {_format_datum(r['von_datum'])}  Bis: {_format_datum(r['bis_datum'])}\n"
                       f"📡 {r['erreichbarkeit'] or '–'}"),
                inline=False,
            )
    embed.set_footer(text="Diese Übersicht ist nur für das Team sichtbar.")

    nachricht_id = get_config("abwesenheit_uebersicht_message_id")
    if nachricht_id:
        try:
            nachricht = await channel.fetch_message(int(nachricht_id))
            await nachricht.edit(embed=embed)
            return
        except (discord.NotFound, discord.Forbidden):
            pass
    nachricht = await channel.send(embed=embed)
    set_config("abwesenheit_uebersicht_message_id", str(nachricht.id))


# ---------------------------------------------------------------------------
# Background-Task: Aktivierung, Erinnerung, automatisches Beenden
# ---------------------------------------------------------------------------

class Abwesenheit(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.add_view(AbwesenheitPanelView())
        self.bot.add_view(AbwesenheitGenehmigungView())
        self.abwesenheits_check.start()

    async def cog_unload(self):
        self.abwesenheits_check.cancel()

    abwesenheit_group = app_commands.Group(name="abwesenheit", description="Team-Abwesenheitssystem")

    @abwesenheit_group.command(name="panel", description="Postet das Abwesenheits-Panel in diesen Channel")
    @benoetigt_befehl("abwesenheit.panel")
    async def panel(self, interaction: discord.Interaction):
        meldepflicht_ab = sc.wert("abwesenheit", "meldepflicht_ab_tagen") or 3
        embed = discord.Embed(
            title="💤 Team-Abwesenheit",
            description=(
                "Du bist mehrere Tage nicht verfügbar?\n"
                "Melde deine Abwesenheit hier an.\n"
                "Private Details sind nicht erforderlich.\n\n"
                f"**Ab {meldepflicht_ab} Kalendertagen** soll eine Abwesenheit grundsätzlich gemeldet werden. "
                "Kürzere Abwesenheiten können freiwillig gemeldet werden."
            ),
            color=sc.farbe("info"),
        )
        await interaction.channel.send(embed=embed, view=AbwesenheitPanelView())
        await interaction.response.send_message("✅ Abwesenheits-Panel gepostet.", ephemeral=True)
        await _uebersicht_aktualisieren(interaction.guild)

    @abwesenheit_group.command(name="übersicht", description="Zeigt alle aktuellen Abwesenheiten (Team)")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def uebersicht(self, interaction: discord.Interaction):
        await _uebersicht_aktualisieren(interaction.guild)
        await interaction.response.send_message("✅ Übersicht aktualisiert.", ephemeral=True)

    @tasks.loop(minutes=1)
    async def abwesenheits_check(self):
        heute = datetime.date.today()
        erinnerung_vor = int(sc.wert("abwesenheit", "erinnerung_vor_tagen") or 1)

        for guild in self.bot.guilds:
            conn = get_connection()
            rows = conn.execute("SELECT * FROM abwesenheiten").fetchall()
            conn.close()

            for r in rows:
                von = datetime.date.fromisoformat(r["von_datum"]) if r["von_datum"] else None
                bis = datetime.date.fromisoformat(r["bis_datum"]) if r["bis_datum"] else None

                # Genehmigt → zum Start aktivieren
                if r["status"] == "genehmigt" and von and von <= heute:
                    conn = get_connection()
                    conn.execute("UPDATE abwesenheiten SET status = 'aktiv' WHERE id = ?", (r["id"],))
                    conn.commit()
                    conn.close()
                    await _rolle_vergeben(guild, int(r["user_id"]))
                    await log_abwesenheit(
                        guild, title=f"🟣 Abwesenheit aktiv: {r['abwesenheit_id']}",
                        description=f"<@{r['user_id']}> ist ab heute abwesend (bis {_format_datum(bis)}). "
                                    f"Die Rolle {sc.rolle('abwesend')} wurde vergeben.",
                        farbe=_status_farbe("aktiv"),
                    )
                    continue

                # Aktiv → erinnern & automatisch beenden
                if r["status"] == "aktiv" and bis:
                    if not r["erinnert"] and (bis - datetime.timedelta(days=erinnerung_vor)) <= heute:
                        conn = get_connection()
                        conn.execute("UPDATE abwesenheiten SET erinnert = 1 WHERE id = ?", (r["id"],))
                        conn.commit()
                        conn.close()
                        await _user_benachrichtigen(
                            guild, int(r["user_id"]),
                            f"⏰ Deine Abwesenheit **{r['abwesenheit_id']}** endet am "
                            f"**{_format_datum(bis)}**. Bitte denke an deine Rückkehr!",
                        )
                    elif bis < heute:
                        conn = get_connection()
                        conn.execute(
                            "UPDATE abwesenheiten SET status = 'beendet', beendet_am = ? WHERE id = ?",
                            (_jetzt(), r["id"]),
                        )
                        conn.commit()
                        conn.close()
                        await _rolle_entfernen(guild, int(r["user_id"]))
                        await log_abwesenheit(
                            guild, title=f"⚫ Abwesenheit beendet: {r['abwesenheit_id']}",
                            description=f"<@{r['user_id']}> ist wieder verfügbar. "
                                        "Die Abwesenheits-Rolle wurde automatisch entfernt.",
                            farbe=_status_farbe("beendet"),
                        )

            await _uebersicht_aktualisieren(guild)

    @abwesenheits_check.before_loop
    async def vor_abwesenheits_check(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(Abwesenheit(bot))
