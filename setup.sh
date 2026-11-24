#!/usr/bin/env bash
set -e
sudo apt-get update && sudo apt-get install -y ffmpeg pulseaudio
pip install -r requirements.txt
playwright install chromium
playwright install-deps chromium
echo "Entorno listo. Exporta tus API keys y ejecuta: python pipeline.py \"Tu idea de app\""
