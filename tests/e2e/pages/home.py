from playwright.async_api import Page, Locator
from .base import BasePage


class HomePage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def shop_collections_button(self) -> Locator:
        return self.page.locator(".hero-actions a.button-primary")

    @property
    def read_biography_button(self) -> Locator:
        return self.page.locator(".hero-actions a.button-secondary")

    @property
    def recent_work_section(self) -> Locator:
        return self.page.locator(".recent-work-section")

    @property
    def recent_work_cards(self) -> Locator:
        return self.page.locator(".product-slider a.product-card-wrapper-link")

    @property
    def read_my_story_button(self) -> Locator:
        return self.page.locator(".about-me-section a.button-terracotta")

    @property
    def get_in_touch_button(self) -> Locator:
        return self.page.locator(".home-contact-section a.button-primary")

    async def click_shop_collections(self) -> None:
        await self.shop_collections_button.click()

    async def click_read_biography(self) -> None:
        await self.read_biography_button.click()

    async def click_read_my_story(self) -> None:
        await self.read_my_story_button.click()

    async def click_get_in_touch(self) -> None:
        await self.get_in_touch_button.click()
