"""
Berechtigungs-Checks für GalaxyBot.

Berechtigungen werden über die Team-Hierarchie (server_config.json,
`rollen.hierarchie`) geprüft: Je niedriger der Index, desto höher die Rechte.

Welche Rolle für einen Befehl mindestens nötig ist, steht in
`berechtigungen` (z. B. "moderation.ban": "🔧 Administration") und kann
live per `/einstellungen berechtigung` geändert werden – ohne Neustart.

"*" als Rolle bedeutet: jedes Teammitglied.
"""

import discord
from discord import app_commands

import server_config as sc
from config import (
    IDX_SERVERLEITUNG, IDX_STELV_LEITUNG, IDX_MANAGEMENT, IDX_ADMINISTRATION,
    IDX_MODERATION, IDX_SUPPORT, IDX_BEWERBUNGSTEAM,
)

__all__ = [
    "team_index", "ist_team", "hat_mindestens", "hat_befehl",
    "benoetigt_teamrolle_ab", "benoetigt_befehl",
    "benoetigt_support", "benoetigt_moderation", "benoetigt_administration",
    "benoetigt_management", "benoetigt_serverleitung",
    "IDX_SERVERLEITUNG", "IDX_STELV_LEITUNG", "IDX_MANAGEMENT",
    "IDX_ADMINISTRATION", "IDX_MODERATION", "IDX_SUPPORT", "IDX_BEWERBUNGSTEAM",
]


def team_index(member: discord.Member) -> int | None:
    """Index der höchsten Team-Rolle des Members (0 = Serverleitung)."""
    return sc._index(member)


def ist_team(member: discord.Member) -> bool:
    return team_index(member) is not None


def hat_mindestens(member: discord.Member, index: int) -> bool:
    """True, wenn der Member die Rolle am `index` (oder eine höhere) hat."""
    if getattr(member.guild_permissions, "administrator", False):
        return True
    idx = team_index(member)
    return idx is not None and idx <= index


def hat_befehl(member: discord.Member, befehl_key: str) -> bool:
    """True, wenn `member` den Befehl laut Konfiguration nutzen darf."""
    return sc.darf_befehl(member, befehl_key)


def benoetigt_teamrolle_ab(index: int):
    """Decorator: erlaubt den Befehl ab der Team-Rolle an `index`."""

    async def predicate(interaction: discord.Interaction) -> bool:
        if hat_mindestens(interaction.user, index):
            return True
        rollen_name = sc.hierarchie()[index] if index < len(sc.hierarchie()) else "Team"
        raise app_commands.CheckFailure(
            f"Für diesen Befehl benötigst du die Rolle **{rollen_name}** (oder höher)."
        )

    return app_commands.check(predicate)


def benoetigt_befehl(befehl_key: str):
    """Decorator: erlaubt den Befehl gemäß `berechtigungen.<befehl_key>` in der Konfiguration.
    Die Rolle wird zur Laufzeit aufgelöst – Änderungen greifen sofort."""

    async def predicate(interaction: discord.Interaction) -> bool:
        if hat_befehl(interaction.user, befehl_key):
            return True
        rolle = sc.mindest_rolle(befehl_key) or "Team"
        raise app_commands.CheckFailure(
            f"Für diesen Befehl benötigst du die Rolle **{rolle}** (oder höher)."
        )

    return app_commands.check(predicate)


# Abwärtskompatible Dekoratoren (Index-basiert)
benoetigt_support = benoetigt_teamrolle_ab(IDX_SUPPORT)
benoetigt_moderation = benoetigt_teamrolle_ab(IDX_MODERATION)
benoetigt_administration = benoetigt_teamrolle_ab(IDX_ADMINISTRATION)
benoetigt_management = benoetigt_teamrolle_ab(IDX_MANAGEMENT)
benoetigt_serverleitung = benoetigt_teamrolle_ab(IDX_SERVERLEITUNG)
