from playwright.async_api import Page, Locator
from .base import BasePage


class AboutPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def title(self) -> Locator:
        return self.page.locator(".about-hero-title")

    @property
    def statement_heading(self) -> Locator:
        return self.page.locator("text=Statement")

    @property
    def bio_heading(self) -> Locator:
        return self.page.locator("text=BIO")
