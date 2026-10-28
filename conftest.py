"""Gemensamma fixtures för alla tester (given kod).

Fixtures med fasta namn som används i kursen:
  base_url                adressen till TechRetail-butiken
  shop                    kontrollerar att butiken svarar
  page                    en ny webbläsarflik per test (från pytest-playwright)
  logged_in_user          loggar in standardkunden i webbläsaren och returnerar kontot
  api_client              API-klient utan inloggning (lektion 4)
  logged_in_api_client    API-klient inloggad som standardkunden, med tom kundvagn (lektion 4)
"""

import os

import httpx
import pytest
from playwright.sync_api import Page, expect

from testdata import STANDARD_USER, Account

DEFAULT_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session")
def base_url() -> str:
    """Butikens adress. Ändra med miljövariabeln TECHRETAIL_URL vid behov."""
    return os.environ.get("TECHRETAIL_URL", DEFAULT_URL).rstrip("/")


@pytest.fixture(scope="session")
def shop(base_url: str) -> str:
    """Kontrollerar en gång per körning att butiken svarar."""
    try:
        httpx.get(f"{base_url}/health", timeout=5).raise_for_status()
    except httpx.HTTPError:
        pytest.exit(
            f"\nTechRetail-butiken svarar inte på {base_url}.\n"
            "Starta den med:  make shop\n"
            "Kontrollera sedan med:  make doctor\n",
            returncode=3,
        )
    return base_url


@pytest.fixture
def page(page: Page, playwright, shop) -> Page:
    """Samma page som i pytest-playwright, men get_by_test_id läser attributet data-test."""
    playwright.selectors.set_test_id_attribute("data-test")
    return page


def _empty_cart(base_url: str, account: Account) -> None:
    with httpx.Client(base_url=base_url, timeout=10) as client:
        token = client.post("/api/auth/token", json={"email": account.email, "password": account.password})
        token.raise_for_status()
        headers = {"Authorization": f"Bearer {token.json()['access_token']}"}
        client.delete("/api/cart", headers=headers).raise_for_status()


@pytest.fixture
def logged_in_user(page: Page, base_url: str) -> Account:
    """Tömmer standardkundens kundvagn och loggar in i webbläsaren.

    Testet äger sin testdata: varje test börjar med en tom kundvagn.
    """
    from pages.login_page import LoginPage

    _empty_cart(base_url, STANDARD_USER)
    login_page = LoginPage(page).open()
    login_page.login(STANDARD_USER.email, STANDARD_USER.password)
    expect(login_page.user_name).to_contain_text(STANDARD_USER.name)
    return STANDARD_USER


@pytest.fixture
def api_client(shop):
    """API-klient (httpx) mot butiken, utan inloggning. Klassen finns i api/client.py."""
    from api.client import TechRetailClient

    client = TechRetailClient(shop)
    yield client
    client.close()


@pytest.fixture
def logged_in_api_client(api_client):
    """API-klient inloggad som standardkunden. Kundvagnen töms först, så testet äger sin testdata."""
    api_client.login(STANDARD_USER.email, STANDARD_USER.password)
    api_client.clear_cart()
    return api_client


def pytest_collection_modifyitems(config, items):
    """Milstolpekontrollerna körs bara när du ber om dem, till exempel pytest -m milestone_l1."""
    if "milestone" in (config.getoption("markexpr") or ""):
        return
    keep = [item for item in items if item.get_closest_marker("milestone") is None]
    skipped = [item for item in items if item.get_closest_marker("milestone") is not None]
    if skipped:
        config.hook.pytest_deselected(items=skipped)
        items[:] = keep
