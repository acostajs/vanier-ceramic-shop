from playwright.async_api import Page, Locator
from .base import BasePage


class LoginPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def username_input(self) -> Locator:
        return self.page.locator("#id_username")

    @property
    def password_input(self) -> Locator:
        return self.page.locator("#id_password")

    @property
    def submit_button(self) -> Locator:
        return self.page.locator("button[type='submit']:has-text('Log In')")

    @property
    def register_link(self) -> Locator:
        return self.page.locator("a:has-text('Dont have an account? Register')")

    async def login(self, username: str, password: str) -> None:
        await self.username_input.fill(username)
        await self.password_input.fill(password)
        await self.submit_button.click()
