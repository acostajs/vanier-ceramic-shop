from .models import Cart


def cart_info(request):
    cart = Cart(request)
    count = cart.count()
    return {"cart_count": count}
