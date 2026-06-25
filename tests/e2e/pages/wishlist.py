from playwright.async_api import Page, Locator
from .base import BasePage


class WishlistPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def title(self) -> Locator:
        return self.page.locator(".product-detail-title")

    @property
    def wishlist_rows(self) -> Locator:
        return self.page.locator("tr.cart-tr")

    @property
    def clear_wishlist_button(self) -> Locator:
        return self.page.locator("button:has-text('Clear Wishlist')")

    @property
    def continue_shopping_button(self) -> Locator:
        return self.page.locator("a:has-text('Continue Shopping')")

    @property
    def empty_wishlist_message(self) -> Locator:
        return self.page.locator("p:has-text('Your wishlist is empty.')")

    async def get_row_by_product_name(self, name: str) -> Locator:
        return self.page.locator(f"tr.cart-tr:has(.cart-item-name:has-text('{name}'))")

    async def remove_product(self, product_name: str) -> None:
        row = await self.get_row_by_product_name(product_name)
        await row.locator("button.cart-remove-btn").click()

    async def transfer_to_cart(self, product_name: str) -> None:
        row = await self.get_row_by_product_name(product_name)
        await row.locator("button.cart-update-btn").click()

    async def clear_wishlist(self) -> None:
        await self.clear_wishlist_button.click()
