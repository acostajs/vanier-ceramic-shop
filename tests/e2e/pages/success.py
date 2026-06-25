from playwright.async_api import Page, Locator
from .base import BasePage


class CheckoutSuccessPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def success_title(self) -> Locator:
        return self.page.locator(".order-status-title")

    @property
    def continue_browsing_link(self) -> Locator:
        return self.page.locator("a:has-text('Continue browsing')")

    @property
    def view_orders_link(self) -> Locator:
        return self.page.locator("a:has-text('View your orders')")

    async def click_continue_browsing(self) -> None:
        await self.continue_browsing_link.click()

    async def click_view_orders(self) -> None:
        await self.view_orders_link.click()
