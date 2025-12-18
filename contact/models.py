from django.db import models
from django.utils.translation import gettext_lazy as _


class ContactMessage(models.Model):
    """Stores a contact form submission."""

    name = models.CharField(_("name"), max_length=100)
    email = models.EmailField(_("email"))
    subject = models.CharField(_("subject"), max_length=200, blank=True)
    message = models.TextField(_("message"))
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} <{self.email}> - {self.subject}"
