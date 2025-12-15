from django.test import TestCase
from .models import Product, Collection
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
import datetime


class CollectionModelTests(TestCase):
    def setUp(self):
        """To set up collection examples to be able to test."""
        image = SimpleUploadedFile(
            name="test_image.jpg", content=b"", content_type="image/jpeg"
        )
        self.collection = Collection.objects.create(
            name="Vase Collection",
            description="A selection of handcrafted ceramic vases.",
            image=image,
            ceramic_type="Furnace Burned",
        )

    def test_collection_fields(self):
        """Fields should store and retrieve values correctly."""
        collection = self.collection
        self.assertEqual(collection.name, "Vase Collection")
        self.assertEqual(
            collection.description, "A selection of handcrafted ceramic vases."
        )
        self.assertTrue(collection.image)
        self.assertEqual(collection.ceramic_type, "Furnace Burned")


class ProductModelTests(TestCase):
    def setUp(self):
        """To set up different ceramic pieces to be able to test."""
        image = SimpleUploadedFile(
            name="test_image.jpg", content=b"", content_type="image/jpeg"
        )
        self.collection = Collection.objects.create(
            name="Mug Collection",
            description="Hand-thrown ceramic mugs for everyday use.",
            image=image,
            ceramic_type="Furnace Burned",
        )
        now = timezone.now()
        self.prod1 = Product.objects.create(
            name="Sunrise Mug",
            description="Stoneware mug with sunrise glaze.",
            quantity=10,
            image="sunrise_mug.png",
            price_in_cents=12000,
            created_date=now - datetime.timedelta(days=60),
            collection=self.collection,
            discount_percentage=10,
        )
        self.prod2 = Product.objects.create(
            name="Ocean Bowl",
            description="Serving bowl with ocean-blue glaze.",
            quantity=0,
            image="ocean_bowl.png",
            price_in_cents=1999,
            created_date=now - datetime.timedelta(days=2),
            collection=self.collection,
            discount_percentage=0,
        )
        self.prod3 = Product.objects.create(
            name="Mini Planter",
            description="Small planter for succulents.",
            quantity=5,
            image="mini_planter.png",
            price_in_cents=500,
            created_date=now,
            collection=self.collection,
            discount_percentage=20,
        )

    def test_is_available(self):
        """Should return True if the product is available, False if it is not available."""
        self.assertTrue(self.prod1.is_available)
        self.assertFalse(self.prod2.is_available)

    def test_price_in_dollars(self):
        """Should return True if the conversion of the price in cents to dollars is working correctly."""
        self.assertEqual(self.prod1.price_in_dollars, "$120.00")
        self.assertEqual(self.prod2.price_in_dollars, "$19.99")

    def test_discounted_price_in_dollars(self):
        """Should return True if the discount is applied to the price."""
        self.assertEqual(self.prod1.discounted_price_in_dollars, "$108.00")
        self.assertEqual(self.prod2.discounted_price_in_dollars, "$19.99")
        self.assertEqual(self.prod3.discounted_price_in_dollars, "$4.00")

    def test_get_discounted_price(self):
        """Should return True if it is properly getting the discounted price in cents."""
        self.assertEqual(self.prod1.get_discounted_price(), 10800)
        self.assertEqual(self.prod2.get_discounted_price(), 1999)
        self.assertEqual(self.prod3.get_discounted_price(), 400)

    def test_created_recently(self):
        """Should return True if the product was created recently, False otherwise."""
        self.assertTrue(self.prod3.created_recently)
        self.assertFalse(self.prod1.created_recently)
