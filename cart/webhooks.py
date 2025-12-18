import os
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import Order


@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe events."""
    print("webhook is running")
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ["STRIPE_WEBHOOK_SECRET"]
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if (
        event["type"] == "checkout.session.completed"
        or event["type"] == "checkout.session.async_payment_succeeded"
    ):
        print("Handling checkout.session.completed")
        stripe_session = event["data"]["object"]
        print("session:", stripe_session)
        order_id = stripe_session["client_reference_id"]
        print("order_id:", order_id)
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return HttpResponse(status=404)

        if not order.account:
            print(f"Order {order_id} has no associated account")
            return HttpResponse(status=400)

        account = order.account
        order.fulfill(
            name=f"{account.first_name} {account.last_name}".strip(),
            email=account.email,
            payment_id=stripe_session["payment_intent"],
            total_cents=order.total_cents,
            billing_address_line1=account.billing_address_line1,
            billing_address_line2=account.billing_address_line2,
            billing_city=account.billing_city,
            billing_postal_code=account.billing_postal_code,
            billing_country=account.billing_country,
            shipping_address_line1=account.shipping_address_line1,
            shipping_address_line2=account.shipping_address_line2,
            shipping_city=account.shipping_city,
            shipping_postal_code=account.shipping_postal_code,
            shipping_country=account.shipping_country,
        )

        order.set_status("paid")

    elif event["type"] in ("payment_intent.payment_failed", "payment_intent.canceled"):
        payment_intent = event["data"]["object"]
        pi_id = payment_intent["id"]

        try:
            order = Order.objects.get(payment_id=pi_id)
        except Order.DoesNotExist:
            return HttpResponse(status=200)

        order.set_status("cancelled")
        print(f"Order {order.id} cancelled")

    return HttpResponse(status=200)
