from playwright.async_api import Page, Locator
from .base import BasePage


class CheckoutPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def title(self) -> Locator:
        return self.page.locator(".product-detail-title")

    @property
    def checkout_rows(self) -> Locator:
        return self.page.locator("tr.cart-tr")

    @property
    def total_price(self) -> Locator:
        return self.page.locator(".cart-subtotal-value")

    @property
    def back_to_cart_link(self) -> Locator:
        return self.page.locator(".checkout-back-link")

    @property
    def proceed_to_payment_button(self) -> Locator:
        return self.page.locator("button:has-text('Proceed to Payment')")

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

    async def proceed_to_payment(self) -> None:
        await self.proceed_to_payment_button.click()

    async def click_back_to_cart(self) -> None:
        await self.back_to_cart_link.click()
