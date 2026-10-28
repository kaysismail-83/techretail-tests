"""Hjälpfunktioner för milstolpekontrollerna. Du behöver inte ändra något här."""

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run_pytest(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", *args],
        cwd=ROOT, capture_output=True, text=True, timeout=600,
    )


def own_tests(folder: str) -> list[str]:
    """Alla insamlade tester i mappen som inte är givna (test_exempel_... eller GIVEN_TESTS)."""
    result = run_pytest("--collect-only", "-q", folder)
    if result.returncode not in (0, 5):
        raise AssertionError(
            f"Testerna i {folder} går inte att läsa in. Det beror oftast på ett skrivfel.\n"
            f"Kör: uv run pytest {folder}\n\n{result.stdout[-2000:]}"
        )
    ids = [line.strip() for line in result.stdout.splitlines() if "::" in line]
    names = [i for i in ids if not i.split("::")[-1].startswith("test_exempel_")]
    return [i for i in names if i.split("::")[-1].split("[")[0] not in GIVEN_TESTS]


def summary(result: subprocess.CompletedProcess) -> str:
    lines = [line for line in result.stdout.splitlines() if line.startswith(("FAILED", "ERROR")) or " passed" in line or " failed" in line]
    return "\n".join(lines[-15:])


def source_files(*folders: str) -> list[Path]:
    files = []
    for folder in folders:
        files += [p for p in (ROOT / folder).rglob("*.py") if "milestones" not in p.parts]
    return files


def fixed_waits(path: Path) -> list[int]:
    """Radnummer där koden anropar time.sleep(...) eller wait_for_timeout(...). Kommentarer räknas inte."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    lines = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
            if name in {"sleep", "wait_for_timeout"}:
                lines.append(node.lineno)
    return lines


def own_test_functions_calling(path: Path, callee: str) -> list[str]:
    """Egna testfunktioner (inte test_exempel_) i filen som anropar callee(...)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_") and not node.name.startswith("test_exempel_"):
            for inner in ast.walk(node):
                if isinstance(inner, ast.Call) and getattr(inner.func, "id", None) == callee:
                    found.append(node.name)
                    break
    return found


def raises_not_implemented(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Raise) and node.exc is not None:
            target = node.exc.func if isinstance(node.exc, ast.Call) else node.exc
            if getattr(target, "id", None) == "NotImplementedError":
                return True
    return False


def git_commit_count() -> int | None:
    try:
        out = subprocess.run(["git", "rev-list", "--count", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    except FileNotFoundError:
        return None
    return int(out.stdout.strip()) if out.returncode == 0 else None


GIVEN_FIXTURES = {"base_url", "shop", "page", "logged_in_user", "api_client", "logged_in_api_client"}
GIVEN_TESTS = {"test_orderhistorik_visar_kundens_ordrar"}


def collected(*args: str) -> list[str]:
    """Node-id för insamlade tester (utan milstolpekontrollerna)."""
    result = run_pytest("--collect-only", "-q", *args)
    return [line.strip() for line in result.stdout.splitlines() if "::" in line and "milestones" not in line]


def _fixture_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for dec in node.decorator_list:
                target = dec.func if isinstance(dec, ast.Call) else dec
                if (getattr(target, "attr", None) or getattr(target, "id", None)) == "fixture":
                    names.add(node.name)
    return names


def own_fixtures_used() -> set[str]:
    """Egna fixtures (inte de givna) som minst ett test använder som parameter."""
    files = [p for p in ROOT.rglob("*.py") if ".venv" not in p.parts and "milestones" not in p.parts
             and not any(part.startswith("utmaning") for part in p.parts)]
    fixtures = set().union(*(_fixture_names(p) for p in files)) - GIVEN_FIXTURES
    params = set()
    for p in ROOT.joinpath("tests").rglob("test_*.py"):
        if "milestones" in p.parts or any(part.startswith("utmaning") for part in p.parts):
            continue
        for node in ast.walk(ast.parse(p.read_text(encoding="utf-8"))):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                params |= {a.arg for a in node.args.args}
    return fixtures & params


def section_words(number: int, file: str = "docs/teststrategi.md") -> int:
    """Antal egna ord under rubriken '## <number>.' – mallens kursiva frågor och tomma tabellrader räknas inte."""
    text = (ROOT / file).read_text(encoding="utf-8")
    current, words = None, 0
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].split(".")[0].strip()
            continue
        stripped = line.strip()
        if current != str(number) or not stripped or stripped.startswith(("*", ">", "|---", "<!--")):
            continue
        if stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if all(not c or c.startswith("MT-01") for c in cells[1:]):
                continue
        words += len(stripped.split())
    return words


def outcomes(*args: str) -> dict[str, str]:
    """Kör pytest och returnerar {node-id: utfall} där utfall är PASSED, FAILED, ERROR, XFAIL, XPASS eller SKIPPED."""
    result = run_pytest("-q", "-rA", *args)
    found = {}
    for line in result.stdout.splitlines():
        parts = line.split(" ", 1)
        # Rader som "SKIPPED [1] fil.py:10: orsak" är sammanfattningar, inte utfall för ett enskilt test.
        if len(parts) == 2 and parts[1].startswith("["):
            continue
        if len(parts) == 2 and parts[0] in {"PASSED", "FAILED", "ERROR", "XFAIL", "XPASS", "SKIPPED"}:
            found[parts[1].split(" - ")[0].strip()] = parts[0]
    return found


def functions_with_marker(path: Path, marker: str) -> list[str]:
    """Testfunktioner i filen som har dekoratorn @pytest.mark.<marker>."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            for dec in node.decorator_list:
                target = dec.func if isinstance(dec, ast.Call) else dec
                if getattr(target, "attr", None) == marker:
                    names.append(node.name)
    return names


def own_words(file: str) -> int:
    """Antal egna ord i ett dokument. Mallens kursiva frågor, citat, kommentarer och rubriker räknas inte."""
    path = ROOT / file
    if not path.exists():
        return 0
    words = 0
    in_comment = False
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("<!--"):
            in_comment = "-->" not in stripped
            continue
        if in_comment:
            in_comment = "-->" not in stripped
            continue
        if not stripped or stripped.startswith(("#", "*", ">", "|---", "```")):
            continue
        if stripped.startswith("|") and all(not c.strip() for c in stripped.strip("|").split("|")[1:]):
            continue
        words += len(stripped.split())
    return words


def ai_log_posts() -> list[str]:
    """Rubrikerna för studentens egna poster i ai/AI-logg.md (under '## Mina poster')."""
    text = (ROOT / "ai" / "AI-logg.md").read_text(encoding="utf-8")
    mine = text.split("## Mina poster", 1)[-1].split("## Summering", 1)[0]
    return [line[4:].strip() for line in mine.splitlines() if line.startswith("### ")]
