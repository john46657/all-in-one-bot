"""
Discord OAuth2-Login und Berechtigungsprüfung.

Ablauf:
1. /login schickt den User zu Discord zum Einloggen (nur `identify`-Scope nötig)
2. Discord schickt ihn zu /callback zurück mit einem `code`
3. Wir tauschen den Code gegen einen Access-Token
4. Wir holen die Discord-User-Infos (wer ist das)
5. Wir prüfen über den BOT-Token, welche Rollen dieser User auf dem Server hat
6. Wir fragen beim Bot-Server (per API) ab, wie die "Leitung"-Rolle aktuell heißt,
   und lassen nur User mit dieser Rolle rein
"""

import requests

import dashboard_config as cfg


def get_oauth_login_url() -> str:
    return (
        f"{cfg.OAUTH_AUTHORIZE_URL}?client_id={cfg.DISCORD_CLIENT_ID}"
        f"&redirect_uri={cfg.DISCORD_REDIRECT_URI}&response_type=code&scope=identify"
    )


def exchange_code_for_token(code: str):
    data = {
        "client_id": cfg.DISCORD_CLIENT_ID,
        "client_secret": cfg.DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": cfg.DISCORD_REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(cfg.OAUTH_TOKEN_URL, data=data, headers=headers, timeout=10)
    if resp.status_code != 200:
        return None
    return resp.json().get("access_token")


def get_discord_user(access_token: str):
    resp = requests.get(
        f"{cfg.DISCORD_API}/users/@me",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    if resp.status_code != 200:
        return None
    return resp.json()


def get_member_rollen_namen(user_id: str):
    """Holt per Bot-Token die Rollen des Users im konfigurierten Server (als Namen)."""
    member_resp = requests.get(
        f"{cfg.DISCORD_API}/guilds/{cfg.GUILD_ID}/members/{user_id}",
        headers={"Authorization": f"Bot {cfg.DISCORD_BOT_TOKEN}"},
        timeout=10,
    )
    if member_resp.status_code != 200:
        return None  # User ist nicht (mehr) auf dem Server

    rollen_ids = member_resp.json().get("roles", [])

    roles_resp = requests.get(
        f"{cfg.DISCORD_API}/guilds/{cfg.GUILD_ID}/roles",
        headers={"Authorization": f"Bot {cfg.DISCORD_BOT_TOKEN}"},
        timeout=10,
    )
    if roles_resp.status_code != 200:
        return None

    alle_rollen = {r["id"]: r["name"] for r in roles_resp.json()}
    return [alle_rollen[rid] for rid in rollen_ids if rid in alle_rollen]


def ist_leitung(rollen_namen: list) -> bool:
    """Fragt beim Bot-Server ab, wie die Leitungs-Rolle aktuell heißt (kann über das
    Dashboard geändert worden sein), und prüft, ob der User sie hat."""
    try:
        resp = requests.get(
            f"{cfg.BOT_API_URL}/api/settings",
            headers={"X-API-Key": cfg.BOT_API_KEY},
            timeout=10,
        )
        if resp.status_code != 200:
            return False
        leitung_rolle = resp.json().get("rolle_leitung", {}).get("wert")
    except requests.RequestException:
        return False

    return leitung_rolle in rollen_namen
