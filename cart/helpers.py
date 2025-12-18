from .models import Cart
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _


def parse_quantity(request):
    """Helper function to determine how many items we have."""
    try:
        qty = int(request.POST.get("quantity", "1"))
    except (ValueError, TypeError):
        qty = 1
    return max(1, qty)


def get_cart(request):
    """Helper function to get or create cart for the authenticated account."""
    user = request.user
    if not user.is_authenticated:
        raise ImproperlyConfigured(_("get_cart() called without an authenticated user"))

    cart, created = Cart.objects.get_or_create(account=user)
    return cart
