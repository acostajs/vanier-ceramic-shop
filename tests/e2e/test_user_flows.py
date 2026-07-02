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
from tests.e2e.pages.wishlist import WishlistPage
from typing import Callable
from pytest_django.live_server_helper import LiveServer
from account.models import Account
from shop.models import Collection, Product


@pytest.mark.asyncio
async def test_user_registration_and_login(
    async_page: Page, live_server: LiveServer
) -> None:
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
    live_server: LiveServer,
    test_collection: Collection,
    test_product: Product,
    create_user: Callable[..., Account],
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
async def test_contact_form_submission(
    async_page: Page, live_server: LiveServer
) -> None:
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


@pytest.mark.asyncio
async def test_wishlist_flow(
    async_page: Page,
    live_server: LiveServer,
    test_collection: Collection,
    test_product: Product,
    create_user: Callable[..., Account],
) -> None:
    """Test login, adding to wishlist, verifying on wishlist page, and removing."""
    # 1. Create a shopper user
    create_user(username="wishlist_shopper", password="shopperpassword123")

    # 2. Initialize Page Objects
    login_page = LoginPage(async_page)
    product_page = ProductDetailPage(async_page)
    wishlist_page = WishlistPage(async_page)

    # 3. Log in
    await login_page.navigate_to(f"{live_server.url}/account/login/")
    await login_page.login(username="wishlist_shopper", password="shopperpassword123")
    await async_page.wait_for_url("**/account/")

    # 4. Navigate to product detail page
    await product_page.navigate_to(f"{live_server.url}/shop/product/{test_product.id}/")
    await async_page.wait_for_url(f"**/shop/product/{test_product.id}/")

    # 5. Add product to wishlist
    await product_page.add_to_wishlist()
    # Wait for wishlist redirect/render to complete (it redirects back to the product details page)
    await async_page.wait_for_url(f"**/shop/product/{test_product.id}/")

    # 6. Navigate to wishlist page
    await product_page.click_wishlist()
    await async_page.wait_for_url("**/account/wishlist/")

    # 7. Verify the product is visible in the wishlist
    product_row = await wishlist_page.get_row_by_product_name(test_product.name)
    assert await product_row.is_visible()

    # 8. Remove product from wishlist
    await wishlist_page.remove_product(test_product.name)
    await async_page.wait_for_url("**/account/wishlist/")

    # 9. Verify the wishlist is empty
    assert await wishlist_page.empty_wishlist_message.is_visible()


@pytest.mark.asyncio
async def test_long_user_flow_with_video(
    live_server: LiveServer,
    test_collection: Collection,
    test_product: Product,
    create_user: Callable[..., Account],
) -> None:
    """Test long user flow and record a webm video of it with 1s pause between steps."""
    import asyncio
    import os
    from playwright.async_api import async_playwright

    # 1. Create a shopper user
    create_user(username="video_shopper", password="shopperpassword123")

    # 2. Start Playwright and configure video recording
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        video_dir = os.path.join(os.path.dirname(__file__), "videos")
        os.makedirs(video_dir, exist_ok=True)

        context = await browser.new_context(
            record_video_dir=video_dir,
            record_video_size={"width": 1280, "height": 720},
        )
        page = await context.new_page()

        try:
            # 3. Initialize Page Objects with the custom page
            login_page = LoginPage(page)
            home_page = HomePage(page)
            shop_page = ShopPage(page)
            collection_page = CollectionPage(page)
            product_page = ProductDetailPage(page)
            cart_page = CartPage(page)
            checkout_page = CheckoutPage(page)
            contact_page = ContactPage(page)
            wishlist_page = WishlistPage(page)
            account_page = AccountPage(page)

            await asyncio.sleep(1.0)

            # 4. Navigate to login page
            await login_page.navigate_to(f"{live_server.url}/account/login/")
            await asyncio.sleep(1.0)

            # 5. Log in
            await login_page.login(
                username="video_shopper", password="shopperpassword123"
            )
            await page.wait_for_url("**/account/")
            await asyncio.sleep(1.0)

            # 6. Navigate to Home
            await page.goto(f"{live_server.url}/")
            await asyncio.sleep(1.0)

            # 7. Go to Shop page
            await home_page.click_shop_collections()
            await page.wait_for_url("**/shop/")
            await asyncio.sleep(1.0)

            # 8. Open collection
            await shop_page.click_collection_by_name("Stoneware Collection")
            await page.wait_for_url("**/shop/collection/*/")
            await asyncio.sleep(1.0)

            # 9. View product detail
            await collection_page.click_product_details_by_name("Artisanal Vase")
            await page.wait_for_url("**/shop/product/*/")
            await asyncio.sleep(1.0)

            # 10. Add to wishlist
            await product_page.add_to_wishlist()
            await page.wait_for_url(f"**/shop/product/{test_product.id}/")
            await asyncio.sleep(1.0)

            # 11. Navigate to wishlist
            await product_page.click_wishlist()
            await page.wait_for_url("**/account/wishlist/")
            await asyncio.sleep(1.0)

            # 12. Verify in wishlist and remove
            product_row = await wishlist_page.get_row_by_product_name(test_product.name)
            assert await product_row.is_visible()
            await wishlist_page.remove_product(test_product.name)
            await page.wait_for_url("**/account/wishlist/")
            await asyncio.sleep(1.0)

            # 13. Back to product page
            await page.goto(f"{live_server.url}/shop/product/{test_product.id}/")
            await page.wait_for_url(f"**/shop/product/{test_product.id}/")
            await asyncio.sleep(1.0)

            # 14. Add to cart
            await product_page.add_to_cart(quantity=3)
            await page.wait_for_url("**/shop/product/*/")
            await asyncio.sleep(1.0)

            # 15. View cart
            await product_page.click_cart()
            await page.wait_for_url("**/cart/")
            await asyncio.sleep(1.0)

            # 16. Update quantity in cart
            await cart_page.update_quantity("Artisanal Vase", 2)
            await asyncio.sleep(1.0)

            # 17. Go to checkout
            await cart_page.click_checkout()
            await page.wait_for_url("**/cart/checkout/")
            await asyncio.sleep(1.0)

            # 18. Verify checkout total and proceed button
            assert await checkout_page.proceed_to_payment_button.is_visible()
            await asyncio.sleep(1.0)

            # 19. Contact page
            await page.goto(f"{live_server.url}/contact/")
            await page.wait_for_url("**/contact/")
            await asyncio.sleep(1.0)

            # 20. Submit message
            await contact_page.submit_message(
                name="Video Shopper",
                email="video_shopper@example.com",
                subject="Test Feedback",
                message="This is a test message to record the full flow.",
            )
            await page.wait_for_selector(".home-hero")
            await asyncio.sleep(1.0)

            # 21. Log out
            await page.goto(f"{live_server.url}/account/")
            await page.wait_for_url("**/account/")
            await asyncio.sleep(1.0)

            await account_page.logout()
            await page.wait_for_url("**/account/login/")
            await asyncio.sleep(1.0)

        finally:
            await context.close()
            await browser.close()
