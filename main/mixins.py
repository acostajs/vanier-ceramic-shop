from django import forms


class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update(
                    {
                        "class": "rounded-xs text-primary focus:ring-primary h-4 w-4 border-hairline bg-canvas"
                    }
                )
            else:
                field.widget.attrs.update(
                    {
                        "class": "rounded-sm border border-hairline bg-canvas text-ink px-4 py-3 w-full text-base focus:outline-none focus:ring-1 focus:ring-primary"
                    }
                )
