"""Mät hur lång tid en testkörning tar och spara resultatet (lektion 3).

    make matning ETIKETT=fore             # mäter hela sviten:  pytest
    make matning ETIKETT=efter ARGS="-m smoke"

Varje mätning blir en rad i docs/matningar.csv. Jämför före och efter en
optimering och skriv in slutsatsen i docs/teststrategi.md och i AI-loggen.
"""

from __future__ import annotations

import csv
import re
import shlex
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_FILE = ROOT / "docs" / "matningar.csv"
FIELDS = ["datum", "etikett", "kommando", "sekunder", "passed", "failed"]


def main() -> int:
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        print('Ange en etikett:  make matning ETIKETT=fore  (och senare ETIKETT=efter)')
        return 2
    label = sys.argv[1].strip()
    args = shlex.split(" ".join(sys.argv[2:]))
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *args]
    start = time.perf_counter()
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    seconds = round(time.perf_counter() - start, 2)
    tail = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
    passed = int(m.group(1)) if (m := re.search(r"(\d+) passed", tail)) else 0
    failed = int(m.group(1)) if (m := re.search(r"(\d+) failed", tail)) else 0

    new_file = not CSV_FILE.exists()
    CSV_FILE.parent.mkdir(exist_ok=True)
    with CSV_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow({"datum": date.today().isoformat(), "etikett": label,
                         "kommando": "pytest " + " ".join(args), "sekunder": seconds,
                         "passed": passed, "failed": failed})
    print(f"{label}: {seconds} s ({passed} passed, {failed} failed) – sparat i docs/matningar.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
