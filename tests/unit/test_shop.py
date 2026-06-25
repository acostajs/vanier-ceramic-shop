import pytest
from django.utils import timezone
import datetime
from shop.models import Collection, Product
from typing import Callable


def test_collection_creation(test_collection: Collection) -> None:
    """Test that a Collection is created with correct fields."""
    assert test_collection.name == "Stoneware Collection"
    assert test_collection.description == "Handcrafted stoneware pieces."
    assert test_collection.ceramic_type == "Stoneware"
    assert test_collection.year == 2026
    assert str(test_collection) == "Stoneware Collection"


def test_product_availability(create_product: Callable[..., Product]) -> None:
    """Test product availability status based on stock quantity."""
    available_product = create_product(quantity=5)
    unavailable_product = create_product(quantity=0)

    assert available_product.is_available is True
    assert unavailable_product.is_available is False


def test_product_price_in_dollars(test_product: Product) -> None:
    """Test conversion of price in cents to formatted dollar string."""
    assert test_product.price_in_dollars == "$45.00"


def test_product_discounted_price(
    create_product: Callable[..., Product],
) -> None:
    """Test price calculations when a discount is applied."""
    no_discount_product = create_product(price_in_cents=1000, discount_percentage=0)
    discount_product = create_product(price_in_cents=1000, discount_percentage=10)

    assert no_discount_product.get_discounted_price() == 1000
    assert no_discount_product.discounted_price_in_dollars == "$10.00"

    assert discount_product.get_discounted_price() == 900
    assert discount_product.discounted_price_in_dollars == "$9.00"


def test_product_created_recently(
    create_product: Callable[..., Product],
) -> None:
    """Test if product was created recently (within last 30 days)."""
    now = timezone.now()
    recent_product = create_product(created_date=now)
    old_product = create_product(created_date=now - datetime.timedelta(days=31))

    assert recent_product.created_recently is True
    assert old_product.created_recently is False


def test_product_discount_from_quantity(
    create_product: Callable[..., Product],
) -> None:
    """Test decrementing product inventory stock."""
    from django.core.exceptions import ValidationError

    product = create_product(quantity=10)
    product.discount_from_quantity(3)
    assert product.quantity == 7

    with pytest.raises(ValidationError):
        product.discount_from_quantity(11)

    with pytest.raises(ValidationError):
        product.discount_from_quantity(0)

    with pytest.raises(ValidationError):
        product.discount_from_quantity(-5)
