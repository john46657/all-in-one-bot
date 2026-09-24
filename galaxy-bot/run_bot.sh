#!/bin/bash
# Startet GalaxyBot mit dem projektlokalen Venv.
# Wird vom LaunchAgent (com.galaxybot) aufgerufen, kann aber auch manuell
# ausgeführt werden:  ./run_bot.sh

set -euo pipefail

# Eigenes Verzeichnis ermitteln (unabhängig vom Aufruf-Ort)
cd "$(dirname "$0")"

# Log- und Datenverzeichnis sicherstellen
mkdir -p data logs

# macOS: CA-Zertifikate für SSL finden (bot-hosting.net/Linux braucht das nicht)
if [ -z "${SSL_CERT_FILE:-}" ]; then
  CERT="$(./venv/bin/python -m certifi 2>/dev/null || true)"
  if [ -n "$CERT" ]; then
    export SSL_CERT_FILE="$CERT"
  fi
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] GalaxyBot wird gestartet ..."
exec ./venv/bin/python bot.py
