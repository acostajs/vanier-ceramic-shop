from django.contrib.auth.models import AbstractUser
from django.db import models
from shop.models import Product
from django.utils.translation import gettext_lazy as _


class Account(AbstractUser):
    """Represents a User Account."""

    billing_address_line1 = models.CharField(
        _("billing_address_line1"), max_length=255, blank=True, null=True
    )
    billing_address_line2 = models.CharField(
        _("billing_address_line2"), max_length=255, blank=True, null=True
    )
    billing_city = models.CharField(
        _("billing_city"), max_length=100, blank=True, null=True
    )
    billing_postal_code = models.CharField(
        _("billing_postal_code"), max_length=20, blank=True, null=True
    )
    billing_country = models.CharField(
        _("billing_country"), max_length=100, blank=True, null=True
    )

    shipping_address_line1 = models.CharField(
        _("shipping_address_line1"), max_length=255, blank=True, null=True
    )
    shipping_address_line2 = models.CharField(
        _("shipping_address_line2"), max_length=255, blank=True, null=True
    )
    shipping_city = models.CharField(
        _("shipping_city"), max_length=100, blank=True, null=True
    )
    shipping_postal_code = models.CharField(
        _("shipping_postal_code"), max_length=20, blank=True, null=True
    )
    shipping_country = models.CharField(
        _("shipping_country"), max_length=100, blank=True, null=True
    )

    def __str__(self):
        return self.username


class Wishlist(models.Model):
    """Represents a Wishlist where Account can add items."""

    product = models.ManyToManyField(Product, blank=True)
    account = models.OneToOneField(Account, on_delete=models.CASCADE)

    def add(self, product: Product):
        """To add a product to the wishlist."""
        self.product.add(product)
        self.save()

    def remove(self, product: Product):
        """To remove a product from the wishlist."""
        self.product.remove(product)
        self.save()

    def clear(self):
        """To clear all products from the wishlist."""
        self.product.clear()
        self.save()

    def count(self):
        """Returns the number of products in the wishlist."""
        return self.product.count()
