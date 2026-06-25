from playwright.async_api import Page, Locator
from .base import BasePage


class BillingPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def address_line1_input(self) -> Locator:
        return self.page.locator("#id_billing_address_line1")

    @property
    def address_line2_input(self) -> Locator:
        return self.page.locator("#id_billing_address_line2")

    @property
    def city_input(self) -> Locator:
        return self.page.locator("#id_billing_city")

    @property
    def postal_code_input(self) -> Locator:
        return self.page.locator("#id_billing_postal_code")

    @property
    def country_input(self) -> Locator:
        return self.page.locator("#id_billing_country")

    @property
    def submit_button(self) -> Locator:
        return self.page.locator("button[type='submit']:has-text('Submit')")

    @property
    def go_back_link(self) -> Locator:
        return self.page.locator("a:has-text('Go Back')")

    async def update_address(
        self,
        line1: str,
        line2: str,
        city: str,
        postal_code: str,
        country: str,
    ) -> None:
        await self.address_line1_input.fill(line1)
        await self.address_line2_input.fill(line2)
        await self.city_input.fill(city)
        await self.postal_code_input.fill(postal_code)
        await self.country_input.fill(country)
        await self.submit_button.click()
