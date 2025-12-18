from django.urls import path
from . import views

app_name = "cart"
urlpatterns = [
    path("", views.cart, name="cart"),
    path("add/<int:product_id>", views.add_to_cart, name="add_to_cart"),
    path("update/<int:product_id>", views.update_cart, name="update_cart"),
    path("remove/<int:product_id>", views.remove_from_cart, name="remove_from_cart"),
    path("clear/", views.clear_cart, name="clear_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path(
        "checkout/update/<int:product_id>",
        views.update_cart_checkout,
        name="update_cart_checkout",
    ),
    path(
        "checkout/remove/<int:product_id>",
        views.remove_from_cart_checkout,
        name="remove_from_cart_checkout",
    ),
    path(
        "checkout/checkout/stripe",
        views.create_checkout_session,
        name="create_checkout_session",
    ),
    path("checkout/succes/", views.success, name="success"),
    path("checkout/canceled/", views.cancel, name="cancel"),
    path("order_details/<int:order_id>", views.order_details, name="order_details"),
]
