"""
AutoMod: Spam-Schutz, Mention-Spam-Schutz, Link-/Einladungs-Schutz.

Regeln sind über die Settings anpassbar:
- automod_spam_nachrichten / automod_spam_zeitfenster / automod_spam_timeout_ab
- automod_mention_max
- automod_link_blocken

Eskalation: nach wiederholten Verstößen greift automatisch ein Timeout.
Alle Aktionen werden in den Mod- und Punishment-Logs protokolliert.
"""

import datetime
import logging
import re
from collections import defaultdict, deque

import discord
from discord.ext import commands

import config
from database import get_connection
from settings import get_setting
from logging_utils import log_mod, log_punishment

log = logging.getLogger("galaxy.automod")

_EINLADUNGS_REGEX = re.compile(r"(discord\.gg/|discord\.com/invite/)", re.IGNORECASE)


def _setting_int(key: str, default: int) -> int:
    try:
        return int(get_setting(key))
    except (TypeError, ValueError):
        return default


def _jetzt() -> str:
    return datetime.datetime.now().isoformat()


class AutoMod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # user_id -> deque[(timestamp, channel_id)]
        self.nachrichten: dict[int, deque] = defaultdict(lambda: deque(maxlen=50))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not self._soll_geprueft_werden(message):
            return

        verausstoss = None

        # 1) Spam: zu viele Nachrichten im Zeitfenster
        spam_grenze = _setting_int("automod_spam_nachrichten", config.AUTOMOD["spam_nachrichten"])
        fenster = _setting_int("automod_spam_zeitfenster", config.AUTOMOD["spam_zeitfenster"])
        jetzt = message.created_at.timestamp()
        historie = self.nachrichten[message.author.id]
        historie.append((jetzt, message.channel.id))
        while historie and jetzt - historie[0][0] > fenster:
            historie.popleft()
        if len(historie) >= spam_grenze:
            verausstoss = "spam"

        # 2) Mention-Spam
        mention_max = _setting_int("automod_mention_max", config.AUTOMOD["mention_max"])
        anzahl_mentions = len(message.mentions) + len(message.role_mentions)
        if anzahl_mentions > mention_max:
            verausstoss = "mention-spam"

        # 3) Link-/Einladungs-Schutz
        link_blocken = get_setting("automod_link_blocken") == "1"
        if link_blocken and _EINLADUNGS_REGEX.search(message.content or ""):
            verausstoss = "einladung"

        if not verausstoss:
            return

        try:
            await message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass

        # Verstoß protokollieren + Eskalation prüfen
        conn = get_connection()
        conn.execute(
            "INSERT INTO automod_verstoesse (user_id, typ, channel_id, erstellt_am) VALUES (?, ?, ?, ?)",
            (message.author.id, verausstoss, message.channel.id, _jetzt()),
        )
        conn.commit()
        anzahl = conn.execute(
            "SELECT COUNT(*) AS c FROM automod_verstoesse WHERE user_id = ? AND typ = ?",
            (message.author.id, verausstoss),
        ).fetchone()["c"]
        conn.close()

        await log_mod(
            message.guild,
            title=f"🛡️ AutoMod: {verrausstoss}",
            description=f"{message.author.mention} in {message.channel.mention}",
            fields=[("Verstöße", str(anzahl), True), ("Inhalt", (message.content or "")[:300], False)],
        )

        # Automatischer Timeout ab X Verstößen
        timeout_ab = _setting_int("automod_spam_timeout_ab", config.AUTOMOD["spam_timeout_ab"])
        if anzahl >= timeout_ab:
            try:
                bis = discord.utils.utcnow() + datetime.timedelta(minutes=10)
                await message.author.timeout(bis, reason=f"AutoMod: {verrausstoss} (x{anzahl})")
                await log_punishment(
                    message.guild,
                    title="🔇 AutoMod Timeout",
                    description=f"{message.author.mention} wurde automatisch timeout.",
                    fields=[("Grund", f"{verrausstoss} ({anzahl} Verstöße)", False)],
                )
            except discord.Forbidden:
                log.warning("AutoMod: Keine Rechte für Timeout bei %s", message.author.id)

    def _soll_geprueft_werden(self, message: discord.Message) -> bool:
        if message.guild is None or message.author.bot:
            return False
        if isinstance(message.author, discord.Member) and message.author.guild_permissions.manage_messages:
            return False  # Team-Mitglieder mit Moderationsrechten nicht auto-moderieren
        return True


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoMod(bot))
