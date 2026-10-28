"""LoginPage – inloggningssidan /logga-in (given kod, lektion 2)."""

from playwright.sync_api import Page

from pages.base_page import BasePage


class LoginPage(BasePage):
    path = "/logga-in"

    def __init__(self, page: Page):
        super().__init__(page)
        self.email_input = page.get_by_label("E-post")
        self.password_input = page.get_by_label("Lösenord")
        self.login_button = page.get_by_role("button", name="Logga in")
        self.error_message = page.get_by_role("alert")

    def login(self, email: str, password: str) -> None:
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.login_button.click()
