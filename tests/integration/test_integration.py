import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from django.test import Client
from django.db import transaction
from django.core.exceptions import ValidationError
from account.models import Account
from shop.models import Collection, Product
from cart.models import Cart, Order, OrderItem
from typing import Callable


@pytest.mark.django_db
def test_orm_queries_and_relationships(
    test_collection: Collection, create_product: Callable[..., Product]
) -> None:
    """Test standard ORM queries, foreign key relationships, and querysets."""
    create_product(name="Collection Vase 1", price_in_cents=3000)
    create_product(name="Collection Vase 2", price_in_cents=5000)

    # Query all products in this collection
    products_in_col = Product.objects.filter(collection=test_collection).order_by(
        "price_in_cents"
    )

    assert products_in_col.count() == 2
    assert products_in_col[0].name == "Collection Vase 1"
    assert products_in_col[1].name == "Collection Vase 2"

    # Reverse relationship lookup
    assert test_collection.product_set.count() == 2


@pytest.mark.django_db
def test_view_response_and_session_state_via_client(
    client: Client, test_user: Account, test_product: Product
) -> None:
    """Test requests, redirects, and state changes via the Django Client (TestClient)."""
    # 1. Accessing account page anonymously should redirect to login
    response = client.get(reverse("account:account"))
    assert response.status_code == 302
    assert "login" in response.url

    # 2. Log in through the client
    client.force_login(test_user)

    # Now accessing account page should succeed (200)
    response_auth = client.get(reverse("account:account"))
    assert response_auth.status_code == 200
    assert test_user.username.encode() in response_auth.content


@pytest.mark.django_db
def test_db_state_after_order_transaction(
    test_user: Account,
    create_product: Callable[..., Product],
    create_order: Callable[..., Order],
) -> None:
    """Test database state updates after order completion transactions."""
    product = create_product(name="Stoneware Platter", quantity=10, price_in_cents=6000)
    order = create_order(user=test_user, total_cents=12000)

    # Create order item
    OrderItem.objects.create(
        order=order, product=product, quantity=2, unit_price_cents=6000
    )

    # Ensure initial DB state
    assert product.quantity == 10

    # Execute order payment transaction / status change
    with transaction.atomic():
        order.set_status("paid")

    # Verify updated DB state
    product.refresh_from_db()
    assert product.quantity == 8

    # Verify transaction constraints (out of stock raises ValidationError and rolls back)
    order2 = create_order(user=test_user, total_cents=60000)
    OrderItem.objects.create(
        order=order2,
        product=product,
        quantity=15,  # Exceeds available stock (8)
        unit_price_cents=6000,
    )

    # Verify transaction rollback upon ValidationError
    with pytest.raises(ValidationError):
        with transaction.atomic():
            order2.set_status("paid")

    # DB state should remain 8 after rolled back transaction
    product.refresh_from_db()
    assert product.quantity == 8

    # Verify order2 status remained pending
    order2.refresh_from_db()
    assert order2.status == Order.STATUS_PENDING


@pytest.mark.django_db
def test_cart_to_order_conversion(
    client: Client,
    test_user: Account,
    test_cart: Cart,
    test_product: Product,
) -> None:
    """Test full integration flow of converting a cart to an order during checkout."""
    # 1. Ensure user has a complete address to pass address validation
    test_user.billing_address_line1 = "123 Ceramic Way"
    test_user.billing_city = "Montreal"
    test_user.billing_postal_code = "H3Z 2Y7"
    test_user.billing_country = "Canada"
    test_user.shipping_address_line1 = "123 Ceramic Way"
    test_user.shipping_city = "Montreal"
    test_user.shipping_postal_code = "H3Z 2Y7"
    test_user.shipping_country = "Canada"
    test_user.save()

    # 2. Add product to cart
    test_cart.add(test_product, quantity=2)
    assert test_cart.count() == 2

    # Log in user
    client.force_login(test_user)

    # 3. Simulate hitting the checkout session creation view (checkout redirect)
    url_checkout = reverse("cart:create_checkout_session")

    with patch("cart.models.stripe.checkout.Session.create") as mock_stripe_create:
        mock_session = MagicMock()
        mock_session.id = "cs_test_123"
        mock_session.payment_intent = "pi_test_123"
        mock_session.url = "https://checkout.stripe.com/test_session"
        mock_stripe_create.return_value = mock_session

        response = client.post(url_checkout)
        assert response.status_code == 302
        assert response.url == "https://checkout.stripe.com/test_session"

    # 4. Verify that the correct Order and OrderItem records are created in DB
    assert Order.objects.filter(account=test_user).count() == 1
    order = Order.objects.get(account=test_user)
    assert order.total_cents == 2 * test_product.price_in_cents
    assert order.status == Order.STATUS_PENDING
    assert order.payment_id == "pi_test_123"

    assert order.items.count() == 1
    order_item = order.items.first()
    assert order_item.product == test_product
    assert order_item.quantity == 2
    assert order_item.unit_price_cents == test_product.price_in_cents

    # 5. Simulate redirecting back to the success view with the session ID
    url_success = reverse("cart:success") + "?session_id=cs_test_123"

    with patch("cart.views.stripe.checkout.Session.retrieve") as mock_retrieve:
        mock_retrieved_session = MagicMock()
        mock_retrieved_session.payment_status = "paid"
        mock_retrieve.return_value = mock_retrieved_session

        response_success = client.get(url_success)
        assert response_success.status_code == 200

    # 6. Verify cart is cleared
    test_cart.refresh_from_db()
    assert test_cart.count() == 0
