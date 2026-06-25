import os
import pytest
from typing import Callable, Any, Coroutine, AsyncGenerator
from django.contrib.auth import get_user_model
from account.models import Account, Wishlist
from shop.models import Collection, Product
from cart.models import Cart, Order
from playwright.async_api import Page, async_playwright
import pytest_asyncio

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
User = get_user_model()


@pytest.fixture(scope="session")
def event_loop() -> Any:
    """Create an instance of the default event loop for the test session."""
    import asyncio

    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_page() -> AsyncGenerator[Page, None]:
    """Async Playwright Page fixture to avoid event loop conflicts in async E2E tests."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        yield page
        await context.close()
        await browser.close()


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db: Any) -> None:
    """Fixture to ensure database access is enabled for all tests."""
    pass


@pytest.fixture
def create_user() -> Callable[..., Account]:
    """Fixture returning a function to create a new Account user."""

    def _create_user(
        username: str = "testuser",
        email: str = "testuser@example.com",
        password: str = "password123",
        **kwargs: Any,
    ) -> Account:
        user = User.objects.create_user(
            username=username, email=email, password=password, **kwargs
        )
        # Create corresponding Wishlist and Cart
        Wishlist.objects.get_or_create(account=user)
        Cart.objects.get_or_create(account=user)
        return user

    return _create_user


@pytest.fixture
def test_user(create_user: Callable[..., Account]) -> Account:
    """Fixture providing a default test user."""
    return create_user()


@pytest.fixture
def create_collection() -> Callable[..., Collection]:
    """Fixture returning a function to create a Collection."""

    def _create_collection(
        name: str = "Stoneware Collection",
        description: str = "Handcrafted stoneware pieces.",
        ceramic_type: str = "Stoneware",
        year: int = 2026,
        **kwargs: Any,
    ) -> Collection:
        from django.core.files.uploadedfile import SimpleUploadedFile

        image = SimpleUploadedFile(
            name="test_collection.jpg", content=b"", content_type="image/jpeg"
        )
        return Collection.objects.create(
            name=name,
            description=description,
            image=image,
            ceramic_type=ceramic_type,
            year=year,
            **kwargs,
        )

    return _create_collection


@pytest.fixture
def test_collection(create_collection: Callable[..., Collection]) -> Collection:
    """Fixture providing a default collection."""
    return create_collection()


@pytest.fixture
def create_product(test_collection: Collection) -> Callable[..., Product]:
    """Fixture returning a function to create a Product."""

    def _create_product(
        name: str = "Artisanal Vase",
        description: str = "A beautiful hand-thrown ceramic vase.",
        quantity: int = 5,
        price_in_cents: int = 4500,
        discount_percentage: int = 0,
        **kwargs: Any,
    ) -> Product:
        from django.core.files.uploadedfile import SimpleUploadedFile

        image = SimpleUploadedFile(
            name="test_product.jpg", content=b"", content_type="image/jpeg"
        )
        return Product.objects.create(
            name=name,
            description=description,
            quantity=quantity,
            image=image,
            price_in_cents=price_in_cents,
            collection=test_collection,
            discount_percentage=discount_percentage,
            **kwargs,
        )

    return _create_product


@pytest.fixture
def test_product(create_product: Callable[..., Product]) -> Product:
    """Fixture providing a default product."""
    return create_product()


@pytest.fixture
def test_cart(test_user: Account) -> Cart:
    """Fixture providing the cart for the default test user."""
    cart, _ = Cart.objects.get_or_create(account=test_user)
    return cart


@pytest.fixture
def test_wishlist(test_user: Account) -> Wishlist:
    """Fixture providing the wishlist for the default test user."""
    wishlist, _ = Wishlist.objects.get_or_create(account=test_user)
    return wishlist


@pytest.fixture
def create_order() -> Callable[..., Order]:
    """Fixture returning a function to create an Order."""

    def _create_order(
        user: Account,
        total_cents: int = 4500,
        status: str = Order.STATUS_PENDING,
        **kwargs: Any,
    ) -> Order:
        return Order.objects.create(
            account=user, total_cents=total_cents, status=status, **kwargs
        )

    return _create_order


@pytest.fixture
def test_order(test_user: Account, create_order: Callable[..., Order]) -> Order:
    """Fixture providing a default pending order."""
    return create_order(user=test_user)


@pytest.fixture
def login_user_helper() -> Callable[[Page, str, str, Any], Coroutine[Any, Any, None]]:
    """Helper fixture to log in a user using Playwright E2E UI login."""

    async def _login(
        page: Page, username: str, password: str, live_server: Any
    ) -> None:
        await page.goto(f"{live_server.url}/account/login/")
        await page.fill("#id_username", username)
        await page.fill("#id_password", password)
        await page.click("button[type='submit']:has-text('Log In')")

    return _login
