from django.test import TestCase
from django.urls import reverse
from .models import Account, Wishlist
from shop.models import Product, Collection


class AccountModelTests(TestCase):
    """To test Account Model."""

    def test_create_account_with_extra_fields(self):
        account = Account.objects.create_user(
            username="juan",
            email="[email protected]",
            password="testpass123",
            billing_address_line1="123 Billing St",
            billing_city="Montreal",
            billing_postal_code="H1H 1H1",
            billing_country="Canada",
            shipping_address_line1="456 Shipping Ave",
            shipping_city="Montreal",
            shipping_postal_code="H2H 2H2",
            shipping_country="Canada",
        )

        self.assertEqual(account.username, "juan")
        self.assertEqual(str(account), "juan")
        self.assertEqual(account.billing_address_line1, "123 Billing St")
        self.assertEqual(account.billing_city, "Montreal")
        self.assertEqual(account.shipping_address_line1, "456 Shipping Ave")
        self.assertEqual(account.shipping_city, "Montreal")

    def test_account_fields_can_be_blank(self):
        account = Account.objects.create_user(
            username="no_addresses",
            email="[email protected]",
            password="testpass123",
        )

        self.assertIsNone(account.billing_address_line1)
        self.assertIsNone(account.shipping_address_line1)


class WishlistModelTests(TestCase):
    """To Test Wishlist Model."""

    def setUp(self):
        self.account = Account.objects.create_user(
            username="juan",
            email="[email protected]",
            password="testpass123",
        )
        self.wishlist = Wishlist.objects.create(account=self.account)

        self.collection = Collection.objects.create(name="Default collection")

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

    def test_add_product_to_wishlist(self):
        self.assertEqual(self.wishlist.count(), 0)
        self.wishlist.add(self.product1)
        self.assertEqual(self.wishlist.count(), 1)
        self.assertIn(self.product1, self.wishlist.product.all())

    def test_remove_product_from_wishlist(self):
        self.wishlist.add(self.product1)
        self.wishlist.add(self.product2)
        self.assertEqual(self.wishlist.count(), 2)
        self.wishlist.remove(self.product1)
        self.assertEqual(self.wishlist.count(), 1)
        self.assertNotIn(self.product1, self.wishlist.product.all())
        self.assertIn(self.product2, self.wishlist.product.all())

    def test_clear_wishlist(self):
        self.wishlist.add(self.product1)
        self.wishlist.add(self.product2)
        self.assertGreater(self.wishlist.count(), 0)
        self.wishlist.clear()
        self.assertEqual(self.wishlist.count(), 0)

    def test_wishlist_one_to_one_with_account(self):
        self.assertEqual(self.wishlist.account, self.account)
        with self.assertRaises(Exception):
            Wishlist.objects.create(account=self.account)


class WishlistContextProcessorTests(TestCase):
    """To Test Wishlist Context Processor."""

    def setUp(self):
        self.account = Account.objects.create_user(
            username="juan",
            email="juan@example.com",
            password="testpass123",
        )
        self.wishlist = Wishlist.objects.create(account=self.account)
        self.collection = Collection.objects.create(name="Default collection")
        self.product = Product.objects.create(
            name="Mug",
            price_in_cents=1500,
            collection=self.collection,
        )

    def test_anonymous_user_wishlist_count(self):
        from django.test import RequestFactory
        from account.context_processors import wishlist_info
        from django.contrib.auth.models import AnonymousUser

        factory = RequestFactory()
        request = factory.get("/")
        request.user = AnonymousUser()

        context = wishlist_info(request)
        self.assertEqual(context["wishlist_count"], 0)

    def test_authenticated_user_empty_wishlist(self):
        from django.test import RequestFactory
        from account.context_processors import wishlist_info

        factory = RequestFactory()
        request = factory.get("/")
        request.user = self.account

        context = wishlist_info(request)
        self.assertEqual(context["wishlist_count"], 0)

    def test_authenticated_user_with_wishlist_items(self):
        from django.test import RequestFactory
        from account.context_processors import wishlist_info

        self.wishlist.add(self.product)

        factory = RequestFactory()
        request = factory.get("/")
        request.user = self.account

        context = wishlist_info(request)
        self.assertEqual(context["wishlist_count"], 1)


class LogoutViewTests(TestCase):
    def setUp(self):
        self.user = Account.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
        )

    def test_logout_get_requests_are_rejected(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("account:logout"))
        self.assertEqual(response.status_code, 405)

    def test_logout_post_request_succeeds(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("account:logout"))
        self.assertEqual(response.status_code, 302)


class WishlistDetailViewTests(TestCase):
    def setUp(self):
        self.user = Account.objects.create_user(
            username="user_no_wishlist",
            email="no_wishlist@example.com",
            password="password123",
        )

    def test_wishlist_detail_creates_wishlist_if_not_exists(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("account:wishlist_detail"))
        self.assertEqual(response.status_code, 200)

    def test_transfer_to_cart_creates_cart_if_not_exists(self):
        from account.models import Wishlist
        from shop.models import Collection, Product
        from cart.models import Cart

        wishlist = Wishlist.objects.create(account=self.user)
        col = Collection.objects.create(name="Col")
        prod = Product.objects.create(name="Prod", price_in_cents=100, collection=col)
        wishlist.add(prod)

        Cart.objects.filter(account=self.user).delete()

        self.client.force_login(self.user)
        response = self.client.post(reverse("account:transfer_to_cart", args=[prod.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Cart.objects.filter(account=self.user).exists())
