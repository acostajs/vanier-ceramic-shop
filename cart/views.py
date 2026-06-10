import stripe
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Order, Cart
from .helpers import parse_quantity, get_cart
from shop.models import Product
from .validation import has_complete_addresses
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, Http404


@login_required
def cart(request: HttpRequest) -> HttpResponse:
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
def add_to_cart(request: HttpRequest, product_id: int) -> HttpResponse:
    """To add a product to Cart."""
    cart = get_cart(request)
    product = get_object_or_404(Product, pk=product_id)
    qty = parse_quantity(request)
    cart.add(product, quantity=qty)
    messages.success(
        request,
        _("Added %(name)s (x%(qty)d) to cart.") % {"name": product.name, "qty": qty},
    )
    return redirect("shop:product", product_id=product.id)


@login_required
@require_POST
def update_cart(request: HttpRequest, product_id: int) -> HttpResponse:
    """Update the quantity of a product in the Cart."""
    cart = get_cart(request)
    product = get_object_or_404(Product, pk=product_id)
    qty = parse_quantity(request)
    cart.add(product, quantity=qty, replace=True)
    messages.success(
        request,
        _("Updated %(name)s (x%(qty)d) to cart.") % {"name": product.name, "qty": qty},
    )
    return redirect("cart:cart")


@login_required
@require_POST
def remove_from_cart(request: HttpRequest, product_id: int) -> HttpResponse:
    """Remove a product completely from the Cart."""
    cart = get_cart(request)
    product = get_object_or_404(Product, pk=product_id)
    cart.remove(product)
    messages.success(request, _("Removed %(name)s from cart.") % {"name": product.name})
    return redirect("cart:cart")


@login_required
@require_POST
def clear_cart(request: HttpRequest) -> HttpResponse:
    """Remove all products from the Cart."""
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
        "subtotal_dollars": cart.subtotal_dollars(),
        "cart_count": cart.count(),
    }
    return render(request, "cart/checkout.html", context)


@login_required
@require_POST
def update_cart_checkout(request, product_id):
    """Update a product's quantity during checkout."""
    product = get_object_or_404(Product, pk=product_id)
    qty = parse_quantity(request)
    cart = get_cart(request)
    cart.add(product, quantity=qty, replace=True)
    messages.success(
        request,
        _("Updated %(name)s to x%(qty)d.") % {"name": product.name, "qty": qty},
    )
    return redirect("cart:checkout")


@login_required
@require_POST
def remove_from_cart_checkout(request, product_id):
    """Remove a product from the cart during checkout."""
    product = get_object_or_404(Product, pk=product_id)
    cart = get_cart(request)
    cart.remove(product)
    messages.info(request, _("Removed %(name)s from cart.") % {"name": product.name})
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


@login_required
def success(request: HttpRequest) -> HttpResponse:
    """Handle successful Stripe Payments."""
    session_id = request.GET.get("session_id")
    if session_id:
        processed_sessions = request.session.setdefault("processed_stripe_sessions", [])
        if session_id not in processed_sessions:
            try:
                session = stripe.checkout.Session.retrieve(session_id)
                if session.payment_status == "paid":
                    cart = get_cart(request)
                    cart.clear()
                    processed_sessions.append(session_id)
                    request.session.modified = True
                    messages.success(
                        request, _("Payment successful! Your order has been placed.")
                    )
            except Exception:
                pass
    return render(request, "cart/success.html", {"session_id": session_id})


def cancel(request: HttpRequest) -> HttpResponse:
    """Handle cancelled Stripe Checkout Sessions."""
    return render(request, "cart/cancel.html")


@login_required
def order_details(request: HttpRequest, order_id: int) -> HttpResponse:
    """Display Order Details."""
    order = get_object_or_404(Order, pk=order_id)
    if order.account != request.user:
        raise Http404("Order not found.")

    context = {"order": order}
    return render(request, "cart/order_details.html", context)
