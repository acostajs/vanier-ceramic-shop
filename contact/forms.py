from django import forms
from .models import ContactMessage
from main.mixins import StyledFormMixin


class ContactForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
