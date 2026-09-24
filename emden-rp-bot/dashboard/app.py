"""
Web-Dashboard für den Emden RP Bot.

Läuft komplett unabhängig vom Bot-Server - spricht ausschließlich über die Bot-API
(HTTP) mit ihm. Kann also problemlos auf einem anderen Hoster laufen als der Bot selbst
(z.B. Dashboard bei Cybrancee, Bot bei bot-hosting.net).

Starten mit: python app.py  (aus dem dashboard/-Ordner heraus)

Nur Mitglieder mit der "Leitung"-Rolle kommen rein.
"""

import functools
import datetime

import requests
from flask import Flask, redirect, request, session, render_template, url_for, flash

import dashboard_config as cfg
from discord_oauth import (
    get_oauth_login_url,
    exchange_code_for_token,
    get_discord_user,
    get_member_rollen_namen,
    ist_leitung,
)

app = Flask(__name__)
app.secret_key = cfg.DASHBOARD_SECRET_KEY

GEFAHRENSTUFEN = {
    "gruen": {"label": "Grün – Normaler Dienst", "emoji": "🟢"},
    "gelb": {"label": "Gelb – Erhöhte Vorsicht", "emoji": "🟡"},
    "rot": {"label": "Rot – Akute Gefahrenlage", "emoji": "🔴"},
}


def bot_api_get(pfad: str):
    resp = requests.get(f"{cfg.BOT_API_URL}{pfad}", headers={"X-API-Key": cfg.BOT_API_KEY}, timeout=10)
    resp.raise_for_status()
    return resp.json()


def bot_api_post(pfad: str, daten: dict):
    resp = requests.post(f"{cfg.BOT_API_URL}{pfad}", json=daten, headers={"X-API-Key": cfg.BOT_API_KEY}, timeout=10)
    resp.raise_for_status()
    return resp.json()


def format_dauer(sekunden) -> str:
    if not sekunden:
        return "0h 0min"
    sekunden = int(sekunden)
    stunden = sekunden // 3600
    minuten = (sekunden % 3600) // 60
    return f"{stunden}h {minuten}min"


app.jinja_env.globals.update(format_dauer=format_dauer)


def login_erforderlich(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/")
def index():
    return redirect(url_for("uebersicht") if "user" in session else url_for("login"))


@app.route("/login")
def login():
    if "user" in session:
        return redirect(url_for("uebersicht"))
    return render_template("login.html", login_url=get_oauth_login_url())


@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        flash("Login fehlgeschlagen: kein Code von Discord erhalten.")
        return redirect(url_for("login"))

    access_token = exchange_code_for_token(code)
    if not access_token:
        flash("Login fehlgeschlagen: Code konnte nicht gegen einen Token getauscht werden.")
        return redirect(url_for("login"))

    user = get_discord_user(access_token)
    if not user:
        flash("Login fehlgeschlagen: Discord-Userdaten konnten nicht geladen werden.")
        return redirect(url_for("login"))

    rollen_namen = get_member_rollen_namen(user["id"])
    if rollen_namen is None:
        flash("Du bist nicht auf dem Emden RP Server. Zugriff verweigert.")
        return redirect(url_for("login"))

    if not ist_leitung(rollen_namen):
        flash("Zugriff verweigert: Du benötigst die Leitungs-Rolle für das Dashboard, "
              "oder der Bot-Server ist gerade nicht erreichbar.")
        return redirect(url_for("login"))

    session["user"] = {"id": user["id"], "username": user.get("username")}
    return redirect(url_for("uebersicht"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/uebersicht")
@login_erforderlich
def uebersicht():
    try:
        daten = bot_api_get("/api/uebersicht")
    except requests.RequestException as e:
        flash(f"Bot-Server nicht erreichbar: {e}")
        daten = {
            "dienstzeiten": [], "dienstberichte_anzahl": [], "ausbildungen": [],
            "gsg9_einsaetze": 0, "funk_whitelist_anzahl": 0, "fahndungen_aktiv": [],
            "gefahrenstatus_aktuell": None,
        }

    return render_template(
        "uebersicht.html",
        dienstzeiten=daten["dienstzeiten"],
        dienstberichte_anzahl=daten["dienstberichte_anzahl"],
        ausbildungen=daten["ausbildungen"],
        gsg9_einsaetze=daten["gsg9_einsaetze"],
        funk_whitelist_anzahl=daten["funk_whitelist_anzahl"],
        fahndungen_aktiv=daten["fahndungen_aktiv"],
        gefahrenstatus_aktuell=daten["gefahrenstatus_aktuell"],
        gefahrenstufen=GEFAHRENSTUFEN,
    )


@app.route("/einstellungen", methods=["GET", "POST"])
@login_erforderlich
def einstellungen():
    if request.method == "POST":
        neue_werte = {key: value.strip() for key, value in request.form.items() if value.strip()}
        try:
            bot_api_post("/api/settings", neue_werte)
            flash("Einstellungen gespeichert. Änderungen gelten sofort, ohne Bot-Neustart.")
        except requests.RequestException as e:
            flash(f"Fehler beim Speichern - Bot-Server nicht erreichbar: {e}")
        return redirect(url_for("einstellungen"))

    try:
        settings = bot_api_get("/api/settings")
    except requests.RequestException as e:
        flash(f"Bot-Server nicht erreichbar: {e}")
        settings = {}

    return render_template("einstellungen.html", settings=settings)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
