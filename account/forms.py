from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update(
                    {
                        "class": "rounded text-amber-600 focus:ring-amber-500 h-4 w-4 border-gray-300"
                    }
                )
            else:
                field.widget.attrs.update(
                    {
                        "class": "rounded-xl border border-gray-300 px-4 py-3 w-full text-base focus:outline-none focus:ring-2 focus:ring-amber-500"
                    }
                )


class RegistrationForm(StyledFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]


class BillingForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "billing_address_line1",
            "billing_address_line2",
            "billing_city",
            "billing_postal_code",
            "billing_country",
        ]


class ShippingForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "shipping_address_line1",
            "shipping_address_line2",
            "shipping_city",
            "shipping_postal_code",
            "shipping_country",
        ]


class LoginForm(StyledFormMixin, forms.Form):
    username = forms.CharField(label=_("username"))
    password = forms.CharField(label=_("password"), widget=forms.PasswordInput)
