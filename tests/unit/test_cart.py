import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from django.test import Client, RequestFactory
from django.core.exceptions import ValidationError
from account.models import Account
from shop.models import Product
from cart.models import Cart, CartItem, Order, OrderItem
from typing import Callable


def test_cart_operations(
    test_cart: Cart, create_product: Callable[..., Product]
) -> None:
    """Test cart addition, replacement, removal, and clearing."""
    p1 = create_product(name="Mug", price_in_cents=1500)
    p2 = create_product(name="Plate", price_in_cents=2500)

    assert test_cart.count() == 0

    test_cart.add(p1, quantity=2)
    test_cart.add(p2, quantity=1)

    assert test_cart.count() == 3
    assert CartItem.objects.filter(cart=test_cart).count() == 2

    # Test replace quantity
    test_cart.add(p1, quantity=5, replace=True)
    item = CartItem.objects.get(cart=test_cart, product=p1)
    assert item.quantity == 5
    assert test_cart.count() == 6

    # Test remove item
    test_cart.remove(p1)
    assert test_cart.count() == 1
    assert not CartItem.objects.filter(cart=test_cart, product=p1).exists()

    # Test clear cart
    test_cart.add(p1, quantity=2)
    test_cart.clear()
    assert test_cart.count() == 0


def test_cart_subtotals(
    test_cart: Cart, create_product: Callable[..., Product]
) -> None:
    """Test subtotals calculation in cents and formatted dollar string."""
    p1 = create_product(name="Mug", price_in_cents=1500)
    p2 = create_product(name="Plate", price_in_cents=2500)

    test_cart.add(p1, quantity=2)
    test_cart.add(p2, quantity=1)

    assert test_cart.subtotal_cents() == 5500
    assert test_cart.subtotal_dollars() == "$55.00"
    assert test_cart.account.email in str(test_cart)


def test_cart_item_totals_and_discount(
    test_cart: Cart, create_product: Callable[..., Product]
) -> None:
    """Test unit/total prices on CartItem, with and without discount."""
    p1 = create_product(name="Mug", price_in_cents=1500)
    item = CartItem.objects.create(cart=test_cart, product=p1, quantity=3)

    assert item.unit_cents == 1500
    assert item.total_cents == 4500
    assert item.unit_dollars == "$15.00"
    assert item.line_dollars == "$45.00"
    assert p1.name in str(item)

    # Test with discount
    p2 = create_product(name="Plate", price_in_cents=2500, discount_percentage=10)
    item2 = CartItem.objects.create(cart=test_cart, product=p2, quantity=2)
    assert item2.unit_cents == 2250
    assert item2.total_cents == 4500
    assert item2.unit_dollars == "$22.50"
    assert item2.line_dollars == "$45.00"


def test_unique_product_per_cart_constraint(
    test_cart: Cart, test_product: Product
) -> None:
    """Test unique database constraint of product per cart."""
    from django.db import IntegrityError

    CartItem.objects.create(cart=test_cart, product=test_product, quantity=1)
    with pytest.raises(IntegrityError):
        CartItem.objects.create(cart=test_cart, product=test_product, quantity=2)


def test_order_status_valid_and_invalid(test_order: Order) -> None:
    """Test changing status and validation on Order."""
    test_order.set_status("paid")
    assert test_order.status == Order.STATUS_PAID

    with pytest.raises(ValueError):
        test_order.set_status("invalid-status")


def test_order_total_dollars(test_order: Order) -> None:
    """Test dollar formatting of order total."""
    test_order.total_cents = 1234
    test_order.save()
    assert test_order.total_in_dollars == "$12.34"
    assert (
        str(test_order)
        == f"Order #{test_order.payment_id} - {test_order.account.email}"
    )


def test_set_status_paid_decrements_inventory(
    test_user: Account,
    create_product: Callable[..., Product],
    create_order: Callable[..., Order],
) -> None:
    """Test order payment decrements product quantity, or raises error if insufficient."""
    product = create_product(quantity=5, price_in_cents=1500)
    order = create_order(user=test_user, total_cents=3000)
    OrderItem.objects.create(
        order=order, product=product, quantity=2, unit_price_cents=1500
    )

    order.set_status("paid")
    product.refresh_from_db()
    assert product.quantity == 3

    # Test error if quantity exceeds stock
    order2 = create_order(user=test_user, total_cents=15000)
    OrderItem.objects.create(
        order=order2, product=product, quantity=10, unit_price_cents=1500
    )
    with pytest.raises(ValidationError):
        order2.set_status("paid")


def test_order_fulfill(test_user: Account, create_order: Callable[..., Order]) -> None:
    """Test order fulfillment loads addresses from account or kwargs."""
    test_user.first_name = "Juan"
    test_user.last_name = "Acosta"
    test_user.billing_city = "Montreal"
    test_user.shipping_city = "Montreal"
    test_user.save()

    order = create_order(user=test_user)
    order.fulfill(payment_id="pi_123")
    assert order.payment_id == "pi_123"
    assert order.name == "Juan Acosta"
    assert order.billing_city == "Montreal"

    # Test override
    order.fulfill(payment_id="pi_456", billing_city="Ottawa")
    assert order.payment_id == "pi_456"
    assert order.billing_city == "Ottawa"


@patch("cart.models.stripe.checkout.Session.create")
def test_create_order_from_cart(
    mock_stripe_create: MagicMock,
    test_user: Account,
    test_cart: Cart,
    create_product: Callable[..., Product],
) -> None:
    """Test creating an order from a shopping cart."""
    rf = RequestFactory()
    request = rf.post(reverse("cart:create_checkout_session"))
    request.user = test_user

    # Empty cart returns None
    session, order = Order.create_from_cart(request, test_cart, test_user)
    assert session is None
    assert order is None

    # Populate cart
    p = create_product(price_in_cents=1500)
    test_cart.add(p, quantity=2)

    mock_session = MagicMock()
    mock_session.id = "cs_test_123"
    mock_session.payment_intent = "pi_test_123"
    mock_stripe_create.return_value = mock_session

    session, order = Order.create_from_cart(request, test_cart, test_user)
    assert session is not None
    assert order is not None
    assert order.total_cents == 3000
    assert order.payment_id == "pi_test_123"
    assert order.items.count() == 1
    assert mock_stripe_create.called


def test_cart_view_protection_requires_login(
    client: Client, test_product: Product
) -> None:
    """Test that cart operations require login."""
    url_update = reverse("cart:update_cart_checkout", args=[test_product.id])
    response = client.post(url_update, {"quantity": 2})
    assert response.status_code == 302
    assert "login" in response.url

    url_remove = reverse("cart:remove_from_cart_checkout", args=[test_product.id])
    response2 = client.post(url_remove)
    assert response2.status_code == 302
    assert "login" in response2.url


def test_cart_view_success_clears_cart(
    client: Client, test_user: Account, test_cart: Cart, test_product: Product
) -> None:
    """Test cart details update and cart clear on successful checkout payment."""
    test_cart.add(test_product, quantity=2)
    assert test_cart.count() == 2

    client.force_login(test_user)
    url_success = reverse("cart:success") + "?session_id=cs_test_123"

    with patch("cart.views.stripe.checkout.Session.retrieve") as mock_retrieve:
        mock_session = MagicMock()
        mock_session.payment_status = "paid"
        mock_retrieve.return_value = mock_session

        response = client.get(url_success)
        assert response.status_code == 200
        assert test_cart.count() == 0


@patch("cart.webhooks.stripe.Webhook.construct_event")
def test_stripe_webhook_completed(
    mock_construct: MagicMock,
    client: Client,
    test_user: Account,
    create_order: Callable[..., Order],
) -> None:
    """Test stripe webhook processing for checkout completed."""
    import os

    old_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    os.environ["STRIPE_WEBHOOK_SECRET"] = "test_webhook_secret"

    order = create_order(user=test_user, total_cents=3000, payment_id="pi_test_123")
    mock_construct.return_value = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "client_reference_id": str(order.id),
                "payment_intent": "pi_test_123",
                "id": "cs_test_123",
            }
        },
    }

    response = client.post(
        reverse("cart:stripe_webhook"),
        data="dummy payload",
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="dummy signature",
    )
    assert response.status_code == 200
    order.refresh_from_db()
    assert order.status == Order.STATUS_PAID

    if old_secret:
        os.environ["STRIPE_WEBHOOK_SECRET"] = old_secret
    else:
        del os.environ["STRIPE_WEBHOOK_SECRET"]


def test_order_details_view_permissions(
    client: Client, test_user: Account, create_order: Callable[..., Order]
) -> None:
    """Test that only the owner of the order can view details."""
    order = create_order(user=test_user)

    client.force_login(test_user)
    response = client.get(reverse("cart:order_details", args=[order.id]))
    assert response.status_code == 200

    other_user = Account.objects.create_user(
        username="other", email="other@ex.com", password="password"
    )
    client.force_login(other_user)
    response2 = client.get(reverse("cart:order_details", args=[order.id]))
    assert response2.status_code == 404
