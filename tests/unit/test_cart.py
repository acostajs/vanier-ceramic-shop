import os
import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from django.test import Client, RequestFactory
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.contrib.auth.models import AnonymousUser
from django.db import IntegrityError
import stripe
from account.models import Account
from shop.models import Product
from cart.models import Cart, CartItem, Order, OrderItem
from cart.context_processors import cart_info
from cart.helpers import parse_quantity, get_cart
from cart.validation import has_complete_addresses
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


def test_cart_info_anonymous(rf: RequestFactory) -> None:
    """Test cart_info context processor with an anonymous user."""
    request = rf.get("/")
    request.user = AnonymousUser()
    res = cart_info(request)
    assert res == {"cart_count": 0}


def test_cart_info_no_cart(rf: RequestFactory, test_user: Account) -> None:
    """Test cart_info context processor when the cart doesn't exist."""
    request = rf.get("/")
    request.user = test_user
    Cart.objects.filter(account=test_user).delete()
    res = cart_info(request)
    assert res == {"cart_count": 0}


def test_parse_quantity_invalid(rf: RequestFactory) -> None:
    """Test parse_quantity with invalid quantity strings and empty/missing parameters."""
    request_abc = rf.post("/", {"quantity": "abc"})
    assert parse_quantity(request_abc) == 1

    request_empty = rf.post("/", {"quantity": ""})
    assert parse_quantity(request_empty) == 1


def test_get_cart_unauthenticated(rf: RequestFactory) -> None:
    """Test get_cart raises ImproperlyConfigured for anonymous user."""
    request = rf.get("/")
    request.user = AnonymousUser()
    with pytest.raises(ImproperlyConfigured):
        get_cart(request)


def test_order_set_status_already_paid(test_order: Order) -> None:
    """Test that setting status to paid on an already paid order does nothing."""
    test_order.set_status("paid")
    assert test_order.status == Order.STATUS_PAID
    # Call again
    test_order.set_status("paid")
    assert test_order.status == Order.STATUS_PAID


def test_order_item_properties(test_order: Order, test_product: Product) -> None:
    """Test OrderItem string representation and calculation properties."""
    item = OrderItem.objects.create(
        order=test_order,
        product=test_product,
        quantity=3,
        unit_price_cents=1250,
    )
    assert str(item) == f"3x {test_product.name}"
    assert item.line_total_cents == 3750
    assert item.unit_price_dollars == 12.50
    assert item.line_total_dollars == 37.50


def test_cart_add_increment(test_cart: Cart, test_product: Product) -> None:
    """Test that adding an existing item without replace increments its quantity."""
    test_cart.add(test_product, quantity=2)
    test_cart.add(test_product, quantity=3)
    item = CartItem.objects.get(cart=test_cart, product=test_product)
    assert item.quantity == 5


def test_has_complete_addresses(test_user: Account) -> None:
    """Test validation of complete addresses on account."""
    assert not has_complete_addresses(test_user)

    test_user.billing_address_line1 = "123 Main St"
    test_user.billing_city = "Montreal"
    test_user.billing_postal_code = "H3Z 2Y7"
    test_user.billing_country = "Canada"
    test_user.shipping_address_line1 = "123 Main St"
    test_user.shipping_city = "Montreal"
    test_user.shipping_postal_code = "H3Z 2Y7"
    test_user.shipping_country = "Canada"
    test_user.save()

    assert has_complete_addresses(test_user)


def test_remove_from_cart_view(
    auth_client: Client, test_cart: Cart, test_product: Product
) -> None:
    """Test POST request to remove_from_cart view."""
    test_cart.add(test_product, quantity=2)
    url = reverse("cart:remove_from_cart", args=[test_product.id])
    response = auth_client.post(url)
    assert response.status_code == 302
    assert response.url == reverse("cart:cart")
    assert test_cart.count() == 0


def test_clear_cart_view(
    auth_client: Client, test_cart: Cart, test_product: Product
) -> None:
    """Test POST request to clear_cart view."""
    test_cart.add(test_product, quantity=2)
    url = reverse("cart:clear_cart")
    response = auth_client.post(url)
    assert response.status_code == 302
    assert response.url == reverse("cart:cart")
    assert test_cart.count() == 0


def test_update_cart_checkout_view(
    auth_client: Client, test_cart: Cart, test_product: Product
) -> None:
    """Test POST request to update_cart_checkout view."""
    test_cart.add(test_product, quantity=1)
    url = reverse("cart:update_cart_checkout", args=[test_product.id])
    response = auth_client.post(url, {"quantity": 3})
    assert response.status_code == 302
    assert response.url == reverse("cart:checkout")
    item = CartItem.objects.get(cart=test_cart, product=test_product)
    assert item.quantity == 3


def test_remove_from_cart_checkout_view(
    auth_client: Client, test_cart: Cart, test_product: Product
) -> None:
    """Test POST request to remove_from_cart_checkout view."""
    test_cart.add(test_product, quantity=1)
    url = reverse("cart:remove_from_cart_checkout", args=[test_product.id])
    response = auth_client.post(url)
    assert response.status_code == 302
    assert response.url == reverse("cart:checkout")
    assert test_cart.count() == 0


def test_create_checkout_session_incomplete_address(
    auth_client: Client, test_cart: Cart, test_product: Product
) -> None:
    """Test checkout redirect when account has incomplete addresses."""
    test_cart.add(test_product, quantity=1)
    url = reverse("cart:create_checkout_session")
    response = auth_client.post(url)
    assert response.status_code == 302
    assert response.url == reverse("account:account")


def test_create_checkout_session_empty_cart(
    auth_client: Client, test_user: Account
) -> None:
    """Test checkout redirect when cart is empty."""
    test_user.billing_address_line1 = "123 Main St"
    test_user.billing_city = "Montreal"
    test_user.billing_postal_code = "H3Z 2Y7"
    test_user.billing_country = "Canada"
    test_user.shipping_address_line1 = "123 Main St"
    test_user.shipping_city = "Montreal"
    test_user.shipping_postal_code = "H3Z 2Y7"
    test_user.shipping_country = "Canada"
    test_user.save()

    url = reverse("cart:create_checkout_session")
    response = auth_client.post(url)
    assert response.status_code == 302
    assert response.url == reverse("cart:cart")


@patch("cart.views.Order.create_from_cart")
def test_create_checkout_session_success(
    mock_create_from_cart: MagicMock,
    auth_client: Client,
    test_user: Account,
    test_cart: Cart,
    test_product: Product,
) -> None:
    """Test checkout session creation success redirects to stripe url."""
    test_user.billing_address_line1 = "123 Main St"
    test_user.billing_city = "Montreal"
    test_user.billing_postal_code = "H3Z 2Y7"
    test_user.billing_country = "Canada"
    test_user.shipping_address_line1 = "123 Main St"
    test_user.shipping_city = "Montreal"
    test_user.shipping_postal_code = "H3Z 2Y7"
    test_user.shipping_country = "Canada"
    test_user.save()

    test_cart.add(test_product, quantity=1)

    mock_session = MagicMock()
    mock_session.url = "https://checkout.stripe.com/test_session"
    mock_order = MagicMock()
    mock_create_from_cart.return_value = (mock_session, mock_order)

    url = reverse("cart:create_checkout_session")
    response = auth_client.post(url)
    assert response.status_code == 302
    assert response.url == "https://checkout.stripe.com/test_session"


def test_success_view_stripe_error(
    auth_client: Client, test_user: Account, test_cart: Cart, test_product: Product
) -> None:
    """Test Stripe retrieval error in success view does not clear cart."""
    test_cart.add(test_product, quantity=2)
    url_success = reverse("cart:success") + "?session_id=cs_test_123"

    with patch("cart.views.stripe.checkout.Session.retrieve") as mock_retrieve:
        mock_retrieve.side_effect = stripe.StripeError("Stripe error description")
        response = auth_client.get(url_success)
        assert response.status_code == 200
        assert test_cart.count() == 2


def test_cancel_view(auth_client: Client) -> None:
    """Test the cancel view returns a 200 OK."""
    url = reverse("cart:cancel")
    response = auth_client.get(url)
    assert response.status_code == 200


@patch("cart.webhooks.stripe.Webhook.construct_event")
def test_stripe_webhook_invalid_signature(
    mock_construct: MagicMock, client: Client
) -> None:
    """Test webhook fails with 400 when Stripe signature is invalid."""
    os.environ["STRIPE_WEBHOOK_SECRET"] = "test_webhook_secret"
    mock_construct.side_effect = stripe.SignatureVerificationError(
        "Invalid sig", "sig_header"
    )
    response = client.post(
        reverse("cart:stripe_webhook"),
        data="dummy payload",
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="invalid signature",
    )
    assert response.status_code == 400


@patch("cart.webhooks.stripe.Webhook.construct_event")
def test_stripe_webhook_invalid_order_id_valid_pi_id(
    mock_construct: MagicMock,
    client: Client,
    test_user: Account,
    create_order: Callable[..., Order],
) -> None:
    """Test webhook falls back to payment_intent ID when client_reference_id is invalid."""
    os.environ["STRIPE_WEBHOOK_SECRET"] = "test_webhook_secret"
    order = create_order(user=test_user, total_cents=3000, payment_id="pi_test_123")
    mock_construct.return_value = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "client_reference_id": "99999",
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


@patch("cart.webhooks.stripe.Webhook.construct_event")
def test_stripe_webhook_fallback_to_session_id(
    mock_construct: MagicMock,
    client: Client,
    test_user: Account,
    create_order: Callable[..., Order],
) -> None:
    """Test webhook falls back to session ID when other IDs are missing or fail."""
    os.environ["STRIPE_WEBHOOK_SECRET"] = "test_webhook_secret"
    order = create_order(user=test_user, total_cents=3000, payment_id="cs_test_123")
    mock_construct.return_value = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "client_reference_id": "",
                "payment_intent": "",
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


@patch("cart.webhooks.stripe.Webhook.construct_event")
def test_stripe_webhook_order_not_found(
    mock_construct: MagicMock, client: Client
) -> None:
    """Test webhook returns 404 when order is not found by any ID."""
    os.environ["STRIPE_WEBHOOK_SECRET"] = "test_webhook_secret"
    mock_construct.return_value = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "client_reference_id": "99999",
                "payment_intent": "pi_nonexistent",
                "id": "cs_nonexistent",
            }
        },
    }
    response = client.post(
        reverse("cart:stripe_webhook"),
        data="dummy payload",
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="dummy signature",
    )
    assert response.status_code == 404


@patch("cart.webhooks.stripe.Webhook.construct_event")
def test_stripe_webhook_order_no_account(
    mock_construct: MagicMock,
    client: Client,
) -> None:
    """Test webhook returns 400 when order exists but has no user account associated."""
    os.environ["STRIPE_WEBHOOK_SECRET"] = "test_webhook_secret"
    order = Order.objects.create(
        total_cents=3000, status=Order.STATUS_PENDING, payment_id="pi_no_account"
    )
    mock_construct.return_value = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "client_reference_id": str(order.id),
                "payment_intent": "pi_no_account",
                "id": "cs_no_account",
            }
        },
    }
    response = client.post(
        reverse("cart:stripe_webhook"),
        data="dummy payload",
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="dummy signature",
    )
    assert response.status_code == 400


@patch("cart.webhooks.stripe.Webhook.construct_event")
def test_stripe_webhook_payment_failed_nonexistent_order(
    mock_construct: MagicMock, client: Client
) -> None:
    """Test webhook returns 200 when payment failure event fails to find corresponding order."""
    os.environ["STRIPE_WEBHOOK_SECRET"] = "test_webhook_secret"
    mock_construct.return_value = {
        "type": "payment_intent.payment_failed",
        "data": {
            "object": {
                "id": "pi_nonexistent",
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


@patch("cart.webhooks.stripe.Webhook.construct_event")
def test_stripe_webhook_payment_failed_existing_order(
    mock_construct: MagicMock,
    client: Client,
    test_user: Account,
    create_order: Callable[..., Order],
) -> None:
    """Test webhook sets status to cancelled when a payment failure event is received for an order."""
    os.environ["STRIPE_WEBHOOK_SECRET"] = "test_webhook_secret"
    order = create_order(user=test_user, total_cents=3000, payment_id="pi_failed_123")
    mock_construct.return_value = {
        "type": "payment_intent.payment_failed",
        "data": {
            "object": {
                "id": "pi_failed_123",
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
    assert order.status == Order.STATUS_CANCELLED
