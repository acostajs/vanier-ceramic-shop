import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model
from account.models import Account, Wishlist
from shop.models import Product
from cart.models import Order
from typing import Callable

User = get_user_model()


@pytest.mark.django_db
def test_shipping_page_get(auth_client: Client, test_user: Account) -> None:
    """Test retrieving the shipping information page when authenticated."""
    response = auth_client.get(reverse("account:shipping"))
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["account"] == test_user


@pytest.mark.django_db
def test_shipping_submit_valid(auth_client: Client, test_user: Account) -> None:
    """Test successfully updating shipping information."""
    payload = {
        "shipping_address_line1": "100 Pine St",
        "shipping_address_line2": "Apt 4B",
        "shipping_city": "Vancouver",
        "shipping_postal_code": "V6B 1A1",
        "shipping_country": "Canada",
    }
    response = auth_client.post(reverse("account:shipping_submit"), data=payload)
    assert response.status_code == 302
    assert response.url == reverse("account:account")

    test_user.refresh_from_db()
    assert test_user.shipping_address_line1 == "100 Pine St"
    assert test_user.shipping_address_line2 == "Apt 4B"
    assert test_user.shipping_city == "Vancouver"
    assert test_user.shipping_postal_code == "V6B 1A1"
    assert test_user.shipping_country == "Canada"


@pytest.mark.django_db
def test_shipping_submit_invalid(auth_client: Client, test_user: Account) -> None:
    """Test updating shipping information with invalid data (e.g. too long postal code)."""
    payload = {
        "shipping_address_line1": "100 Pine St",
        "shipping_postal_code": "A" * 50,  # Max length on model is 20
        "shipping_country": "Canada",
    }
    response = auth_client.post(reverse("account:shipping_submit"), data=payload)
    assert response.status_code == 200
    assert "form" in response.context
    assert not response.context["form"].is_valid()
    assert "shipping_postal_code" in response.context["form"].errors


@pytest.mark.django_db
def test_billing_page_get(auth_client: Client, test_user: Account) -> None:
    """Test retrieving the billing information page when authenticated."""
    response = auth_client.get(reverse("account:billing"))
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["account"] == test_user


@pytest.mark.django_db
def test_billing_submit_valid(auth_client: Client, test_user: Account) -> None:
    """Test successfully updating billing information."""
    payload = {
        "billing_address_line1": "200 Maple Ave",
        "billing_address_line2": "Suite 10",
        "billing_city": "Toronto",
        "billing_postal_code": "M5V 2N2",
        "billing_country": "Canada",
    }
    response = auth_client.post(reverse("account:billing_submit"), data=payload)
    assert response.status_code == 302
    assert response.url == reverse("account:account")

    test_user.refresh_from_db()
    assert test_user.billing_address_line1 == "200 Maple Ave"
    assert test_user.billing_address_line2 == "Suite 10"
    assert test_user.billing_city == "Toronto"
    assert test_user.billing_postal_code == "M5V 2N2"
    assert test_user.billing_country == "Canada"


@pytest.mark.django_db
def test_billing_submit_invalid(auth_client: Client, test_user: Account) -> None:
    """Test updating billing information with invalid data (e.g. too long postal code)."""
    payload = {
        "billing_address_line1": "200 Maple Ave",
        "billing_postal_code": "B" * 50,  # Max length on model is 20
        "billing_country": "Canada",
    }
    response = auth_client.post(reverse("account:billing_submit"), data=payload)
    assert response.status_code == 200
    assert "form" in response.context
    assert not response.context["form"].is_valid()
    assert "billing_postal_code" in response.context["form"].errors


@pytest.mark.django_db
def test_wishlist_add_valid(auth_client: Client, test_product: Product) -> None:
    """Test adding an existing product to the wishlist."""
    response = auth_client.post(
        reverse("account:add_to_wishlist", args=[test_product.id])
    )
    assert response.status_code == 302
    assert response.url == reverse("shop:product", args=[test_product.id])

    wishlist = Wishlist.objects.get(account__username="testuser")
    assert test_product in wishlist.product.all()


@pytest.mark.django_db
def test_wishlist_add_invalid(auth_client: Client) -> None:
    """Test adding a non-existent product to the wishlist returns 404."""
    response = auth_client.post(reverse("account:add_to_wishlist", args=[999999]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_wishlist_remove_valid(
    auth_client: Client, test_wishlist: Wishlist, test_product: Product
) -> None:
    """Test removing a product from the wishlist."""
    test_wishlist.add(test_product)
    assert test_product in test_wishlist.product.all()

    response = auth_client.post(
        reverse("account:remove_from_wishlist", args=[test_product.id])
    )
    assert response.status_code == 302
    assert response.url == reverse("account:wishlist_detail")

    assert test_product not in test_wishlist.product.all()


@pytest.mark.django_db
def test_wishlist_remove_invalid(auth_client: Client) -> None:
    """Test removing a non-existent product from the wishlist returns 404."""
    response = auth_client.post(reverse("account:remove_from_wishlist", args=[999999]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_wishlist_clear(
    auth_client: Client, test_wishlist: Wishlist, create_product: Callable[..., Product]
) -> None:
    """Test clearing all products from the wishlist."""
    p1 = create_product(name="P1")
    p2 = create_product(name="P2")
    test_wishlist.add(p1)
    test_wishlist.add(p2)
    assert test_wishlist.count() == 2

    response = auth_client.post(reverse("account:clear_wishlist"))
    assert response.status_code == 302
    assert response.url == reverse("account:wishlist_detail")

    assert test_wishlist.count() == 0


@pytest.mark.django_db
def test_order_history_view(
    auth_client: Client, test_user: Account, create_order: Callable[..., Order]
) -> None:
    """Test that order history is displayed in the user profile page."""
    # Create two orders for the test user
    o1 = create_order(user=test_user, total_cents=10000, status=Order.STATUS_PAID)
    o2 = create_order(user=test_user, total_cents=5000, status=Order.STATUS_PENDING)

    response = auth_client.get(reverse("account:account"))
    assert response.status_code == 200
    assert "orders" in response.context
    orders_in_context = list(response.context["orders"])
    assert len(orders_in_context) == 2
    # Should be sorted by created_at descending (newer order first)
    assert o2 in orders_in_context
    assert o1 in orders_in_context


@pytest.mark.django_db
def test_registration_page_get(client: Client) -> None:
    """Test retrieving the registration page (GET)."""
    response = client.get(reverse("account:registration"))
    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_login_page_get(client: Client) -> None:
    """Test retrieving the login page (GET)."""
    response = client.get(reverse("account:login"))
    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_registration_submit_success(client: Client) -> None:
    """Test successful user registration submission."""
    User.objects.filter(username="newregistereduser").delete()

    payload = {
        "username": "newregistereduser",
        "first_name": "New",
        "last_name": "User",
        "email": "newuser@example.com",
        "password1": "password123!",
        "password2": "password123!",
    }
    response = client.post(reverse("account:registration_submit"), data=payload)
    assert response.status_code == 302
    assert response.url == reverse("account:login")
    assert User.objects.filter(username="newregistereduser").exists()


@pytest.mark.django_db
def test_login_submit_success(
    client: Client, create_user: Callable[..., Account]
) -> None:
    """Test successful login form submission."""
    username = "loginuser"
    password = "correctpassword123"
    create_user(username=username, password=password)

    payload = {
        "username": username,
        "password": password,
    }
    response = client.post(reverse("account:login_submit"), data=payload)
    assert response.status_code == 302
    assert response.url == reverse("account:account")
