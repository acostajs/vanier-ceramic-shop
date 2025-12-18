from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class RegistrationForm(UserCreationForm):
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


class BillingForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "billing_address_line1",
            "billing_address_line2",
            "shipping_city",
            "billing_postal_code",
            "billing_country",
        ]


class ShippingForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "shipping_address_line1",
            "shipping_address_line2",
            "shipping_city",
            "shipping_postal_code",
            "shipping_country",
        ]


class LoginForm(forms.Form):
    username = forms.CharField(label=_("username"))
    password = forms.CharField(label=_("password"), widget=forms.PasswordInput)
