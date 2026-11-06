"""Uppdaterar butiken i ditt repo till version 2026.11.0 och rättar post-create.sh.

    curl -fsSL https://raw.githubusercontent.com/kaysismail-83/techretail-tests/main/scripts/fixa_butiken.sh | bash

Kommandot hämtar och kör det här skriptet.

Vad skriptet gör:
0. Hämtar den nya butiken från kursens mall på GitHub, om den inte redan finns i sut/.
1. Pekar pyproject.toml och uv.lock på den nya butiken i sut/ och tar bort den gamla.
2. Lägger in raden som tar bort Yarns apt-källa i .devcontainer/post-create.sh, om den saknas.
3. Kör uv sync och startar om butiken.
4. Gör en commit med bara de här filerna. Dina tester och texter rörs inte.

Du kan köra skriptet flera gånger. Andra gången står det att allt redan är klart.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD_WHEEL = "techretail_shop-2026.10.0-py3-none-any.whl"
NEW_WHEEL = "techretail_shop-2026.11.0-py3-none-any.whl"
OLD_HASH = "sha256:26aaec28fb28d421b8fe2ff1ff7e5a22910142f711e7fb3745ae2f719b8407d7"
NEW_HASH = "sha256:2067663f8e44c43d33049f7aa9bb88978f3e30691db8c47070a4e1cdebcb90b8"
WHEEL_URL = f"https://raw.githubusercontent.com/kaysismail-83/techretail-tests/main/sut/{NEW_WHEEL}"
NEW_LOCK_SHA = "260e287accc01f3fec6a9221d4d9672bfccb36e8a3f3364a9ddec2d91bb3ee25"
OLD_POST_CREATE_SHA = "f2608b5d0d99f1f698ae84fa33fe6e7e921b19b48e1f336fb9e38ea94196c92f"
YARN_LINES = ('echo "==> Tar bort Yarns apt-källa (basavbildningens nyckel har gått ut och stoppar apt)"\n'
              "sudo rm -f /etc/apt/sources.list.d/yarn.list\n\n")
CHROMIUM_LINE = 'echo "==> Installerar Chromium för Playwright"\n'
NEW_POST_CREATE = r'''#!/usr/bin/env bash
# Körs en gång när Codespace/devcontainer skapas. Installerar allt kursen behöver.
set -euo pipefail

UV_VERSION="0.13.4"
K6_VERSION="v2.3.0"

echo "==> Installerar uv ${UV_VERSION}"
curl -LsSf "https://astral.sh/uv/${UV_VERSION}/install.sh" | sh
export PATH="$HOME/.local/bin:$PATH"

echo "==> Installerar Python-paketen (låsta versioner i uv.lock)"
uv sync --locked

echo "==> Tar bort Yarns apt-källa (basavbildningens nyckel har gått ut och stoppar apt)"
sudo rm -f /etc/apt/sources.list.d/yarn.list

echo "==> Installerar Chromium för Playwright"
uv run playwright install --with-deps chromium

echo "==> Installerar Chromium för Playwright MCP (lektion 8)"
npx -y @playwright/mcp@0.0.83 install-browser chromium

echo "==> Installerar k6 ${K6_VERSION}"
arch="$(dpkg --print-architecture)"   # amd64 eller arm64
curl -fsSL "https://github.com/grafana/k6/releases/download/${K6_VERSION}/k6-${K6_VERSION}-linux-${arch}.tar.gz" \
  | sudo tar -xz -C /usr/local/bin --strip-components=1 "k6-${K6_VERSION}-linux-${arch}/k6"

echo "==> Klart. Node $(node --version), k6 $(k6 version | awk '{print $2}'), $(uv --version)"
'''
URL = os.environ.get("TECHRETAIL_URL", "http://127.0.0.1:8000").rstrip("/")
FILES = ["pyproject.toml", "uv.lock", "sut", ".devcontainer/post-create.sh", "scripts/uppdatera_butiken.py"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> str:
    return path.read_bytes().decode("utf-8")


def write(path: Path, text: str) -> None:
    # Bytes, så att radsluten blir desamma på Windows som i kursens filer.
    path.write_bytes(text.encode("utf-8"))


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def update_pyproject() -> bool:
    path = ROOT / "pyproject.toml"
    text = read(path)
    if NEW_WHEEL in text and "techretail-shop==2026.11.0" in text:
        return False
    if OLD_WHEEL not in text or "techretail-shop==2026.10.0" not in text:
        raise SystemExit("pyproject.toml ser inte ut som kursens fil. Inget är ändrat. Kopiera allt i terminalen till tråden under inlägget om butiken i Allmänt.")
    text = text.replace("techretail-shop==2026.10.0", "techretail-shop==2026.11.0").replace(OLD_WHEEL, NEW_WHEEL)
    write(path, text)
    return True


def update_lock() -> bool:
    path = ROOT / "uv.lock"
    text = read(path)
    if NEW_WHEEL in text and OLD_WHEEL not in text:
        return False
    text = text.replace(OLD_WHEEL, NEW_WHEEL).replace(OLD_HASH, NEW_HASH)
    text = text.replace('name = "techretail-shop"\nversion = "2026.10.0"', 'name = "techretail-shop"\nversion = "2026.11.0"')
    write(path, text)
    if sha(path) != NEW_LOCK_SHA:
        # Låsfilen skilde sig redan från kursens. Låt uv räkna fram den igen.
        subprocess.run(["uv", "lock"], cwd=ROOT, check=False)
    return True


def update_post_create() -> bool:
    path = ROOT / ".devcontainer" / "post-create.sh"
    if not path.exists():
        return False
    text = read(path)
    if "yarn.list" in text:
        return False
    if sha(path) == OLD_POST_CREATE_SHA:
        write(path, NEW_POST_CREATE)
    elif CHROMIUM_LINE in text:
        write(path, text.replace(CHROMIUM_LINE, YARN_LINES + CHROMIUM_LINE, 1))
    else:
        print("  Obs: .devcontainer/post-create.sh ser annorlunda ut och är inte ändrad.")
        return False
    return True


def shop_version() -> str | None:
    try:
        with urllib.request.urlopen(f"{URL}/health", timeout=3) as r:
            return json.loads(r.read().decode()).get("version")
    except (OSError, ValueError):
        return None


def fetch_wheel(target: Path) -> bool:
    print("Hämtar butiken 2026.11.0 från kursens mall på GitHub ...")
    try:
        with urllib.request.urlopen(WHEEL_URL, timeout=60) as r:
            data = r.read()
    except OSError as e:
        print(f"Det gick inte att hämta butiken: {e}")
        return False
    if "sha256:" + hashlib.sha256(data).hexdigest() != NEW_HASH:
        print("Filen som hämtades är inte kursens butik. Inget är ändrat.")
        return False
    target.parent.mkdir(exist_ok=True)
    target.write_bytes(data)
    return True


def main() -> int:
    wheel = ROOT / "sut" / NEW_WHEEL
    if not wheel.exists() and not fetch_wheel(wheel):
        print("Vänta en minut och kör kommandot igen. Hjälper det inte, kopiera allt i terminalen")
        print("och klistra in det i tråden under inlägget om butiken i kanalen Allmänt i Teams.")
        return 2

    changed = [name for name, done in [("pyproject.toml", update_pyproject()), ("uv.lock", update_lock()),
                                       (".devcontainer/post-create.sh", update_post_create())] if done]
    old = ROOT / "sut" / OLD_WHEEL
    if old.exists():
        old.unlink()
        changed.append(f"sut/{OLD_WHEEL} (borttagen)")

    if changed:
        print("Ändrade filer:")
        for name in changed:
            print(f"  {name}")
    else:
        print("Filerna var redan uppdaterade.")

    print("Kör uv sync ...")
    if subprocess.run(["uv", "sync"], cwd=ROOT).returncode != 0:
        print("uv sync misslyckades. Kör kommandot igen. Står felet kvar, kopiera allt i terminalen till tråden under inlägget om butiken i Allmänt.")
        return 1

    yarn_list = Path("/etc/apt/sources.list.d/yarn.list")
    if yarn_list.exists() and shutil.which("sudo"):
        subprocess.run(["sudo", "rm", "-f", str(yarn_list)], check=False)

    if shop_version() is not None:
        subprocess.run(["uv", "run", "--quiet", "python", "scripts/shop.py", "restart"], cwd=ROOT)
    version = shop_version()

    if git("rev-parse", "--is-inside-work-tree").stdout.strip() == "true" and changed:
        git("add", "-A", "--", *FILES)
        commit = git("commit", "-m", "Patch: butiken 2026.11.0", "--", *FILES)
        if commit.returncode != 0:
            print("Commiten gick inte att göra. Gör den själv i Källkontroll (Source Control) med meddelandet")
            print("  Patch: butiken 2026.11.0")

    print()
    if version == "2026.11.0":
        print("Klart. Butiken kör version 2026.11.0.")
    elif version is None:
        print("Klart. Butiken är inte igång just nu. Starta den med  make shop  .")
        print("Kontrollera sedan med  make doctor  att det står butiken 2026.11.0.")
    else:
        print(f"Butiken svarar men kör fortfarande version {version}.")
        print("Kör  make shop-stop  och sedan  make shop  . Hjälper det inte, starta om din codespace.")
    if not shutil.which("k6") and os.environ.get("CODESPACES"):
        print("k6 saknas i din codespace. Det behövs först i lektion 6. Kör Rebuild Container före lektion 6.")
    print("Nästa steg:  git push")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
