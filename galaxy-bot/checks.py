"""
Berechtigungs-Checks für GalaxyBot.

Die Team-Rollen werden über ihre Position in der Hierarchie
(config.TEAM_ROLLEN) geprüft: Je niedriger der Index, desto höher die Rechte.
`benoetigt_teamrolle_ab(index)` erlaubt allen Rollen ab (inklusive) dem
gegebenen Index den Zugriff.
"""

import discord
from discord import app_commands

import config
# Index-Konstanten bequem aus checks importierbar machen
from config import (
    IDX_SERVERLEITUNG,
    IDX_STELV_LEITUNG,
    IDX_MANAGEMENT,
    IDX_ADMINISTRATION,
    IDX_MODERATION,
    IDX_SUPPORT,
    IDX_BEWERBUNGSTEAM,
)


def team_index(member: discord.Member) -> int | None:
    """Index der höchsten Team-Rolle des Members (0 = Serverleitung).
    None, wenn der Member keine Team-Rolle hat."""
    namen = {r.name for r in member.roles}
    for i, name in enumerate(config.TEAM_ROLLEN):
        if name in namen:
            return i
    return None


def ist_team(member: discord.Member) -> bool:
    return team_index(member) is not None


def hat_mindestens(member: discord.Member, index: int) -> bool:
    """True, wenn der Member die Rolle am `index` (oder eine höhere) hat."""
    if member.guild_permissions.administrator:
        return True
    idx = team_index(member)
    return idx is not None and idx <= index


def benoetigt_teamrolle_ab(index: int):
    """Decorator: erlaubt den Befehl ab der Team-Rolle an `index` (0 = Serverleitung)."""

    async def predicate(interaction: discord.Interaction) -> bool:
        rolle_name = config.TEAM_ROLLEN[index]
        if hat_mindestens(interaction.user, index):
            return True
        raise app_commands.CheckFailure(
            f"Für diesen Befehl benötigst du die Rolle **{rolle_name}** (oder höher)."
        )

    return app_commands.check(predicate)


# Fertige Dekoratoren für die häufigsten Fälle
benoetigt_support = benoetigt_teamrolle_ab(config.IDX_SUPPORT)
benoetigt_moderation = benoetigt_teamrolle_ab(config.IDX_MODERATION)
benoetigt_administration = benoetigt_teamrolle_ab(config.IDX_ADMINISTRATION)
benoetigt_management = benoetigt_teamrolle_ab(config.IDX_MANAGEMENT)
benoetigt_serverleitung = benoetigt_teamrolle_ab(config.IDX_SERVERLEITUNG)
