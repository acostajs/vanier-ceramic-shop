from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, LoginForm, ShippingForm, BillingForm
from cart.models import Cart
from shop.models import Product
from .models import Wishlist
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import (
    authenticate,
    login as auth_login,
    logout as auth_logout,
)
from django.utils.translation import gettext_lazy as _


def registration(request):
    """Display Register form for the User to register an Account."""

    form = RegistrationForm()
    context = {"form": form}

    return render(request, "account/registration.html", context)


@require_POST
def registration_submit(request):
    """Handles the registration submit, it register user to an Account."""

    form = RegistrationForm(request.POST)
    if form.is_valid():
        user = form.save()
        Wishlist.objects.create(account=user)
        Cart.objects.create(account=user)
        msg = "Your account has properly been created."
        messages.success(request, msg)
        return redirect("account:login")

    context = {"form": form}

    return render(request, "account/registration.html", context)


def login(request):
    """Display Login form for the User to log in into an Account."""
    form = LoginForm()
    context = {"form": form}

    return render(request, "account/login.html", context)


@require_POST
def login_submit(request):
    """Process the login form submission with authentication."""
    form = LoginForm(request.POST)

    if form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )
        if user:
            auth_login(request, user)
            msg = "You have Logged in Successfully."
            messages.success(request, msg)
            return redirect("account:account")
        else:
            form.add_error(None, _("Invalid username or password"))

    return render(request, "account/login.html", {"form": form})


@login_required(login_url="account:login")
def logout(request):
    """Display Logout form for the User from Account Session."""
    auth_logout(request)
    msg = "You have logout Successfully."
    messages.success(request, msg)
    return redirect("account:login")


@login_required(login_url="account:login")
def account(request):
    """Display User Account Information."""
    account = request.user
    orders = account.order_set.all()
    context = {
        "account": account,
        "orders": orders,
    }

    return render(request, "account/account.html", context)


@login_required(login_url="account:login")
@require_GET
def wishlist_detail(request):
    """Display the wishlist if the user is logged in."""
    wishlist = get_object_or_404(Wishlist, account=request.user)
    wishlist_products = wishlist.product.all()

    context = {
        "wishlist": wishlist,
        "wishlist_products": wishlist_products,
    }
    return render(request, "account/wishlist.html", context)


@login_required(login_url="account:login")
@require_POST
def add_to_wishlist(request, product_id):
    """Adds a product to the wishlist if the user is logged in."""
    product = get_object_or_404(Product, pk=product_id)
    wishlist = get_object_or_404(Wishlist, account=request.user)
    wishlist.add(product)
    messages.success(request, f"Added {product.name} to wishlist.")
    return redirect("shop:product", product_id)


@login_required(login_url="account:login")
@require_POST
def remove_from_wishlist(request, product_id):
    """Removes a product from the wishlist if the user is logged in."""
    product = get_object_or_404(Product, pk=product_id)
    user = request.user
    wishlist = get_object_or_404(Wishlist, account=user)
    wishlist.remove(product)
    messages.info(request, f"Removed {product.name} from wishlist.")
    return redirect("account:wishlist_detail")


@login_required(login_url="account:login")
@require_POST
def clear_wishlist(request):
    """Clear the wishlist from all products if the user is logged in."""
    wishlist = get_object_or_404(Wishlist, account=request.user)
    wishlist.clear()
    messages.info(request, _("Wishlist cleared."))
    return redirect("account:wishlist_detail")


@login_required(login_url="account:login")
@require_POST
def transfer_to_cart(request, product_id):
    """Transfer all the products in the wishlist to the user account related cart."""
    wishlist = Wishlist.objects.get(account=request.user)
    cart = Cart(request)
    for product in wishlist.product.all():
        cart.add(product, quantity=1)
    wishlist.clear()
    msg = "You have succesfully transfer the item to your shopping cart."
    messages.success(request, msg)

    return redirect("cart:cart_detail")


@login_required(login_url="account:login")
def shipping(request):
    """Display Shipping formulary."""
    account = request.user
    form = ShippingForm(instance=account)
    context = {"form": form, "account": account}

    return render(request, "account/shipping.html", context)


@login_required(login_url="account:login")
@require_POST
def shipping_submit(request):
    """Handles update of the user shipping information."""
    account = request.user

    form = ShippingForm(request.POST, instance=account)
    if form.is_valid():
        form.save()
        msg = "Your Shipping Information has been Updated"
        messages.success(request, msg)
        return redirect("account:account")

    return render(request, "account/shipping.html", {"form": form})


@login_required(login_url="account:login")
def billing(request):
    """Display Billing formulary."""
    account = request.user
    form = BillingForm(instance=account)
    context = {"form": form, "account": account}

    return render(request, "account/billing.html", context)


@login_required(login_url="account:login")
@require_POST
def billing_submit(request):
    """Handles the update of the user billing information."""
    account = request.user

    form = BillingForm(request.POST, instance=account)
    if form.is_valid():
        form.save()
        msg = "Your Billing Information has been Updated"
        messages.success(request, msg)
        return redirect("account:account")

    return render(request, "account/billing.html", {"form": form})
