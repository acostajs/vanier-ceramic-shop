from playwright.async_api import Page, Locator
from .base import BasePage


class CheckoutCancelPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def cancel_title(self) -> Locator:
        return self.page.locator(".order-status-title")

    @property
    def back_to_cart_link(self) -> Locator:
        return self.page.locator("a:has-text('Back to cart')")

    @property
    def continue_browsing_link(self) -> Locator:
        return self.page.locator("a:has-text('Continue browsing')")

    async def click_back_to_cart(self) -> None:
        await self.back_to_cart_link.click()

    async def click_continue_browsing(self) -> None:
        await self.continue_browsing_link.click()
