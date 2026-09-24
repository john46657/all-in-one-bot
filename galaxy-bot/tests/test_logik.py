"""
Logik-Tests für GalaxyBot (ohne Discord-Verbindung lauffähig).

Getestet werden die reinen Funktionen, die für den Betrieb kritisch sind:
- Wortgrenzen der Bewerbungs-/Übergabe-Texte (50–250 Wörter)
- Datums- und Dauer-Parser
- Team-Hierarchie / Berechtigungs-Checks
- Status-Farben des Abwesenheitssystems

Ausführen:  python tests/test_logik.py
"""

import datetime
import os
import sys
import types
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config  # noqa: E402
from checks import hat_mindestens, ist_team, team_index  # noqa: E402


def _text(anzahl_woerter: int) -> str:
    return " ".join(["wort"] * anzahl_woerter)


def _fake_member(rollen_namen: list[str], administrator: bool = False):
    return types.SimpleNamespace(
        roles=[types.SimpleNamespace(name=n) for n in rollen_namen],
        guild_permissions=types.SimpleNamespace(administrator=administrator),
    )


class WortZaehlTests(unittest.TestCase):
    """Master-Prompt §34: 49 → ablehnen, 50 → akzeptieren, 250 → akzeptieren, 251 → ablehnen."""

    def test_woertgrenzen(self):
        from cogs.absence import _zaehle_woerter

        self.assertEqual(_zaehle_woerter(_text(49)), 49)
        self.assertEqual(_zaehle_woerter(_text(50)), 50)
        self.assertEqual(_zaehle_woerter(_text(250)), 250)
        self.assertEqual(_zaehle_woerter(_text(251)), 251)

    def test_ist_uebergabe_text_valide(self):
        from cogs.absence import _zaehle_woerter

        def valid(text):
            return 50 <= _zaehle_woerter(text) <= 250

        self.assertFalse(valid(_text(49)), "49 Wörter müssen abgelehnt werden")
        self.assertTrue(valid(_text(50)), "50 Wörter müssen akzeptiert werden")
        self.assertTrue(valid(_text(250)), "250 Wörter müssen akzeptiert werden")
        self.assertFalse(valid(_text(251)), "251 Wörter müssen abgelehnt werden")

    def test_leerer_text(self):
        from cogs.absence import _zaehle_woerter

        self.assertEqual(_zaehle_woerter(""), 0)
        self.assertEqual(_zaehle_woerter("   "), 0)


class DauerParserTests(unittest.TestCase):
    def test_einheiten(self):
        from cogs.moderation import _parse_dauer

        self.assertEqual(_parse_dauer("10m"), 600)
        self.assertEqual(_parse_dauer("1h"), 3600)
        self.assertEqual(_parse_dauer("2h30m"), 9000)
        self.assertEqual(_parse_dauer("1d"), 86400)
        self.assertEqual(_parse_dauer("30s"), 30)

    def test_ungueltig(self):
        from cogs.moderation import _parse_dauer

        self.assertIsNone(_parse_dauer("abc"))
        self.assertIsNone(_parse_dauer("10"))
        self.assertIsNone(_parse_dauer(""))


class DatumParserTests(unittest.TestCase):
    def test_formate(self):
        from cogs.absence import _parse_datum

        self.assertEqual(_parse_datum("24.09.2026"), datetime.date(2026, 9, 24))
        self.assertEqual(_parse_datum("2026-09-24"), datetime.date(2026, 9, 24))
        self.assertEqual(_parse_datum("24.09"), datetime.date(datetime.date.today().year, 9, 24))

    def test_ungueltig(self):
        from cogs.absence import _parse_datum

        self.assertIsNone(_parse_datum("abc"))
        self.assertIsNone(_parse_datum("32.13.9999"))
        self.assertIsNone(_parse_datum(""))

    def test_formatierung(self):
        from cogs.absence import _format_datum

        self.assertEqual(_format_datum(datetime.date(2026, 9, 24)), "24.09.2026")
        self.assertEqual(_format_datum("2026-09-24"), "24.09.2026")
        self.assertEqual(_format_datum(None), "–")


class HierarchieTests(unittest.TestCase):
    def test_keine_team_rolle(self):
        self.assertIsNone(team_index(_fake_member(["👤 Mitglied"])))
        self.assertFalse(ist_team(_fake_member(["👤 Mitglied"])))

    def test_moderator(self):
        member = _fake_member(["👤 Mitglied", "🔨 Moderation"])
        self.assertEqual(team_index(member), config.IDX_MODERATION)
        self.assertTrue(ist_team(member))

    def test_serverleitung_sieht_alles(self):
        member = _fake_member(["👤 Mitglied", "🔨 Moderation", "👑 Serverleitung"])
        self.assertEqual(team_index(member), config.IDX_SERVERLEITUNG)

    def test_hat_mindestens(self):
        moderator = _fake_member(["🔨 Moderation"])
        self.assertTrue(hat_mindestens(moderator, config.IDX_MODERATION))
        self.assertFalse(hat_mindestens(moderator, config.IDX_ADMINISTRATION))

        admin = _fake_member(["🔧 Administration"])
        self.assertTrue(hat_mindestens(admin, config.IDX_ADMINISTRATION))
        self.assertTrue(hat_mindestens(admin, config.IDX_MODERATION))

    def test_administrator_bypass(self):
        member = _fake_member(["👤 Mitglied"], administrator=True)
        self.assertTrue(hat_mindestens(member, config.IDX_SERVERLEITUNG))


class AbwesenheitsStatusTests(unittest.TestCase):
    def test_status_farben(self):
        from cogs.absence import _status_farbe

        self.assertEqual(_status_farbe("eingereicht"), config.STATUS_FARBEN["🟡"])
        self.assertEqual(_status_farbe("genehmigt"), config.STATUS_FARBEN["🟢"])
        self.assertEqual(_status_farbe("abgelehnt"), config.STATUS_FARBEN["🔴"])
        self.assertEqual(_status_farbe("verlaengert"), config.STATUS_FARBEN["🔵"])
        self.assertEqual(_status_farbe("aktiv"), config.STATUS_FARBEN["🟣"])
        self.assertEqual(_status_farbe("beendet"), config.STATUS_FARBEN["⚫"])

    def test_status_anzeige_vollstaendig(self):
        from cogs.absence import STATUS_ANZEIGE

        erwartete = {"eingereicht", "genehmigt", "abgelehnt", "verlaengert", "aktiv", "beendet"}
        self.assertEqual(set(STATUS_ANZEIGE.keys()), erwartete)


class TicketTests(unittest.TestCase):
    def test_ticket_typen_vollstaendig(self):
        from cogs.tickets import TICKET_TYPEN

        erwartete = {"support", "bewerbung", "spieler_meldung", "bug_meldung", "vorschlag", "partnerschaft"}
        self.assertEqual(set(TICKET_TYPEN.keys()), erwartete)
        for v in TICKET_TYPEN.values():
            self.assertIn("emoji", v)
            self.assertIn("label", v)
            self.assertIn("farbe", v)


class ConfigTests(unittest.TestCase):
    def test_team_rollen_hierarchie(self):
        # Serverleitung muss an erster Stelle stehen
        self.assertEqual(config.TEAM_ROLLEN[0], "👑 Serverleitung")
        # Indizes müssen zur Liste passen
        self.assertLess(config.IDX_ADMINISTRATION, config.IDX_MODERATION)
        self.assertLess(config.IDX_MODERATION, config.IDX_SUPPORT)

    def test_status_farben_vollstaendig(self):
        self.assertEqual(len(config.STATUS_FARBEN), 7)


if __name__ == "__main__":
    unittest.main(verbosity=2)
