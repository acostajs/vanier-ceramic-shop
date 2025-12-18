from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Order, Cart
from .helpers import parse_quantity, get_cart
from shop.models import Product
from .validation import has_complete_addresses
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib import messages


@login_required
def cart(request):
    """Display Cart."""
    cart = get_cart(request)
    context = {
        "cart": cart,
        "cart_items": cart.items(),
        "subtotal_dollars": cart.subtotal_dollars(),
    }
    return render(request, "cart/cart.html", context)


@login_required
@require_POST
def add_to_cart(request, product_id):
    """To add a product to Cart."""
    cart = get_cart(request)
    product = get_object_or_404(Product, pk=product_id)
    qty = parse_quantity(request)
    cart.add(product, quantity=qty)
    messages.success(request, _(f"Added {product.name} (x{qty}) to cart."))
    context = {"product": product}
    return render(request, "shop/product.html", context)


@login_required
@require_POST
def update_cart(request, product_id):
    """To add a product to Cart."""
    cart = get_cart(request)
    product = get_object_or_404(Product, pk=product_id)
    qty = parse_quantity(request)
    cart.add(product, quantity=qty, replace=True)
    messages.success(request, _(f"Updated {product.name} (x{qty}) to cart."))
    return redirect("cart:cart")


@login_required
@require_POST
def remove_from_cart(request, product_id):
    """To add a product to Cart."""
    cart = get_cart(request)
    product = get_object_or_404(Product, pk=product_id)
    cart.remove(product)
    messages.success(request, _(f"Removed {product.name} from cart."))
    return redirect("cart:cart")


@login_required
@require_POST
def clear_cart(request):
    """To add a product to Cart."""
    cart = get_cart(request)
    cart.clear()
    messages.success(request, _("Cart Cleared."))
    return redirect("cart:cart")


@login_required
def checkout(request):
    """Display checkout page with cart summary."""
    cart = get_cart(request)
    context = {
        "cart_items": list(cart.items()),
        "subtotal_cents": cart.subtotal_cents(),
        "cart_count": cart.count(),
    }
    return render(request, "cart/checkout.html", context)


@require_POST
def update_cart_checkout(request, product_id):
    """Update a product's quantity during checkout."""
    product = get_object_or_404(Product, pk=product_id)
    qty = parse_quantity(request)
    cart = get_cart(request)
    cart.add(product, quantity=qty, replace=True)
    messages.success(request, f"Updated {product.name} to x{qty}.")
    return redirect("cart:checkout")


@require_POST
def remove_from_cart_checkout(request, product_id):
    """Remove a product from the cart during checkout."""
    product = get_object_or_404(Product, pk=product_id)
    cart = get_cart(request)
    cart.remove(product)
    messages.info(request, f"Removed {product.name} from cart.")
    return redirect("cart:checkout")


@login_required
@require_POST
def create_checkout_session(request):
    """Create Stripe Checkout session from cart and redirect to Stripe."""
    account = request.user
    cart = get_object_or_404(Cart, account=account)

    if not has_complete_addresses(account):
        messages.warning(
            request,
            _("Please complete your billing and shipping address before checkout."),
        )
        return redirect("account:account")

    session, order = Order.create_from_cart(request, cart, account)

    if not session:
        messages.warning(request, _("Your cart is empty."))
        return redirect("cart:cart")

    return redirect(session.url, code=303)


def success(request):
    """Handle succesful Stripe Payments."""
    session_id = request.GET.get("session_id")
    cart = get_cart(request)
    cart.clear()
    messages.success(request, _("Payment successful! Your order has been placed."))
    return render(request, "cart/success.html", {"session_id": session_id})


def cancel(request):
    """Handle cancelled Stripe Checkout Sessions."""
    return render(request, "cart/cancel.html")


@login_required
def order_details(request, order_id):
    """Display Order Details."""
    order = get_object_or_404(Order, pk=order_id)

    context = {"order": order}
    return render(request, "cart/order_details.html", context)
