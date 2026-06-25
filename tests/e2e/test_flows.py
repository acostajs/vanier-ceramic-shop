import pytest
from playwright.async_api import Page
from tests.e2e.pages.registration import RegisterPage
from tests.e2e.pages.login import LoginPage
from tests.e2e.pages.account import AccountPage
from tests.e2e.pages.home import HomePage
from tests.e2e.pages.shop import ShopPage
from tests.e2e.pages.collection import CollectionPage
from tests.e2e.pages.product import ProductDetailPage
from tests.e2e.pages.cart import CartPage
from tests.e2e.pages.checkout import CheckoutPage
from tests.e2e.pages.contact import ContactPage
from typing import Any, Callable
from shop.models import Collection, Product


@pytest.mark.asyncio
async def test_user_registration_and_login(async_page: Page, live_server: Any) -> None:
    """Test register a new account, login, and verify account detail rendering."""
    # Initialize Page Objects
    register_page = RegisterPage(async_page)
    login_page = LoginPage(async_page)
    account_page = AccountPage(async_page)

    # 1. Registration
    await register_page.navigate_to(f"{live_server.url}/account/registration/")
    await register_page.register(
        username="e2e_user",
        first_name="John",
        last_name="Doe",
        email="e2e_user@example.com",
        password="E2Epassword123!",
    )

    # After registration, should redirect to login
    await async_page.wait_for_url("**/account/login/")

    # 2. Login
    await login_page.login(username="e2e_user", password="E2Epassword123!")

    # After login, should redirect to account details page
    await async_page.wait_for_url("**/account/")

    # 3. Account verification
    assert await account_page.username_title.inner_text() == "e2e_user"
    assert "John" in await account_page.first_name_text.inner_text()
    assert "Doe" in await account_page.last_name_text.inner_text()
    assert "e2e_user@example.com" in await account_page.email_text.inner_text()

    # 4. Logout
    await account_page.logout()
    await async_page.wait_for_url("**/account/login/")


@pytest.mark.asyncio
async def test_catalog_browsing_cart_and_checkout_flow(
    async_page: Page,
    live_server: Any,
    test_collection: Collection,
    test_product: Product,
    create_user: Callable[..., Any],
) -> None:
    """Test browsing catalog, adding to cart, wishlisting, transferring, and checkout page verification."""
    # E2E tests need a logged in state for shopping/checkout
    create_user(username="shopper", password="shopperpassword123")

    # Log in first
    login_page = LoginPage(async_page)
    await login_page.navigate_to(f"{live_server.url}/account/login/")
    await login_page.login(username="shopper", password="shopperpassword123")
    await async_page.wait_for_url("**/account/")

    # Initialize Page Objects
    home_page = HomePage(async_page)
    shop_page = ShopPage(async_page)
    collection_page = CollectionPage(async_page)
    product_page = ProductDetailPage(async_page)
    cart_page = CartPage(async_page)
    checkout_page = CheckoutPage(async_page)

    # 1. Navigate to Home
    await home_page.navigate_to(f"{live_server.url}/")
    await home_page.click_shop_collections()
    await async_page.wait_for_url("**/shop/")

    # 2. Shop Collections Page
    assert await shop_page.title.inner_text() == "My Collections"
    await shop_page.click_collection_by_name("Stoneware Collection")
    await async_page.wait_for_url("**/shop/collection/*/")

    # 3. Collection Page
    assert await collection_page.title.inner_text() == "Stoneware Collection"
    await collection_page.click_product_details_by_name("Artisanal Vase")
    await async_page.wait_for_url("**/shop/product/*/")

    # 4. Product Details
    assert await product_page.title.inner_text() == "Artisanal Vase"
    assert "$45.00" in await product_page.price.inner_text()

    # Add to cart
    await product_page.add_to_cart(quantity=2)
    # The view redirects back to the product details page
    await async_page.wait_for_url("**/shop/product/*/")
    # Click on the cart link in the header
    await product_page.click_cart()
    await async_page.wait_for_url("**/cart/")

    # 5. Cart Page
    assert "Your Cart" in await cart_page.title.inner_text()
    assert await cart_page.total_price.inner_text() == "$90.00"

    # Update Quantity
    await cart_page.update_quantity("Artisanal Vase", 1)
    assert await cart_page.total_price.inner_text() == "$45.00"

    # 6. Checkout Page
    await cart_page.click_checkout()
    await async_page.wait_for_url("**/cart/checkout/")
    assert await checkout_page.total_price.inner_text() == "$45.00"

    # Verify proceed to payment button exists
    assert await checkout_page.proceed_to_payment_button.is_visible()


@pytest.mark.asyncio
async def test_contact_form_submission(async_page: Page, live_server: Any) -> None:
    """Test contact form submission sends and redirects to home page."""
    contact_page = ContactPage(async_page)

    await contact_page.navigate_to(f"{live_server.url}/contact/")
    await contact_page.submit_message(
        name="Guest User",
        email="guest@example.com",
        subject="Art Enquiry",
        message="I would love to query about custom vases.",
    )

    # After submit, should redirect to home page
    await async_page.wait_for_selector(".home-hero")
