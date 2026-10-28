"""Milstolpe lektion 2 – kontrolleras med:  make milstolpe L=2  (eller uv run pytest -m milestone_l2 -v)

Butiken måste vara igång (make shop). Samma lista används i bedömningsmallen.
"""

import pytest
from playwright.sync_api import expect

from tests.milestones.hjalp import (
    ROOT,
    fixed_waits,
    own_test_functions_calling,
    own_tests,
    raises_not_implemented,
    run_pytest,
    source_files,
    summary,
)

pytestmark = [pytest.mark.milestone, pytest.mark.milestone_l2]

MIN_OWN_GUI_TESTS = 3


def test_l2_product_page_ar_implementerad(page):
    todo_left = raises_not_implemented(ROOT / "pages" / "product_page.py")
    assert not todo_left, "Det finns kvar NotImplementedError i pages/product_page.py (TODO 2 och 3)."
    from pages.product_page import ProductPage

    product_page = ProductPage(page)
    missing = [a for a in ("name", "price", "quantity_input", "add_to_cart_button") if getattr(product_page, a, None) is None]
    assert not missing, f"Lokaliserare saknas i ProductPage (TODO 1): {', '.join(missing)}"


def test_l2_product_page_fungerar_mot_butiken(page):
    from pages.product_page import ProductPage

    product_page = ProductPage(page)
    assert product_page.open(1) is product_page, "ProductPage.open ska returnera self."
    expect(product_page.name).to_have_text("Skruvdragare 18 V")
    expect(product_page.price).to_contain_text("1 499,00 kr")
    product_page.add_to_cart(2)
    product_page.expect_cart_count(2)


def test_l2_minst_tre_egna_gui_tester():
    own = own_tests("tests/gui")
    assert len(own) >= MIN_OWN_GUI_TESTS, (
        f"Du har {len(own)} egna GUI-tester. Minst {MIN_OWN_GUI_TESTS} krävs. Skriv dem i tests/gui/test_produkt.py."
    )


def test_l2_egna_gui_tester_anvander_product_page():
    uses = [name for p in (ROOT / "tests" / "gui").rglob("test_*.py") for name in own_test_functions_calling(p, "ProductPage")]
    assert uses, "Dina GUI-tester ska använda ProductPage, till exempel ProductPage(page).open(1)."


def test_l2_inga_fasta_vantetider():
    offenders = [f"{p.relative_to(ROOT)} rad {line}" for p in source_files("pages", "tests/gui") for line in fixed_waits(p)]
    assert not offenders, (
        "Fasta väntetider (time.sleep eller wait_for_timeout) ger instabila tester. "
        f"Använd expect(...) i stället. Hittade i: {', '.join(offenders)}"
    )


def test_l2_alla_gui_tester_ar_grona():
    result = run_pytest("tests/gui", "-q")
    assert result.returncode == 0, (
        "Minst ett GUI-test fallerar. Kör  uv run pytest tests/gui -v --tracing retain-on-failure\n"
        "och öppna spåret (trace) som README.md beskriver.\n\n" + summary(result)
    )
