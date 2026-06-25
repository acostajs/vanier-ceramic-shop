from playwright.async_api import Page, Locator
from .base import BasePage


class OrderDetailsPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def title(self) -> Locator:
        return self.page.locator(".product-detail-title")

    @property
    def payment_id(self) -> Locator:
        return self.page.locator(".order-payment-id-val")

    @property
    def total_price(self) -> Locator:
        return self.page.locator(".cart-subtotal-value")

    @property
    def status_badge(self) -> Locator:
        return self.page.locator(".order-status-badge")

    @property
    def order_date(self) -> Locator:
        return self.page.locator(".order-date-val")

    @property
    def order_item_rows(self) -> Locator:
        return self.page.locator(".order-item-row")

    @property
    def back_to_account_link(self) -> Locator:
        return self.page.locator(".checkout-back-link")

    async def click_back_to_account(self) -> None:
        await self.back_to_account_link.click()
