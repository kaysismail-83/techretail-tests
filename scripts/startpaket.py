"""Lägg till veckans startpaket från kursledaren (zip-fil från Teams).

    make startpaket ZIP=startpaket-l3.zip

Ett startpaket innehåller bara NYA filer för lektionen. Skriptet lägger till dem
och rör aldrig en fil som redan finns. Därefter görs en commit.
"""

from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1]:
        print("Ange paketet:  make startpaket ZIP=startpaket-l3.zip")
        return 2
    package = Path(sys.argv[1]).expanduser()
    if not package.is_absolute():
        package = (Path.cwd() / package).resolve()
    if not package.exists():
        print(f"Hittar inte {package}. Ladda upp zip-filen till repots rotmapp och försök igen.")
        return 2

    added, skipped = [], []
    with zipfile.ZipFile(package) as zf:
        for info in zf.infolist():
            parts = PurePosixPath(info.filename).parts
            rel = PurePosixPath(*parts[1:]) if parts and parts[0].startswith("techretail-tests") else PurePosixPath(*parts)
            if info.is_dir() or not rel.parts or ".." in rel.parts:
                continue
            target = ROOT / str(rel)
            if target.exists():
                skipped.append(str(rel))
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(zf.read(info))
            added.append(str(rel))

    if not added:
        print("Inga nya filer – startpaketet är redan på plats.")
        return 0
    if git("rev-parse", "--is-inside-work-tree").stdout.strip() == "true":
        git("add", "--", *added)
        git("commit", "-m", f"Startpaket: {package.stem}")
    print(f"Klart. {len(added)} nya filer från {package.stem}:")
    for name in added:
        print(f"  + {name}")
    if skipped:
        print(f"{len(skipped)} filer fanns redan och lämnades orörda.")
    print("Nästa steg:  make test  och  git push")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
