import pytest
from django.urls import reverse
from django.test import Client
from django.db import transaction
from django.core.exceptions import ValidationError
from account.models import Account
from shop.models import Collection, Product
from cart.models import Order, OrderItem
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
