from playwright.async_api import Page, Locator
from .base import BasePage


class ProductDetailPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def title(self) -> Locator:
        return self.page.locator(".product-detail-title")

    @property
    def description(self) -> Locator:
        return self.page.locator(".product-detail-desc")

    @property
    def price(self) -> Locator:
        return self.page.locator(
            ".product-detail-price, .product-detail-price-discounted"
        )

    @property
    def old_price(self) -> Locator:
        return self.page.locator(".product-detail-price-old")

    @property
    def quantity_input(self) -> Locator:
        return self.page.locator("#quantity")

    @property
    def add_to_cart_button(self) -> Locator:
        return self.page.locator("button[type='submit']:has-text('Add to Cart')")

    @property
    def sold_out_button(self) -> Locator:
        return self.page.locator(".button-sold-out")

    @property
    def add_to_wishlist_button(self) -> Locator:
        return self.page.locator("button[type='submit']:has-text('Add to Wishlist')")

    @property
    def stock_warning(self) -> Locator:
        return self.page.locator(".product-stock-warning")

    async def set_quantity(self, quantity: int) -> None:
        await self.quantity_input.fill(str(quantity))

    async def add_to_cart(self, quantity: int = 1) -> None:
        if quantity > 1:
            await self.set_quantity(quantity)
        await self.add_to_cart_button.click()

    async def add_to_wishlist(self) -> None:
        await self.add_to_wishlist_button.click()
