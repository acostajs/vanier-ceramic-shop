from django.shortcuts import get_object_or_404, render
from .models import Collection, Product


def shop(request):
    """Display Shop, showing the different collections."""
    return render(request, "shop/shop.html")


def collection(request, collection_id):
    """Display a single Collection, showing the different products in that collection."""
    collection = get_object_or_404(Collection, id=collection_id)
    products = collection.product_set.all()
    context = {
        "collection": collection,
        "products": products,
    }
    return render(request, "shop/collection.html", context)


def product(request, product_id):
    """Display a single Product detail page."""
    product = get_object_or_404(Product, id=product_id)
    context = {
        "product": product,
    }
    return render(request, "shop/product.html", context)


def home(request):
    """Display the homepage, showing the most recent products."""
    recent_products = Product.objects.all().order_by("-created_date")[:3]
    return render(request, "home.html", {"recent_products": recent_products})
