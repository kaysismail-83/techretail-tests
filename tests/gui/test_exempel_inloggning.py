"""Givna exempel på GUI-tester med Page Objects (lektion 2). Läs dem innan du skriver egna."""

from playwright.sync_api import expect

from pages.login_page import LoginPage
from testdata import LOCKED_USER, STANDARD_USER


def test_exempel_inloggad_kund_ser_sitt_namn(page, logged_in_user):
    # Arrange och Act sker i fixturen logged_in_user.
    # Assert
    expect(LoginPage(page).user_name).to_contain_text(logged_in_user.name)


def test_exempel_fel_losenord_visar_felmeddelande(page):
    # Arrange
    login_page = LoginPage(page).open()
    # Act
    login_page.login(STANDARD_USER.email, "fel-losenord")
    # Assert
    expect(login_page.error_message).to_have_text("Fel e-post eller lösenord.")


def test_exempel_last_konto_kan_inte_logga_in(page):
    login_page = LoginPage(page).open()
    login_page.login(LOCKED_USER.email, LOCKED_USER.password)
    expect(login_page.error_message).to_contain_text("Kontot är låst")
