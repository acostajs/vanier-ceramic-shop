from django.urls import path
from . import views

app_name = "account"
urlpatterns = [
    path("", views.account, name="account"),
    path("registration/", views.registration, name="registration"),
    path("registration/submit/", views.registration_submit, name="registration_submit"),
    path("login/", views.login, name="login"),
    path("login/submit/", views.login_submit, name="login_submit"),
    path("logout/", views.logout, name="logout"),
    path("wishlist/", views.wishlist_detail, name="wishlist_detail"),
    path(
        "wishlist/add/<int:product_id>", views.add_to_wishlist, name="add_to_wishlist"
    ),
    path(
        "wishlist/remove/<int:product_id>",
        views.remove_from_wishlist,
        name="remove_from_wishlist",
    ),
    path("wishlist/clear/", views.clear_wishlist, name="clear_wishlist"),
    path(
        "wishlist/transfer/<int:product_id>",
        views.transfer_to_cart,
        name="transfer_to_cart",
    ),
    path("shipping/", views.shipping, name="shipping"),
    path("billing/", views.billing, name="billing"),
    path("shipping_submit/", views.shipping_submit, name="shipping_submit"),
    path("billing_submit/", views.billing_submit, name="billing_submit"),
]
