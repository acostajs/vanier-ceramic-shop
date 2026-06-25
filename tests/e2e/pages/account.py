from playwright.async_api import Page, Locator
from .base import BasePage


class AccountPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def username_title(self) -> Locator:
        return self.page.locator(".product-detail-title")

    @property
    def first_name_text(self) -> Locator:
        return self.page.locator(".profile-info-text:has-text('First name')")

    @property
    def last_name_text(self) -> Locator:
        return self.page.locator(".profile-info-text:has-text('Last name')")

    @property
    def email_text(self) -> Locator:
        return self.page.locator(".profile-info-text:has-text('Email')")

    @property
    def shipping_info_link(self) -> Locator:
        return self.page.locator("a:has-text('Update your Shipping Information')")

    @property
    def billing_info_link(self) -> Locator:
        return self.page.locator("a:has-text('Update your Billing Information')")

    @property
    def logout_link(self) -> Locator:
        return self.page.locator("a.logout-link")

    @property
    def order_items(self) -> Locator:
        return self.page.locator(".orders-list-item")

    async def click_update_shipping(self) -> None:
        await self.shipping_info_link.click()

    async def click_update_billing(self) -> None:
        await self.billing_info_link.click()

    async def logout(self) -> None:
        await self.logout_link.click()

    async def get_order_by_id(self, order_id: str) -> Locator:
        return self.page.locator(
            f".orders-list-item:has(.orders-item-id:has-text('{order_id}'))"
        )

    async def view_order_details(self, order_id: str) -> None:
        order = await self.get_order_by_id(order_id)
        await order.locator("a.cart-update-btn").click()
