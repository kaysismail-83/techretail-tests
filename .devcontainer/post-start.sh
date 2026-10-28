#!/usr/bin/env bash
# Körs varje gång Codespace startar: startar butiken i bakgrunden.
export PATH="$HOME/.local/bin:$PATH"
uv run --quiet python scripts/shop.py start || echo "Butiken startade inte. Kör: make shop"
echo "Kör  make doctor  för att kontrollera att allt fungerar."
