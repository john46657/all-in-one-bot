"""
Einstellungen: Server-Konfiguration live aus Discord verwalten.

Alles wird in server_config.json gespeichert und greift sofort – ohne Neustart:
- /einstellungen anzeigen     – aktuelle Konfiguration ansehen
- /einstellungen neu_laden    – manuelle Änderungen an der JSON einlesen
- /einstellungen channel      – Channel-Namen anpassen
- /einstellungen rolle        – Rollen-Namen anpassen
- /einstellungen berechtigung – mindesteste Rolle pro Befehl festlegen
- /einstellungen automod      – AutoMod-Grenzen
- /einstellungen abwesenheit  – Abwesenheits-Regeln
- /einstellungen willkommen   – Willkommensnachricht
"""

import logging

import discord
from discord import app_commands
from discord.ext import commands

import server_config as sc
from checks import benoetigt_befehl

log = logging.getLogger("galaxy.einstellungen")


def _channel_choices() -> list[app_commands.Choice[str]]:
    return [app_commands.Choice(name=k, value=k) for k in sc.daten().get("channels", {})]


def _rolle_choices() -> list[app_commands.Choice[str]]:
    return [app_commands.Choice(name=k, value=k) for k in sc.daten().get("rollen", {}) if k != "hierarchie"]


def _hierarchie_choices() -> list[app_commands.Choice[str]]:
    return [app_commands.Choice(name=r, value=r) for r in sc.hierarchie()]


class Einstellungen(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    einstellungen_group = app_commands.Group(
        name="einstellungen", description="Server-Konfiguration verwalten (Serverleitung)"
    )

    # --- Übersicht ----------------------------------------------------------

    @einstellungen_group.command(name="anzeigen", description="Zeigt die aktuelle Konfiguration")
    @benoetigt_befehl("einstellungen.verwalten")
    async def anzeigen(self, interaction: discord.Interaction):
        daten = sc.daten()
        embed = discord.Embed(
            title="⚙️ Server-Konfiguration",
            description=f"Version `{daten.get('version', 1)}` · `{sc.PFAD.split('/')[-1]}`",
            color=sc.farbe("info"),
        )

        channels = daten.get("channels", {})
        embed.add_field(
            name="📺 Channels",
            value="\n".join(f"`{k}`: {v}" for k, v in channels.items()) or "–",
            inline=False,
        )

        rollen = {k: v for k, v in daten.get("rollen", {}).items() if k != "hierarchie"}
        embed.add_field(
            name="🏷️ Rollen",
            value="\n".join(f"`{k}`: {v}" for k, v in rollen.items()) or "–",
            inline=False,
        )

        automod = daten.get("automod", {})
        embed.add_field(
            name="🛡️ AutoMod",
            value="\n".join(f"`{k}`: {v}" for k, v in automod.items()) or "–",
            inline=False,
        )

        abwesenheit = {
            k: v for k, v in daten.get("abwesenheit", {}).items()
            if k not in ("gruende", "erreichbarkeit")
        }
        embed.add_field(
            name="💤 Abwesenheit",
            value="\n".join(f"`{k}`: {v}" for k, v in abwesenheit.items()) or "–",
            inline=False,
        )

        embed.add_field(
            name="🔐 Berechtigungen (Befehl → Rolle)",
            value="\n".join(f"`{k}` → {v}" for k, v in daten.get("berechtigungen", {}).items()) or "–",
            inline=False,
        )
        embed.set_footer(text="Änderungen mit /einstellungen ... greifen sofort.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # --- Neu laden ----------------------------------------------------------

    @einstellungen_group.command(name="neu_laden", description="Lädt server_config.json neu (nach manueller Bearbeitung)")
    @benoetigt_befehl("einstellungen.verwalten")
    async def neu_laden(self, interaction: discord.Interaction):
        sc.neu_laden()
        log.info("server_config.json neu geladen (durch %s).", interaction.user)
        await interaction.response.send_message(
            "✅ `server_config.json` wurde neu geladen.", ephemeral=True
        )

    # --- Channel ------------------------------------------------------------

    @einstellungen_group.command(name="channel", description="Ändert einen Channel- (oder Kategorie-)Namen")
    @app_commands.describe(
        key="Welcher Channel?",
        name="Neuer Name (exact so, wie der Channel im Server heißt)",
    )
    @app_commands.choices(key=_channel_choices())
    @benoetigt_befehl("einstellungen.verwalten")
    async def channel(self, interaction: discord.Interaction, key: app_commands.Choice[str], name: str):
        name = name.strip()
        if not name:
            await interaction.response.send_message("⚠️ Der Name darf nicht leer sein.", ephemeral=True)
            return
        sc.setze("channels", key.value, name)
        await interaction.response.send_message(
            f"✅ Channel **{key.value}** ist jetzt `{name}`.", ephemeral=True
        )

    # --- Rolle --------------------------------------------------------------

    @einstellungen_group.command(name="rolle", description="Ändert einen Rollen-Namen")
    @app_commands.describe(
        key="Welche Rolle?",
        name="Neuer Name (exakt so, wie die Rolle im Server heißt)",
    )
    @app_commands.choices(key=_rolle_choices())
    @benoetigt_befehl("einstellungen.verwalten")
    async def rolle(self, interaction: discord.Interaction, key: app_commands.Choice[str], name: str):
        name = name.strip()
        if not name:
            await interaction.response.send_message("⚠️ Der Name darf nicht leer sein.", ephemeral=True)
            return
        sc.setze("rollen", key.value, name)
        await interaction.response.send_message(
            f"✅ Rolle **{key.value}** ist jetzt `{name}`.", ephemeral=True
        )

    # --- Berechtigung -------------------------------------------------------

    @einstellungen_group.command(name="berechtigung", description="Legt die mindesteste Rolle für einen Befehl fest")
    @app_commands.describe(
        befehl="Der Befehl (z. B. moderation.ban)",
        rolle="Ab dieser Rolle (inklusive) ist der Befehl erlaubt",
    )
    @app_commands.choices(rolle=_hierarchie_choices())
    @benoetigt_befehl("einstellungen.verwalten")
    async def berechtigung(
        self,
        interaction: discord.Interaction,
        befehl: str,
        rolle: app_commands.Choice[str],
    ):
        befehl = befehl.strip().lower()
        if befehl not in (sc.daten().get("berechtigungen") or {}):
            await interaction.response.send_message(
                f"⚠️ Unbekannter Befehl: `{befehl}`. Mit /einstellungen anzeigen siehst du alle.",
                ephemeral=True,
            )
            return
        sc.setze("berechtigungen", befehl, rolle.value)
        log.info("Berechtigung %s -> %s (durch %s).", befehl, rolle.value, interaction.user)
        await interaction.response.send_message(
            f"✅ **{befehl}** ist ab der Rolle **{rolle.value}** (oder höher) erlaubt.",
            ephemeral=True,
        )

    @berechtigung.autocomplete("befehl")
    async def _berechtigung_autocomplete(
        self, interaction: discord.Interaction, aktuell: str
    ) -> list[app_commands.Choice[str]]:
        eintraege = (sc.daten().get("berechtigungen") or {})
        aktuell = (aktuell or "").strip().lower()
        return [
            app_commands.Choice(name=f"{k}  (aktuell: {v})", value=k)
            for k, v in eintraege.items()
            if aktuell in k
        ][:25]

    # --- AutoMod ------------------------------------------------------------

    @einstellungen_group.command(name="automod", description="Passt die AutoMod-Regeln an")
    @app_commands.describe(
        spam_nachrichten="Max. Nachrichten im Zeitfenster",
        spam_zeitfenster="Zeitfenster in Sekunden",
        spam_timeout_ab="Verstöße, ab denen ein Timeout folgt",
        mention_max="Max. Erwähnungen pro Nachricht",
        timeout_minuten="Timeout-Dauer in Minuten",
        link_blocken="Discord-Einladungen blocken?",
    )
    @benoetigt_befehl("einstellungen.verwalten")
    async def automod(
        self,
        interaction: discord.Interaction,
        spam_nachrichten: app_commands.Range[int, 1, 100] | None = None,
        spam_zeitfenster: app_commands.Range[int, 1, 300] | None = None,
        spam_timeout_ab: app_commands.Range[int, 1, 20] | None = None,
        mention_max: app_commands.Range[int, 1, 50] | None = None,
        timeout_minuten: app_commands.Range[int, 1, 1440] | None = None,
        link_blocken: bool | None = None,
    ):
        neu = {
            "spam_nachrichten": spam_nachrichten,
            "spam_zeitfenster": spam_zeitfenster,
            "spam_timeout_ab": spam_timeout_ab,
            "mention_max": mention_max,
            "timeout_minuten": timeout_minuten,
            "link_blocken": link_blocken,
        }
        geaendert = {k: v for k, v in neu.items() if v is not None}
        if not geaendert:
            await interaction.response.send_message(
                "⚠️ Bitte mindestens einen Wert angeben.", ephemeral=True
            )
            return
        for k, v in geaendert.items():
            sc.setze("automod", k, v)
        text = "\n".join(f"**{k}**: {v}" for k, v in geaendert.items())
        await interaction.response.send_message(
            f"✅ AutoMod aktualisiert:\n{text}", ephemeral=True
        )

    # --- Abwesenheit --------------------------------------------------------

    @einstellungen_group.command(name="abwesenheit", description="Passt die Abwesenheits-Regeln an")
    @app_commands.describe(
        meldepflicht_ab_tagen="Ab so vielen Tagen ist eine Abwesenheit meldepflichtig",
        erinnerung_vor_tagen="Erinnerung X Tage vor Ende",
        min_woerter="Min. Wörter für die Aufgabenübergabe",
        max_woerter="Max. Wörter für die Aufgabenübergabe",
    )
    @benoetigt_befehl("einstellungen.verwalten")
    async def abwesenheit(
        self,
        interaction: discord.Interaction,
        meldepflicht_ab_tagen: app_commands.Range[int, 0, 90] | None = None,
        erinnerung_vor_tagen: app_commands.Range[int, 0, 30] | None = None,
        min_woerter: app_commands.Range[int, 0, 2000] | None = None,
        max_woerter: app_commands.Range[int, 1, 2000] | None = None,
    ):
        neu = {
            "meldepflicht_ab_tagen": meldepflicht_ab_tagen,
            "erinnerung_vor_tagen": erinnerung_vor_tagen,
            "min_woerter": min_woerter,
            "max_woerter": max_woerter,
        }
        geaendert = {k: v for k, v in neu.items() if v is not None}
        if not geaendert:
            await interaction.response.send_message(
                "⚠️ Bitte mindestens einen Wert angeben.", ephemeral=True
            )
            return
        if None not in (min_woerter, max_woerter) and min_woerter > max_woerter:
            await interaction.response.send_message(
                "⚠️ min_woerter darf nicht größer als max_woerter sein.", ephemeral=True
            )
            return
        for k, v in geaendert.items():
            sc.setze("abwesenheit", k, v)
        text = "\n".join(f"**{k}**: {v}" for k, v in geaendert.items())
        await interaction.response.send_message(
            f"✅ Abwesenheits-Regeln aktualisiert:\n{text}", ephemeral=True
        )

    # --- Willkommen ---------------------------------------------------------

    @einstellungen_group.command(name="willkommen", description="Ändert den Willkommenstext")
    @app_commands.describe(text="Der neue Willkommenstext (leer lassen für den Standardtext)")
    @benoetigt_befehl("einstellungen.verwalten")
    async def willkommen(self, interaction: discord.Interaction, text: str | None = None):
        if text is None:
            await interaction.response.send_message(
                "⚠️ Bitte einen Text angeben (oder 'standard' für den Standardtext).",
                ephemeral=True,
            )
            return
        text = text.strip()
        if text.lower() in ("standard", "default", "reset"):
            text = ""
        if len(text) > 2000:
            await interaction.response.send_message(
                "⚠️ Der Text darf maximal 2000 Zeichen lang sein.", ephemeral=True
            )
            return
        sc.setze("willkommen", "text", text)
        await interaction.response.send_message(
            "✅ Willkommenstext aktualisiert." if text else "✅ Willkommenstext zurückgesetzt.",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Einstellungen(bot))
