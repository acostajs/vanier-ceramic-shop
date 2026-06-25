from playwright.async_api import Page, Locator
from .base import BasePage


class ShopPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def title(self) -> Locator:
        return self.page.locator(".shop-hero-title")

    @property
    def collection_cards(self) -> Locator:
        return self.page.locator(".collections-grid .collection-card")

    async def get_collection_card_by_name(self, name: str) -> Locator:
        return self.page.locator(
            f".collections-grid .collection-card:has(.collection-card-title:has-text('{name}'))"
        )

    async def click_collection_by_name(self, name: str) -> None:
        card = await self.get_collection_card_by_name(name)
        await card.locator("a.collection-card-link").click()
