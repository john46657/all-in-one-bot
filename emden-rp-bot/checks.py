"""
Custom Slash-Command-Check, der die Rolle dynamisch aus den Settings liest
(statt fest zur Import-Zeit), damit Änderungen über das Dashboard sofort wirken,
ohne den Bot neu zu starten.
"""

import discord
from discord import app_commands

from settings import get_setting


def benoetigt_rolle(setting_key: str):
    """Decorator: prüft, ob der User die Rolle hat, die aktuell unter `setting_key` hinterlegt ist.
    Administratoren dürfen immer durch."""

    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.user.guild_permissions.administrator:
            return True
        rollen_name = get_setting(setting_key)
        rolle = discord.utils.get(interaction.user.roles, name=rollen_name)
        if rolle is None:
            raise app_commands.CheckFailure(f"Dir fehlt die Rolle '{rollen_name}' für diesen Befehl.")
        return True

    return app_commands.check(predicate)
