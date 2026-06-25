import pytest
from playwright.async_api import Page
from pytest_django.live_server_helper import LiveServer
from shop.models import Collection, Product


@pytest.mark.asyncio
async def test_smoke_home_page(async_page: Page, live_server: LiveServer) -> None:
    """Smoke test to verify that the home page loads correctly."""
    await async_page.goto(f"{live_server.url}/")
    # Verify we can find the hero section
    await async_page.wait_for_selector(".home-hero")
    assert await async_page.title() != ""


@pytest.mark.asyncio
async def test_smoke_shop_page(async_page: Page, live_server: LiveServer) -> None:
    """Smoke test to verify that the shop page loads correctly."""
    await async_page.goto(f"{live_server.url}/shop/")
    # Verify the shop title exists
    title_element = async_page.locator(".shop-hero-title")
    await title_element.wait_for()
    assert await title_element.inner_text() == "My Collections"


@pytest.mark.asyncio
async def test_smoke_collection_page(
    async_page: Page, live_server: LiveServer, test_collection: Collection
) -> None:
    """Smoke test to verify that a collection detail page loads correctly."""
    await async_page.goto(f"{live_server.url}/shop/collection/{test_collection.id}/")
    title_element = async_page.locator(".collection-banner-title")
    await title_element.wait_for()
    assert await title_element.inner_text() == test_collection.name


@pytest.mark.asyncio
async def test_smoke_product_page(
    async_page: Page, live_server: LiveServer, test_product: Product
) -> None:
    """Smoke test to verify that a product detail page loads correctly."""
    await async_page.goto(f"{live_server.url}/shop/product/{test_product.id}/")
    title_element = async_page.locator(".product-detail-title")
    await title_element.wait_for()
    assert await title_element.inner_text() == test_product.name


@pytest.mark.asyncio
async def test_smoke_contact_page(async_page: Page, live_server: LiveServer) -> None:
    """Smoke test to verify that the contact page loads correctly."""
    await async_page.goto(f"{live_server.url}/contact/")
    # Check that contact form elements exist
    await async_page.wait_for_selector(".contact-submit-btn")
    assert "Contact" in await async_page.content()


@pytest.mark.asyncio
async def test_smoke_login_page(async_page: Page, live_server: LiveServer) -> None:
    """Smoke test to verify that the login page loads correctly."""
    await async_page.goto(f"{live_server.url}/account/login/")
    await async_page.wait_for_selector("input[name='username']")
    await async_page.wait_for_selector("input[name='password']")


@pytest.mark.asyncio
async def test_smoke_registration_page(
    async_page: Page, live_server: LiveServer
) -> None:
    """Smoke test to verify that the registration page loads correctly."""
    await async_page.goto(f"{live_server.url}/account/registration/")
    await async_page.wait_for_selector("input[name='username']")
    await async_page.wait_for_selector("input[name='email']")
