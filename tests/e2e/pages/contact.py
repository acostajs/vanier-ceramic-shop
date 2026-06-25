from playwright.async_api import Page, Locator
from .base import BasePage


class ContactPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def name_input(self) -> Locator:
        return self.page.locator("#id_name")

    @property
    def email_input(self) -> Locator:
        return self.page.locator("#id_email")

    @property
    def subject_input(self) -> Locator:
        return self.page.locator("#id_subject")

    @property
    def message_input(self) -> Locator:
        return self.page.locator("#id_message")

    @property
    def submit_button(self) -> Locator:
        return self.page.locator("button[type='submit'].contact-submit-btn")

    async def submit_message(
        self,
        name: str,
        email: str,
        subject: str,
        message: str,
    ) -> None:
        await self.name_input.fill(name)
        await self.email_input.fill(email)
        await self.subject_input.fill(subject)
        await self.message_input.fill(message)
        await self.submit_button.click()
