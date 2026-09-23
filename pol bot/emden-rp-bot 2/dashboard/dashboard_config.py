"""
Konfiguration für das Web-Dashboard. Werte kommen aus der .env Datei im dashboard/-Ordner.

WICHTIG: Anders als in der ursprünglichen Version braucht das Dashboard jetzt KEINEN
Zugriff mehr auf die lokale bot.db, sondern spricht über HTTP mit dem Bot (der auf einem
anderen Server laufen kann, z.B. bot-hosting.net, während das Dashboard bei Cybrancee liegt).
"""

import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI", "http://localhost:5000/callback")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_TOKEN")  # derselbe Bot-Token wie beim Bot (für Rollen-Check)
GUILD_ID = os.getenv("DISCORD_GUILD_ID")
DASHBOARD_SECRET_KEY = os.getenv("DASHBOARD_SECRET_KEY", "bitte-in-der-env-datei-aendern")

# Adresse, unter der der Bot-Server erreichbar ist (Domain/IP + Port der bot-hosting.net-Instanz)
BOT_API_URL = os.getenv("BOT_API_URL", "http://localhost:8080")
# Muss exakt mit API_KEY in der .env des BOTS übereinstimmen
BOT_API_KEY = os.getenv("BOT_API_KEY")

DISCORD_API = "https://discord.com/api/v10"
OAUTH_AUTHORIZE_URL = "https://discord.com/oauth2/authorize"
OAUTH_TOKEN_URL = f"{DISCORD_API}/oauth2/token"
