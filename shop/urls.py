from django.urls import path
from . import views

app_name = "shop"
urlpatterns = [
    path("", views.shop, name="shop"),
    path("collection/<int:collection_id>/", views.collection, name="collection"),
    path("product/<int:product_id>/", views.product, name="product"),
]
