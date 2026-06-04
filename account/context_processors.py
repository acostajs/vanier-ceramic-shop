from account.models import Wishlist


def wishlist_info(request):
    """Get the total count of products inside Wishlist."""
    if not request.user or not request.user.is_authenticated:
        return {"wishlist_count": 0}
    try:
        wishlist = Wishlist.objects.get(account=request.user)
        count = wishlist.count()
    except Wishlist.DoesNotExist:
        count = 0
    return {"wishlist_count": count}
