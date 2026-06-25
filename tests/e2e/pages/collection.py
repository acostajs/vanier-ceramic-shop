from playwright.async_api import Page, Locator
from .base import BasePage


class CollectionPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def title(self) -> Locator:
        return self.page.locator(".collection-banner-title")

    @property
    def description(self) -> Locator:
        return self.page.locator(".collection-banner-desc")

    @property
    def product_cards(self) -> Locator:
        return self.page.locator(".collections-grid .collection-card")

    async def get_product_card_by_name(self, name: str) -> Locator:
        return self.page.locator(
            f".collections-grid .collection-card:has(.product-card-title:has-text('{name}'))"
        )

    async def click_product_details_by_name(self, name: str) -> None:
        card = await self.get_product_card_by_name(name)
        await card.locator("a.product-card-link").click()
