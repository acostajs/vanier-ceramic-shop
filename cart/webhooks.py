import os
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest, HttpResponse
from .models import Order


@csrf_exempt
def stripe_webhook(request: HttpRequest) -> HttpResponse:
    """Handle Stripe events."""
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ["STRIPE_WEBHOOK_SECRET"]
        )
    except (ValueError, stripe.SignatureVerificationError):
        return HttpResponse(status=400)

    if (
        event["type"] == "checkout.session.completed"
        or event["type"] == "checkout.session.async_payment_succeeded"
    ):
        stripe_session = event["data"]["object"]
        session_id = stripe_session.get("id")
        pi_id = stripe_session.get("payment_intent")
        order_id = stripe_session.get("client_reference_id")

        order = None
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
            except (Order.DoesNotExist, ValueError):
                pass

        if not order and pi_id:
            try:
                order = Order.objects.get(payment_id=pi_id)
            except Order.DoesNotExist:
                pass

        if not order and session_id:
            try:
                order = Order.objects.get(payment_id=session_id)
            except Order.DoesNotExist:
                pass

        if not order:
            return HttpResponse(status=404)

        if not order.account:
            return HttpResponse(status=400)

        order.fulfill(payment_id=pi_id)

        order.set_status("paid")

    elif event["type"] in ("payment_intent.payment_failed", "payment_intent.canceled"):
        payment_intent = event["data"]["object"]
        pi_id = payment_intent["id"]

        try:
            order = Order.objects.get(payment_id=pi_id)
        except Order.DoesNotExist:
            return HttpResponse(status=200)

        order.set_status("cancelled")

    return HttpResponse(status=200)
