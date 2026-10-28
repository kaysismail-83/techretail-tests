"""Starta, stoppa och återställ TechRetail-butiken i bakgrunden.

Används av Makefile och av Codespaces vid start:
    uv run python scripts/shop.py start [--profil kurs]
    uv run python scripts/shop.py stop
    uv run python scripts/shop.py status
    uv run python scripts/shop.py reset

Butikens databas och logg hamnar i mappen .shop/ i repot (ignoreras av git).
Butikens inställningar läses från sut/shop.env. Miljövariabler i terminalen går före.
"""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".shop"
PID_FILE = STATE / "shop.pid"
LOG_FILE = STATE / "shop.log"
URL = os.environ.get("TECHRETAIL_URL", "http://127.0.0.1:8000").rstrip("/")


def healthy(timeout: float = 2.0) -> bool:
    try:
        with urllib.request.urlopen(f"{URL}/health", timeout=timeout) as r:
            return r.status == 200
    except OSError:
        return False


SHOP_ENV = ROOT / "sut" / "shop.env"


def read_shop_env() -> dict[str, str]:
    values = {}
    if SHOP_ENV.exists():
        for line in SHOP_ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip()
    return values


def shop_env(profile: str | None) -> dict[str, str]:
    env = {**read_shop_env(), **os.environ}
    env.setdefault("TECHRETAIL_HOME", str(STATE))
    if profile:
        env["TECHRETAIL_PROFILE"] = profile
    return env


def start(profile: str | None) -> int:
    if healthy():
        print(f"Butiken körs redan på {URL}")
        return 0
    STATE.mkdir(exist_ok=True)
    port = URL.rsplit(":", 1)[-1].split("/")[0]
    log = open(LOG_FILE, "a", encoding="utf-8")
    kwargs = {"start_new_session": True} if os.name != "nt" else {"creationflags": 0x00000008}
    proc = subprocess.Popen(
        [sys.executable, "-m", "techretail_shop.cli", "--port", port],
        cwd=ROOT, env=shop_env(profile), stdout=log, stderr=subprocess.STDOUT, **kwargs,
    )
    PID_FILE.write_text(str(proc.pid))
    for _ in range(60):
        if healthy(1):
            print(f"Butiken är igång på {URL}  (logg: .shop/shop.log)")
            return 0
        if proc.poll() is not None:
            break
        time.sleep(0.5)
    print("Butiken startade inte. De sista raderna i .shop/shop.log:", file=sys.stderr)
    print("\n".join(LOG_FILE.read_text(encoding="utf-8").splitlines()[-15:]), file=sys.stderr)
    print("Tips: är port 8000 upptagen? Kör  make shop-stop  och försök igen.", file=sys.stderr)
    return 1


def stop() -> int:
    if not PID_FILE.exists():
        print("Ingen butik startad härifrån." + (" (Men något svarar på porten.)" if healthy() else ""))
        return 0
    pid = int(PID_FILE.read_text())
    try:
        os.kill(pid, signal.SIGTERM)
        print("Butiken är stoppad.")
    except ProcessLookupError:
        print("Butiken var redan stoppad.")
    PID_FILE.unlink(missing_ok=True)
    return 0


def reset(profile: str | None) -> int:
    if healthy():
        req = urllib.request.Request(f"{URL}/test/reset", method="POST")
        with urllib.request.urlopen(req, timeout=10):
            pass
        print("Testdata är återställd.")
        return 0
    return subprocess.call([sys.executable, "-m", "techretail_shop.cli", "--reset"], env=shop_env(profile))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("action", choices=["start", "stop", "status", "reset", "restart"])
    parser.add_argument("--profil", default=os.environ.get("PROFIL") or None,
                        help="Butiksprofil, till exempel kurs (standard) eller l7-buggvariant")
    args = parser.parse_args()
    if args.action == "start":
        return start(args.profil)
    if args.action == "stop":
        return stop()
    if args.action == "restart":
        stop()
        time.sleep(1)
        return start(args.profil)
    if args.action == "reset":
        return reset(args.profil)
    print(f"Butiken {'svarar' if healthy() else 'svarar INTE'} på {URL}")
    return 0 if healthy() else 1


if __name__ == "__main__":
    raise SystemExit(main())
