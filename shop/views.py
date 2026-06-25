from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
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


@require_GET
def api_products(request):
    """API endpoint to get list of products. Requires Bearer Token Auth."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return JsonResponse(
            {"detail": "Authentication credentials were not provided."},
            status=401,
        )

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return JsonResponse(
            {"detail": "Invalid token header. No credentials provided."},
            status=401,
        )

    token = parts[1]
    if token != "secret-api-token-123":
        return JsonResponse({"detail": "Invalid token."}, status=403)

    products = Product.objects.all().order_by("id")
    data = []
    for product in products:
        data.append(
            {
                "id": product.id,
                "name": product.name,
                "price_in_cents": product.price_in_cents,
                "quantity": product.quantity,
                "discount_percentage": product.discount_percentage,
            }
        )
    return JsonResponse(data, safe=False)
