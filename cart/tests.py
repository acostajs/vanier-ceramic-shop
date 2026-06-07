from unittest.mock import patch
from django.test import TestCase, RequestFactory
from account.models import Account
from cart.models import Order, Cart, CartItem
from shop.models import Product, Collection
from django.urls import reverse


class BaseCartSetupMixin:
    """To setup for the Cart, CartItem, Order and OrderItem tests."""

    def setUp(self):
        self.account = Account.objects.create_user(
            username="juan",
            email="[email protected]",
            password="testpass123",
        )

        self.collection = Collection.objects.create(name="Default")

        self.product1 = Product.objects.create(
            name="Mug",
            price_in_cents=1500,
            collection=self.collection,
        )
        self.product2 = Product.objects.create(
            name="Plate",
            price_in_cents=2500,
            collection=self.collection,
        )

        self.cart = Cart.objects.create(account=self.account)


class CartModelTests(BaseCartSetupMixin, TestCase):
    """Takes setup from BaseCartSetup and Test Cart Model."""

    def test_add_and_count_items(self):
        self.assertEqual(self.cart.count(), 0)

        self.cart.add(self.product1, quantity=2)
        self.cart.add(self.product2, quantity=1)

        self.assertEqual(self.cart.count(), 3)
        self.assertEqual(CartItem.objects.filter(cart=self.cart).count(), 2)

    def test_add_replace_quantity(self):
        self.cart.add(self.product1, quantity=2)
        self.cart.add(self.product1, quantity=5, replace=True)

        item = CartItem.objects.get(cart=self.cart, product=self.product1)
        self.assertEqual(item.quantity, 5)

    def test_remove_item(self):
        self.cart.add(self.product1, quantity=2)
        self.cart.add(self.product2, quantity=1)
        self.assertEqual(self.cart.count(), 3)

        self.cart.remove(self.product1)

        self.assertEqual(self.cart.count(), 1)
        self.assertFalse(
            CartItem.objects.filter(cart=self.cart, product=self.product1).exists()
        )

    def test_clear_cart(self):
        self.cart.add(self.product1, quantity=2)
        self.cart.add(self.product2, quantity=1)
        self.assertGreater(self.cart.count(), 0)

        self.cart.clear()

        self.assertEqual(self.cart.count(), 0)
        self.assertEqual(CartItem.objects.filter(cart=self.cart).count(), 0)

    def test_subtotals(self):
        self.cart.add(self.product1, quantity=2)
        self.cart.add(self.product2, quantity=1)
        self.assertEqual(self.cart.subtotal_cents(), 5500)
        self.assertEqual(self.cart.subtotal_dollars(), "$55.00")

    def test_cart_str(self):
        self.assertIn(self.account.email, str(self.cart))


class CartItemModelTests(BaseCartSetupMixin, TestCase):
    """Takes setup from BaseCartSetup and Test CartItem Model."""

    def test_cart_item_totals_and_str(self):
        item = CartItem.objects.create(
            cart=self.cart,
            product=self.product1,
            quantity=3,
        )

        self.assertEqual(item.unit_cents, 1500)
        self.assertEqual(item.total_cents, 4500)
        self.assertEqual(item.unit_dollars, self.product1.price_in_dollars)
        self.assertEqual(item.line_dollars, "$45.00")
        self.assertIn(self.product1.name, str(item))

    def test_unique_product_per_cart_constraint(self):
        CartItem.objects.create(cart=self.cart, product=self.product1, quantity=1)
        with self.assertRaises(Exception):
            CartItem.objects.create(cart=self.cart, product=self.product1, quantity=2)


class OrderModelTests(BaseCartSetupMixin, TestCase):
    """Takes setup from BaseCartSetup and Order Model."""

    def test_set_status_valid_and_invalid(self):
        order = Order.objects.create(
            account=self.account,
            total_cents=1000,
        )

        order.set_status("paid")
        self.assertEqual(order.status, Order.STATUS_PAID)

        with self.assertRaises(ValueError):
            order.set_status("something-else")

    def test_total_in_dollars_property(self):
        order = Order.objects.create(
            account=self.account,
            total_cents=1234,
        )
        self.assertEqual(order.total_in_dollars, "$12.34")

    def test_set_status_paid_decrements_inventory(self):
        from django.core.exceptions import ValidationError
        from cart.models import OrderItem

        # Set product1 quantity to 5
        self.product1.quantity = 5
        self.product1.save()

        order = Order.objects.create(
            account=self.account,
            total_cents=1500,
        )
        OrderItem.objects.create(
            order=order,
            product=self.product1,
            quantity=2,
            unit_price_cents=750,
        )

        order.set_status("paid")
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.quantity, 3)

        # Test failure when inventory is insufficient
        order2 = Order.objects.create(
            account=self.account,
            total_cents=1500,
        )
        OrderItem.objects.create(
            order=order2,
            product=self.product1,
            quantity=10,
            unit_price_cents=750,
        )

        with self.assertRaises(ValidationError):
            order2.set_status("paid")

    def test_fulfill_sets_fields(self):
        order = Order.objects.create(
            account=self.account,
            total_cents=0,
        )

        order.fulfill(
            name="Juan",
            email="[email protected]",
            payment_id="pi_123",
            total_cents=5000,
            billing_address_line1="B1",
            billing_address_line2="B2",
            billing_city="BCity",
            billing_postal_code="BZIP",
            billing_country="BCountry",
            shipping_address_line1="S1",
            shipping_address_line2="S2",
            shipping_city="SCity",
            shipping_postal_code="SZIP",
            shipping_country="SCountry",
        )

        order.refresh_from_db()
        self.assertEqual(order.payment_id, "pi_123")
        self.assertEqual(order.name, "Juan")
        self.assertEqual(order.email, "[email protected]")
        self.assertEqual(order.total_cents, 5000)
        self.assertEqual(order.billing_city, "BCity")
        self.assertEqual(order.shipping_city, "SCity")

    def test_order_str(self):
        order = Order.objects.create(
            account=self.account,
            payment_id="pi_abc",
            total_cents=1000,
        )
        s = str(order)
        self.assertIn("pi_abc", s)
        self.assertIn(self.account.email, s)


class OrderCreateFromCartTests(BaseCartSetupMixin, TestCase):
    """Takes setup from BaseCartSetup and Test Order Model taking information from Cart."""

    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()

    @patch("cart.models.stripe.checkout.Session.create")
    def test_create_from_cart_empty(self, mock_stripe):
        request = self.factory.post("/fake/")
        request.user = self.account
        session, order = Order.create_from_cart(request, self.cart, self.account)
        self.assertIsNone(session)
        self.assertIsNone(order)
        mock_stripe.assert_not_called()

    @patch("cart.models.stripe.checkout.Session.create")
    def test_create_from_cart_creates_order_items_and_stripe_session(self, mock_stripe):
        self.cart.add(self.product1, quantity=2)
        self.cart.add(self.product2, quantity=1)

        request = self.factory.post("/fake/")
        request.user = self.account

        mock_stripe.return_value = type(
            "DummySession",
            (),
            {
                "url": "https://stripe.test",
                "id": "cs_test_123",
                "payment_intent": "pi_test_123",
            },
        )()

        session, order = Order.create_from_cart(request, self.cart, self.account)

        self.assertIsNotNone(session)
        self.assertIsNotNone(order)
        self.assertEqual(order.account, self.account)
        self.assertEqual(order.total_cents, self.cart.subtotal_cents())
        self.assertEqual(order.items.count(), 2)
        item = order.items.get(product=self.product1)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.unit_price_cents, self.product1.price_in_cents)
        self.assertEqual(order.payment_id, "pi_test_123")
        self.assertTrue(mock_stripe.called)


class CartViewTests(BaseCartSetupMixin, TestCase):
    """Test login protection on cart views."""

    def test_update_cart_checkout_requires_login(self):
        from django.urls import reverse

        # Anonymous request redirects to login
        url = reverse("cart:update_cart_checkout", args=[self.product1.id])
        response = self.client.post(url)
        # Check redirect. Because of i18n_patterns, the prefix might be added
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

        # Logged-in request works (redirects to checkout after update)
        self.client.login(username="juan", password="testpass123")
        response = self.client.post(url, {"quantity": 3})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("cart:checkout"), fetch_redirect_response=False
        )

    def test_remove_from_cart_checkout_requires_login(self):
        from django.urls import reverse

        # Anonymous request redirects to login
        url = reverse("cart:remove_from_cart_checkout", args=[self.product1.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

        # Logged-in request works
        self.client.login(username="juan", password="testpass123")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("cart:checkout"), fetch_redirect_response=False
        )

    def test_success_requires_login(self):
        from django.urls import reverse

        # Anonymous request redirects to login
        url = reverse("cart:success")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

        # Logged-in request works
        self.client.login(username="juan", password="testpass123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class StripeWebhookTests(BaseCartSetupMixin, TestCase):
    """Test Stripe webhook handling."""

    def setUp(self):
        super().setUp()
        import os

        self.old_webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
        os.environ["STRIPE_WEBHOOK_SECRET"] = "test_webhook_secret"

    def tearDown(self):
        import os

        if self.old_webhook_secret is not None:
            os.environ["STRIPE_WEBHOOK_SECRET"] = self.old_webhook_secret
        else:
            del os.environ["STRIPE_WEBHOOK_SECRET"]
        super().tearDown()

    @patch("cart.webhooks.stripe.Webhook.construct_event")
    def test_stripe_webhook_checkout_session_completed(self, mock_construct):
        from django.urls import reverse

        order = Order.objects.create(
            account=self.account,
            total_cents=1000,
            payment_id="pi_test_123",
        )
        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "client_reference_id": str(order.id),
                    "payment_intent": "pi_test_123",
                    "id": "cs_test_123",
                }
            },
        }

        response = self.client.post(
            reverse("cart:stripe_webhook"),
            data="dummy payload",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="dummy signature",
        )
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_PAID)
        self.assertEqual(order.payment_id, "pi_test_123")

    @patch("cart.webhooks.stripe.Webhook.construct_event")
    def test_stripe_webhook_checkout_session_completed_lookup_by_payment_id(
        self, mock_construct
    ):
        from django.urls import reverse

        # Create an order where client_reference_id might be missing but payment_id matches
        order = Order.objects.create(
            account=self.account,
            total_cents=1000,
            payment_id="pi_test_123",
        )
        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "client_reference_id": None,
                    "payment_intent": "pi_test_123",
                    "id": "cs_test_123",
                }
            },
        }

        response = self.client.post(
            reverse("cart:stripe_webhook"),
            data="dummy payload",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="dummy signature",
        )
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_PAID)

    @patch("cart.webhooks.stripe.Webhook.construct_event")
    def test_stripe_webhook_payment_intent_failed(self, mock_construct):
        from django.urls import reverse

        order = Order.objects.create(
            account=self.account,
            total_cents=1000,
            payment_id="pi_test_123",
        )
        mock_construct.return_value = {
            "type": "payment_intent.payment_failed",
            "data": {
                "object": {
                    "id": "pi_test_123",
                }
            },
        }

        response = self.client.post(
            reverse("cart:stripe_webhook"),
            data="dummy payload",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="dummy signature",
        )
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.STATUS_CANCELLED)


class OrderDetailsViewTests(BaseCartSetupMixin, TestCase):
    def test_order_details_owner_can_access(self):
        order = Order.objects.create(
            account=self.account,
            total_cents=1000,
        )
        self.client.force_login(self.account)
        response = self.client.get(reverse("cart:order_details", args=[order.id]))
        self.assertEqual(response.status_code, 200)

    def test_order_details_non_owner_cannot_access(self):
        other_user = Account.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="otherpassword",
        )
        order = Order.objects.create(
            account=self.account,
            total_cents=1000,
        )
        self.client.force_login(other_user)
        response = self.client.get(reverse("cart:order_details", args=[order.id]))
        self.assertEqual(response.status_code, 404)
