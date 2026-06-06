from .models import Cart


def cart_info(request):
    """Get the total count of products inside Cart."""
    if not request.user or not request.user.is_authenticated:
        return {"cart_count": 0}
    try:
        cart = Cart.objects.get(account=request.user)
        count = cart.count()
    except Cart.DoesNotExist:
        count = 0
    return {"cart_count": count}
