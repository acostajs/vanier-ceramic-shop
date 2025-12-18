from django.test import TestCase
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
