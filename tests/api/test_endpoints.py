import pytest
import requests
from typing import Any
from shop.models import Product


@pytest.mark.django_db
def test_api_products_auth_missing(live_server: Any) -> None:
    """Test that requesting without an Authorization header returns 401."""
    url = f"{live_server.url}/en/shop/api/products/"
    response = requests.get(url)
    assert response.status_code == 401
    json_data = response.json()
    assert json_data["detail"] == "Authentication credentials were not provided."


@pytest.mark.django_db
def test_api_products_auth_invalid_schema(live_server: Any) -> None:
    """Test that requesting with an invalid authorization schema returns 401."""
    url = f"{live_server.url}/en/shop/api/products/"
    headers = {"Authorization": "Basic c2VjcmV0LWFwaS10b2tlbi0xMjM="}
    response = requests.get(url, headers=headers)
    assert response.status_code == 401
    json_data = response.json()
    assert json_data["detail"] == "Invalid token header. No credentials provided."


@pytest.mark.django_db
def test_api_products_auth_invalid_token(live_server: Any) -> None:
    """Test that requesting with a wrong bearer token returns 403."""
    url = f"{live_server.url}/en/shop/api/products/"
    headers = {"Authorization": "Bearer wrong-token-123"}
    response = requests.get(url, headers=headers)
    assert response.status_code == 403
    json_data = response.json()
    assert json_data["detail"] == "Invalid token."


@pytest.mark.django_db
def test_api_products_success(live_server: Any, test_product: Product) -> None:
    """Test that requesting with correct credentials returns 200 and product list."""
    url = f"{live_server.url}/en/shop/api/products/"
    headers = {"Authorization": "Bearer secret-api-token-123"}
    response = requests.get(url, headers=headers)
    assert response.status_code == 200

    # Check JSON response structure and values
    json_data = response.json()
    assert isinstance(json_data, list)
    assert len(json_data) == 1

    product_data = json_data[0]
    assert product_data["id"] == test_product.id
    assert product_data["name"] == test_product.name
    assert product_data["price_in_cents"] == test_product.price_in_cents
    assert product_data["quantity"] == test_product.quantity
    assert product_data["discount_percentage"] == test_product.discount_percentage
