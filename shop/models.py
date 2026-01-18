from django.db import models
from django.utils import timezone
import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class Collection(models.Model):
    """Represents a Collection of Products."""

    name = models.CharField(_("name"), max_length=100)
    description = models.TextField(_("description"))
    image = models.ImageField(_("image"), upload_to="collections/")
    ceramic_type = models.CharField(_("ceramic type"), max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Represents a single Product."""

    name = models.CharField(_("name"), max_length=200)
    description = models.TextField(_("description"))
    quantity = models.IntegerField(_("quantity"), default=0)
    image = models.ImageField(_("image"), upload_to="products/")
    price_in_cents = models.IntegerField(_("price"), default=0)
    created_date = models.DateTimeField(default=timezone.now)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
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

    def discount_from_quantity(self, quantity):
        """To discount from the inventory of the product."""
        if quantity <= 0:
            raise ValidationError("Quantity must be positive.")
        if self.quantity >= quantity:
            self.quantity -= quantity
            self.save(update_fields=["quantity"])
        else:
            raise ValidationError(
                "Not enough quantity available to complete this operation."
            )
