from django import forms
from .models import ContactMessage


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


class ContactForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
