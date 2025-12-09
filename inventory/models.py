from django.db import models
from django.utils import timezone
import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """Represents a Category of Products."""

    name = models.CharField(_("name"), max_length=100)
    description = models.TextField(_("description"))
    image = models.ImageField(_("image"))

    def __str__(self):
        return self.name


class Product(models.Model):
    """Represents a single Product."""

    name = models.CharField(_("name"), max_length=200)
    description = models.TextField(_("description"))
    quantity = models.IntegerField(_("quantity"), default=0)
    image = models.ImageField(_("image"))
    price_in_cents = models.IntegerField(_("price"), default=0)
    created_date = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    discount_percentage = models.IntegerField(
        _("discount_percentage"),
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    @property
    def is_available(self):
        """To check if the product is available or not."""
        return self.quantity > 0

    @property
    def price_in_dollars(self):
        """Return the cent price in dollars with two decimals."""
        return f"${self.price_in_cents / 100:.2f}"

    def get_discounted_price(self):
        """if there is a discount, return the discounted price"""
        if self.discount_percentage > 0:
            discount_amount = (self.price_in_cents * self.discount_percentage) // 100
            return self.price_in_cents - discount_amount
        return self.price_in_cents

    @property
    def discounted_price_in_dollars(self):
        """Return the price in dollars with the percentage discount applied."""
        discounted = self.get_discounted_price()
        return f"${discounted / 100:.2f}"

    @property
    def created_recently(self):
        """Return if the Product was created recently."""
        return self.created_date >= timezone.now() - datetime.timedelta(days=30)
