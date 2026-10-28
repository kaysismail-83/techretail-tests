"""ProductPage – produktsidan /produkter/<id> (lektion 2, din uppgift).

Öppna en produktsida i webbläsaren, till exempel http://127.0.0.1:8000/produkter/1,
och undersök den. Tips: högerklicka och välj "Inspektera", eller kör
    uv run playwright codegen http://127.0.0.1:8000/produkter/1

Titta på login_page.py för att se hur ett färdigt Page Object ser ut.
"""

from playwright.sync_api import Page

from pages.base_page import BasePage


class ProductPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # TODO 1: Skapa lokaliserare för
        #   - produktens namn (rubriken på sidan)       tips: get_by_role("heading", level=1)
        #   - priset                                     tips: get_by_test_id("product-price")
        #   - fältet för antal                           tips: get_by_label(...)
        #   - knappen "Lägg i kundvagn"                  tips: get_by_role("button", name=...)
        self.name = None
        self.price = None
        self.quantity_input = None
        self.add_to_cart_button = None

    def open(self, product_id: int) -> "ProductPage":
        """Gå till produktsidan för product_id och returnera self."""
        # TODO 2: Gå till /produkter/<product_id>. Titta på BasePage.open för inspiration.
        raise NotImplementedError("TODO 2: implementera ProductPage.open")

    def add_to_cart(self, quantity: int = 1) -> None:
        """Fyll i antal och klicka på "Lägg i kundvagn"."""
        # TODO 3: Fyll i quantity i antal-fältet (som text) och klicka på knappen.
        raise NotImplementedError("TODO 3: implementera ProductPage.add_to_cart")
