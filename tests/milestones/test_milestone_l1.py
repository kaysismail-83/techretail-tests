"""Milstolpe lektion 1 – kontrolleras med:  make milstolpe L=1  (eller uv run pytest -m milestone_l1 -v)

Samma lista används i bedömningsmallen för inlämningen.
"""

import pytest

from tests.milestones.hjalp import git_commit_count, own_tests, run_pytest, summary

pytestmark = [pytest.mark.milestone, pytest.mark.milestone_l1]

MIN_OWN_UNIT_TESTS = 5


def test_l1_minst_fem_egna_komponenttester():
    own = own_tests("tests/unit")
    assert len(own) >= MIN_OWN_UNIT_TESTS, (
        f"Du har {len(own)} egna komponenttester. Minst {MIN_OWN_UNIT_TESTS} krävs.\n"
        "Skriv dem i tests/unit/test_pricing.py. Namnet ska börja med test_ men inte med test_exempel_."
    )


def test_l1_alla_komponenttester_ar_grona():
    result = run_pytest("tests/unit", "-q")
    assert result.returncode in (0, 5), (
        "Minst ett komponenttest fallerar. Kör  uv run pytest tests/unit -v  och läs felet.\n"
        "Är det testet eller koden som har fel? Tänk på kravet i src/techretail/pricing.py.\n\n" + summary(result)
    )


def test_l1_forsta_egna_commit():
    count = git_commit_count()
    assert count is not None, "Mappen är inte ett git-repo. Följ steg 2 i README.md (Kom igång)."
    assert count >= 2, (
        "Repot har bara startcommiten. Spara ditt arbete:\n"
        '  git add . && git commit -m "Lektion 1: egna komponenttester" && git push'
    )
