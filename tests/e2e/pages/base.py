from playwright.async_api import Page, Locator


class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page

    async def navigate_to(self, url: str) -> None:
        """Navigates to a specific URL path."""
        await self.page.goto(url)

    # Navigation header elements
    @property
    def logo_link(self) -> Locator:
        return self.page.locator("a.nav-logo")

    @property
    def desktop_about_link(self) -> Locator:
        return self.page.locator(".nav-menu-desktop a[href*='/about/']")

    @property
    def desktop_account_link(self) -> Locator:
        return self.page.locator(".nav-menu-desktop a[href$='/account/']")

    @property
    def desktop_login_link(self) -> Locator:
        return self.page.locator(".nav-menu-desktop a[href*='/account/login/']")

    @property
    def desktop_register_link(self) -> Locator:
        return self.page.locator(".nav-menu-desktop a[href*='/account/registration/']")

    @property
    def desktop_wishlist_link(self) -> Locator:
        return self.page.locator(".nav-menu-desktop a[aria-label='Wishlist']")

    @property
    def desktop_cart_link(self) -> Locator:
        return self.page.locator(".nav-menu-desktop a[href$='/cart/']")

    @property
    def desktop_contact_link(self) -> Locator:
        return self.page.locator(".nav-menu-desktop a[aria-label='Contact Us']")

    @property
    def collections_dropdown_trigger(self) -> Locator:
        return self.page.locator(
            ".nav-menu-desktop button.nav-link:has-text('Collections'), "
            ".nav-menu-desktop button.nav-link:has-text('Collection')"
        )

    @property
    def collections_dropdown_menu(self) -> Locator:
        return self.page.locator(".nav-menu-desktop ul.nav-dropdown")

    @property
    def language_button(self) -> Locator:
        return self.page.locator(".nav-menu-desktop .lang-btn")

    # Mobile nav triggers/links
    @property
    def mobile_menu_button(self) -> Locator:
        return self.page.locator("#mobile-menu-button")

    @property
    def mobile_menu(self) -> Locator:
        return self.page.locator("#mobile-menu")

    # Toast elements
    @property
    def toast_messages(self) -> Locator:
        return self.page.locator(".toast-message")

    @property
    def success_toasts(self) -> Locator:
        return self.page.locator(".toast-message.success")

    @property
    def error_toasts(self) -> Locator:
        return self.page.locator(".toast-message.error, .toast-message.danger")

    # Common Actions
    async def click_logo(self) -> None:
        await self.logo_link.click()

    async def click_about(self) -> None:
        await self.desktop_about_link.click()

    async def click_account(self) -> None:
        await self.desktop_account_link.click()

    async def click_login(self) -> None:
        await self.desktop_login_link.click()

    async def click_register(self) -> None:
        await self.desktop_register_link.click()

    async def click_wishlist(self) -> None:
        await self.desktop_wishlist_link.click()

    async def click_cart(self) -> None:
        await self.desktop_cart_link.click()

    async def click_contact(self) -> None:
        await self.desktop_contact_link.click()

    async def select_collection_from_dropdown(self, collection_name: str) -> None:
        """Hover over Collections dropdown and select a collection."""
        await self.collections_dropdown_trigger.hover()
        await self.collections_dropdown_menu.locator(
            f"a:has-text('{collection_name}')"
        ).click()

    async def change_language(self, lang_code: str) -> None:
        """Changes the language via desktop dropdown (en, es, fr)."""
        await self.language_button.hover()
        lang_btn = self.page.locator(
            f".nav-menu-desktop form:has(input[name='language'][value='{lang_code}']) "
            "button[type='submit']"
        )
        await lang_btn.click()

    async def toggle_mobile_menu(self) -> None:
        await self.mobile_menu_button.click()

    async def get_toast_texts(self) -> list[str]:
        return await self.toast_messages.all_inner_texts()
