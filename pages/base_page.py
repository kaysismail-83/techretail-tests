"""BasePage: det som finns på alla sidor i butiken (given kod, lektion 2).

Ett Page Object samlar lokaliserare och handlingar för en sida på ett ställe.
Om butiken ändras behöver du bara rätta här, inte i varje test.

Lokaliseringsordning i kursen:
  1. get_by_role / get_by_label  (som en användare eller skärmläsare ser sidan)
  2. get_by_test_id              (attributet data-test, se conftest.py)
  3. CSS
  4. XPath, bara om inget annat går
"""

from playwright.sync_api import Page, expect


class BasePage:
    path = "/"

    def __init__(self, page: Page):
        self.page = page
        self.cart_link = page.get_by_role("link", name="Kundvagn")
        self.cart_badge = page.get_by_test_id("cart-badge")
        self.user_name = page.get_by_test_id("user-name")
        self.toast = page.get_by_test_id("toast")

    def open(self):
        """Gå till sidan. Adressen är relativ till base_url (se conftest.py)."""
        self.page.goto(self.path)
        return self

    def expect_cart_count(self, count: int) -> None:
        """Vänta tills kundvagnsbadgen visar rätt antal.

        expect väntar automatiskt (upp till 5 sekunder). Använd aldrig
        time.sleep() eller wait_for_timeout(). Det ger instabila tester.
        """
        expect(self.cart_badge).to_have_text(str(count))
