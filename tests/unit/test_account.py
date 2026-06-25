import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model
from account.models import Account, Wishlist
from shop.models import Product
from cart.models import Cart
from typing import Callable

User = get_user_model()


def test_create_account_with_extra_fields(
    create_user: Callable[..., Account],
) -> None:
    """Test creating account with shipping/billing details."""
    account = create_user(
        username="juan",
        email="juan@example.com",
        billing_address_line1="123 Billing St",
        billing_city="Montreal",
        billing_postal_code="H1H 1H1",
        billing_country="Canada",
        shipping_address_line1="456 Shipping Ave",
        shipping_city="Montreal",
        shipping_postal_code="H2H 2H2",
        shipping_country="Canada",
    )
    assert account.username == "juan"
    assert str(account) == "juan"
    assert account.billing_address_line1 == "123 Billing St"
    assert account.billing_city == "Montreal"
    assert account.shipping_address_line1 == "456 Shipping Ave"
    assert account.shipping_city == "Montreal"


def test_account_fields_can_be_blank(
    create_user: Callable[..., Account],
) -> None:
    """Test account shipping/billing fields default to None if not provided."""
    account = create_user(username="no_addresses", email="no@addr.com")
    assert account.billing_address_line1 is None
    assert account.shipping_address_line1 is None


def test_wishlist_operations(
    test_wishlist: Wishlist, create_product: Callable[..., Product]
) -> None:
    """Test add, remove, count, and clear methods of Wishlist."""
    p1 = create_product(name="Mug")
    p2 = create_product(name="Plate")

    assert test_wishlist.count() == 0

    test_wishlist.add(p1)
    assert test_wishlist.count() == 1
    assert p1 in test_wishlist.product.all()

    test_wishlist.add(p2)
    assert test_wishlist.count() == 2

    test_wishlist.remove(p1)
    assert test_wishlist.count() == 1
    assert p1 not in test_wishlist.product.all()
    assert p2 in test_wishlist.product.all()

    test_wishlist.clear()
    assert test_wishlist.count() == 0


def test_wishlist_one_to_one_constraint(test_user: Account) -> None:
    """Test that creating a second Wishlist for same Account raises IntegrityError."""
    from django.db import IntegrityError

    with pytest.raises(IntegrityError):
        Wishlist.objects.create(account=test_user)


def test_wishlist_context_processor_anonymous(client: Client) -> None:
    """Test wishlist context processor for unauthenticated user returns 0 count."""
    from django.contrib.auth.models import AnonymousUser
    from django.test import RequestFactory
    from account.context_processors import wishlist_info

    factory = RequestFactory()
    request = factory.get("/")
    request.user = AnonymousUser()
    context = wishlist_info(request)
    assert context["wishlist_count"] == 0


def test_wishlist_context_processor_authenticated_empty(
    client: Client, test_user: Account
) -> None:
    """Test wishlist context processor for authenticated user with empty wishlist."""
    client.force_login(test_user)
    response = client.get(reverse("home"))
    assert response.status_code == 200
    assert response.context["wishlist_count"] == 0


def test_wishlist_context_processor_authenticated_items(
    client: Client,
    test_user: Account,
    test_wishlist: Wishlist,
    test_product: Product,
) -> None:
    """Test wishlist context processor returns correct count of wishlist items."""
    test_wishlist.add(test_product)
    client.force_login(test_user)
    response = client.get(reverse("home"))
    assert response.status_code == 200
    assert response.context["wishlist_count"] == 1


def test_logout_view_methods(client: Client, test_user: Account) -> None:
    """Test LogoutView rejects GET requests and redirects successfully on POST."""
    client.force_login(test_user)
    response_get = client.get(reverse("account:logout"))
    assert response_get.status_code == 405

    response_post = client.post(reverse("account:logout"))
    assert response_post.status_code == 302
    assert "login" in response_post.url


def test_wishlist_detail_view_creates_wishlist_if_not_exists(
    client: Client, create_user: Callable[..., Account]
) -> None:
    """Test accessing wishlist details creates a wishlist if one is missing."""
    user = create_user(username="user_no_wishlist", email="nowish@ex.com")
    Wishlist.objects.filter(account=user).delete()

    client.force_login(user)
    response = client.get(reverse("account:wishlist_detail"))
    assert response.status_code == 200
    assert Wishlist.objects.filter(account=user).exists()


def test_wishlist_transfer_to_cart(
    client: Client,
    test_user: Account,
    test_wishlist: Wishlist,
    test_product: Product,
) -> None:
    """Test transferring a product from Wishlist to Cart."""
    test_wishlist.add(test_product)
    Cart.objects.filter(account=test_user).delete()

    client.force_login(test_user)
    response = client.post(reverse("account:transfer_to_cart", args=[test_product.id]))
    assert response.status_code == 302
    assert response.url == reverse("cart:cart")

    assert test_product not in test_wishlist.product.all()
    cart = Cart.objects.get(account=test_user)
    assert cart.products.filter(id=test_product.id).exists()
