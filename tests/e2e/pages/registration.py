from playwright.async_api import Page, Locator
from .base import BasePage


class RegisterPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def username_input(self) -> Locator:
        return self.page.locator("#id_username")

    @property
    def first_name_input(self) -> Locator:
        return self.page.locator("#id_first_name")

    @property
    def last_name_input(self) -> Locator:
        return self.page.locator("#id_last_name")

    @property
    def email_input(self) -> Locator:
        return self.page.locator("#id_email")

    @property
    def password1_input(self) -> Locator:
        return self.page.locator("#id_password1")

    @property
    def password2_input(self) -> Locator:
        return self.page.locator("#id_password2")

    @property
    def submit_button(self) -> Locator:
        return self.page.locator("button[type='submit']:has-text('Register')")

    @property
    def login_link(self) -> Locator:
        return self.page.locator("a:has-text('Already have an account? Log in')")

    async def register(
        self,
        username: str,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
    ) -> None:
        await self.username_input.fill(username)
        await self.first_name_input.fill(first_name)
        await self.last_name_input.fill(last_name)
        await self.email_input.fill(email)
        await self.password1_input.fill(password)
        await self.password2_input.fill(password)
        await self.submit_button.click()
