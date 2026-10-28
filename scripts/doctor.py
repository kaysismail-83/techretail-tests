"""make doctor – kontrollerar att din miljö är redo för kursen.

Varje kontroll skriver OK, FEL eller INFO. Vid FEL står det exakt vad du ska göra.
"""

from __future__ import annotations

import importlib.metadata as md
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL = os.environ.get("TECHRETAIL_URL", "http://127.0.0.1:8000").rstrip("/")
EXPECTED = {"pytest": "9.1.1", "pytest-playwright": "0.10.0", "playwright": "1.64.0", "httpx": "0.28.1"}

problems = 0


def ok(text: str) -> None:
    print(f"  [OK]   {text}")


def fail(text: str, fix: str) -> None:
    global problems
    problems += 1
    print(f"  [FEL]  {text}")
    for line in fix.strip().splitlines():
        print(f"         {line}")


def info(text: str) -> None:
    print(f"  [INFO] {text}")


def run(cmd: list[str]) -> str | None:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=20, cwd=ROOT)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def check_python() -> None:
    v = sys.version_info
    if v >= (3, 12):
        ok(f"Python {v.major}.{v.minor}.{v.micro}")
    else:
        fail(f"Python {v.major}.{v.minor} är för gammal (minst 3.12 krävs).",
             "Kör:  uv python install 3.12  och sedan  uv sync")


def check_uv() -> None:
    version = run(["uv", "--version"])
    if version:
        ok(version)
    else:
        fail("uv hittas inte.", "Installera uv: se README.md, avsnittet 'Lokalt'.")


def check_packages() -> None:
    missing = []
    for name, version in EXPECTED.items():
        try:
            installed = md.version(name)
        except md.PackageNotFoundError:
            missing.append(name)
            continue
        if installed != version:
            fail(f"{name} {installed} är installerat, kursen använder {version}.", "Kör:  uv sync")
    try:
        shop = md.version("techretail-shop")
        ok(f"Kursens paket är installerade (pytest {EXPECTED['pytest']}, Playwright {EXPECTED['playwright']}, butiken {shop})")
    except md.PackageNotFoundError:
        missing.append("techretail-shop")
    if missing:
        fail(f"Paket saknas: {', '.join(missing)}.", "Kör:  uv sync")


def check_browser() -> None:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            version = browser.version
            browser.close()
        ok(f"Playwright kan starta Chromium {version}")
    except Exception as exc:  # noqa: BLE001 – vi vill visa alla fel på ett vänligt sätt
        first = str(exc).strip().splitlines()[0] if str(exc).strip() else type(exc).__name__
        fail(f"Playwright kan inte starta Chromium ({first[:90]}).",
             "Kör:  uv run playwright install --with-deps chromium\n"
             "(Lokalt på Mac eller Windows räcker:  uv run playwright install chromium)")


def check_shop() -> None:
    try:
        with urllib.request.urlopen(f"{URL}/health", timeout=3) as r:
            body = r.read().decode()
        ok(f"Butiken svarar på {URL}  {body}")
    except OSError:
        fail(f"Butiken svarar inte på {URL}.", "Starta den med:  make shop\nSe loggen med:     make shop-logg")


def check_git() -> None:
    if not shutil.which("git"):
        fail("git hittas inte.", "Installera git: https://git-scm.com/downloads (finns redan i Codespaces).")
        return
    if run(["git", "rev-parse", "--is-inside-work-tree"]) != "true":
        fail("Mappen är inte ett git-repo.", "Följ 'Kom igång' i README.md, steg 2.")
        return
    name = run(["git", "config", "user.name"])
    email = run(["git", "config", "user.email"])
    if name and email:
        ok(f"git är konfigurerat som {name} <{email}>")
    else:
        fail("git vet inte vem du är.",
             'Kör:  git config --global user.name "Ditt Namn"\n'
             '      git config --global user.email "din-epost@example.com"')
    remote = run(["git", "remote", "get-url", "origin"])
    if remote:
        ok(f"git-remote origin: {remote}")
    else:
        info("Ingen git-remote 'origin' ännu. Behövs för att pusha till GitHub (README.md, steg 2).")


def check_optional() -> None:
    k6 = run(["k6", "version"])
    info(f"k6: {k6.split()[1] if k6 else 'saknas'} (behövs från lektion 6, finns i Codespaces)")
    node = run(["node", "--version"])
    info(f"Node: {node or 'saknas'} (behövs i lektion 8, finns i Codespaces)")


def main() -> int:
    print("make doctor – kontrollerar din kursmiljö\n")
    for check in (check_python, check_uv, check_packages, check_browser, check_shop, check_git, check_optional):
        check()
    print()
    if problems:
        print(f"{problems} problem hittades. Åtgärda dem uppifrån och ned och kör  make doctor  igen.")
        print("Fastnar du? Klistra in hela utskriften i kursens hjälpkanal.")
        return 1
    print("Allt ser bra ut. Du är redo för kursen.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
