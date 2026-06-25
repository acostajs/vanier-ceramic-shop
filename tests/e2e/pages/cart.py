from playwright.async_api import Page, Locator
from .base import BasePage


class CartPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def title(self) -> Locator:
        return self.page.locator(".product-detail-title")

    @property
    def cart_rows(self) -> Locator:
        return self.page.locator("tr.cart-tr")

    @property
    def total_price(self) -> Locator:
        return self.page.locator(".cart-subtotal-value")

    @property
    def clear_cart_button(self) -> Locator:
        return self.page.locator("button:has-text('Clear Cart')")

    @property
    def checkout_button(self) -> Locator:
        return self.page.locator("a:has-text('Checkout')")

    @property
    def empty_cart_message(self) -> Locator:
        return self.page.locator("p:has-text('Your cart is empty.')")

    @property
    def continue_shopping_button(self) -> Locator:
        return self.page.locator("a:has-text('Continue Shopping')")

    async def get_row_by_product_name(self, name: str) -> Locator:
        return self.page.locator(f"tr.cart-tr:has(.cart-item-name:has-text('{name}'))")

    async def update_quantity(self, product_name: str, quantity: int) -> None:
        row = await self.get_row_by_product_name(product_name)
        input_field = row.locator("input.cart-qty-input")
        await input_field.fill(str(quantity))
        await row.locator("button.cart-update-btn").click()

    async def remove_product(self, product_name: str) -> None:
        row = await self.get_row_by_product_name(product_name)
        await row.locator("button.cart-remove-btn").click()

    async def click_checkout(self) -> None:
        await self.checkout_button.click()

    async def clear_cart(self) -> None:
        await self.clear_cart_button.click()
