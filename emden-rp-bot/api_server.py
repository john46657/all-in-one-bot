"""
Eingebaute HTTP-API im Bot-Prozess. Läuft parallel zum Discord-Bot und erlaubt dem
Web-Dashboard (das auf einem ANDEREN Server laufen kann, z.B. bei Cybrancee, während
der Bot z.B. bei bot-hosting.net läuft), Daten abzurufen und Einstellungen zu ändern -
ohne direkten Zugriff auf die lokale SQLite-Datei zu brauchen.

Absicherung: Jede Anfrage muss den korrekten API-Schlüssel im Header 'X-API-Key'
mitschicken (siehe .env -> API_KEY). Ohne korrekten Schlüssel: 401 Unauthorized.
"""

import os
import logging

from aiohttp import web

from database import get_connection
from settings import SETTINGS, alle_settings, set_setting

log = logging.getLogger("api")

API_KEY = os.getenv("API_KEY")


@web.middleware
async def auth_middleware(request: web.Request, handler):
    if not API_KEY:
        return web.json_response({"error": "API_KEY ist auf dem Bot-Server nicht gesetzt."}, status=500)
    if request.headers.get("X-API-Key") != API_KEY:
        return web.json_response({"error": "Ungültiger oder fehlender API-Key."}, status=401)
    return await handler(request)


async def handle_uebersicht(request: web.Request):
    conn = get_connection()

    dienstzeiten = conn.execute("""
        SELECT user_id, SUM(dauer_sekunden) as gesamt, COUNT(*) as schichten
        FROM dienstzeiten WHERE ende_zeit IS NOT NULL
        GROUP BY user_id ORDER BY gesamt DESC LIMIT 15
    """).fetchall()

    dienstberichte_anzahl = conn.execute("""
        SELECT user_id, COUNT(*) as anzahl FROM dienstberichte
        GROUP BY user_id ORDER BY anzahl DESC LIMIT 15
    """).fetchall()

    ausbildungen = conn.execute(
        "SELECT rekrut_id, ausbilder_id, abgeschlossen FROM ausbildung ORDER BY id DESC"
    ).fetchall()

    gsg9_einsaetze = conn.execute("SELECT COUNT(*) as anzahl FROM gsg9_einsatzberichte").fetchone()
    funk_whitelist_anzahl = conn.execute("SELECT COUNT(*) as anzahl FROM funk_whitelist").fetchone()

    fahndungen_aktiv = conn.execute(
        "SELECT name, grund, dringlichkeit FROM fahndungen WHERE aktiv = 1 ORDER BY id DESC"
    ).fetchall()

    gefahrenstatus_aktuell = conn.execute(
        "SELECT status, grund, gesetzt_am FROM gefahrenstatus_verlauf ORDER BY id DESC LIMIT 1"
    ).fetchone()

    conn.close()

    def zu_dict_liste(rows):
        return [dict(r) for r in rows]

    return web.json_response({
        "dienstzeiten": zu_dict_liste(dienstzeiten),
        "dienstberichte_anzahl": zu_dict_liste(dienstberichte_anzahl),
        "ausbildungen": zu_dict_liste(ausbildungen),
        "gsg9_einsaetze": gsg9_einsaetze["anzahl"] if gsg9_einsaetze else 0,
        "funk_whitelist_anzahl": funk_whitelist_anzahl["anzahl"] if funk_whitelist_anzahl else 0,
        "fahndungen_aktiv": zu_dict_liste(fahndungen_aktiv),
        "gefahrenstatus_aktuell": dict(gefahrenstatus_aktuell) if gefahrenstatus_aktuell else None,
    })


async def handle_get_settings(request: web.Request):
    return web.json_response(alle_settings())


async def handle_post_settings(request: web.Request):
    daten = await request.json()
    for key, wert in daten.items():
        if key in SETTINGS and isinstance(wert, str) and wert.strip():
            set_setting(key, wert.strip())
    return web.json_response({"status": "ok", "settings": alle_settings()})


async def start_api_server():
    app = web.Application(middlewares=[auth_middleware])
    app.router.add_get("/api/uebersicht", handle_uebersicht)
    app.router.add_get("/api/settings", handle_get_settings)
    app.router.add_post("/api/settings", handle_post_settings)

    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("API_PORT", "8080"))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    log.info(f"API-Server läuft auf Port {port}.")
