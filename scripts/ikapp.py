"""Kom ikapp med ett ikapp-paket från kursledaren (zip-fil från Teams).

    make ikapp ZIP=ikapp-l2-start.zip

Vad skriptet gör:
1. Sparar ditt nuvarande arbete i en commit och i en egen gren (mitt-arbete-fore-<paket>).
   Inget du har gjort försvinner.
2. Packar upp paketets kod (src, pages, tests, api, perf med flera) över din kod.
   Dina egna texter och resultat (docs/, ai/, perf/k6/tolkning.md, din k6-körning och din
   klassning av CI-fel) skrivs aldrig över. Saknade mallar läggs till.
3. Gör en commit med den nya koden.
"""

from __future__ import annotations

import subprocess
import sys
import zipfile
from datetime import date
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = ("src/", "pages/", "tests/", "scripts/", "sut/", ".github/", ".devcontainer/", ".vscode/", "api/", "perf/",
           "anonymisering/", "felsokning/", "mcp_server/", "evals/",
           "conftest.py", "testdata.py", "pyproject.toml", "uv.lock", "Makefile", "README.md")
# Studentens egna texter och resultat (betygsunderlag) skrivs aldrig över. Saknade mallar läggs till.
ADD_ONLY = ("docs/", "ai/", "perf/k6/tolkning.md", "perf/k6/resultat.json", "felsokning/ci-feldataset/urval-10.csv")


def git(*args: str, check: bool = True) -> str:
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if check and out.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} misslyckades:\n{out.stderr}")
    return out.stdout.strip()


def main() -> int:
    if len(sys.argv) != 2:
        print("Ange paketet:  make ikapp ZIP=ikapp-l2-start.zip")
        return 2
    package = Path(sys.argv[1]).expanduser()
    if not package.is_absolute():
        package = (Path.cwd() / package).resolve()
    if not package.exists():
        print(f"Hittar inte {package}. Ladda upp zip-filen till repots rotmapp och försök igen.")
        return 2
    if git("rev-parse", "--is-inside-work-tree", check=False) != "true":
        print("Mappen är inte ett git-repo. Följ 'Kom igång' i README.md först.")
        return 2

    name = package.stem
    backup = f"mitt-arbete-fore-{name}-{date.today().isoformat()}"
    n = 2
    while git("rev-parse", "--verify", "--quiet", backup, check=False):
        backup = f"mitt-arbete-fore-{name}-{date.today().isoformat()}-{n}"
        n += 1

    if git("status", "--porcelain"):
        git("add", "-A")
        git("commit", "-m", f"Sparar mitt arbete före {name}", check=False)
    git("branch", backup)

    with zipfile.ZipFile(package) as zf:
        members = []
        for info in zf.infolist():
            parts = PurePosixPath(info.filename).parts
            rel = PurePosixPath(*parts[1:]) if parts and parts[0].startswith("techretail-tests") else PurePosixPath(*parts)
            text = str(rel)
            if info.is_dir() or ".." in rel.parts:
                continue
            if text.startswith(ADD_ONLY):
                if (ROOT / text).exists():
                    continue
            elif not text.startswith(ALLOWED):
                continue
            members.append((info, text))
        if not members:
            print("Paketet innehåller ingen kod. Är det rätt zip-fil?")
            return 2
        for info, text in members:
            target = ROOT / text
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(zf.read(info))

    git("add", "-A")
    git("commit", "-m", f"Ikapp: {name}", check=False)
    print(f"Klart. {len(members)} filer från {name} är på plats.")
    print(f"Ditt tidigare arbete finns kvar i grenen {backup}.")
    print("Nästa steg:  uv sync  och sedan  make test  och  git push")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
