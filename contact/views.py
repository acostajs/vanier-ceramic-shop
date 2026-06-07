from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .forms import ContactForm
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.conf import settings
from django.http import HttpRequest, HttpResponse


def contact(request: HttpRequest) -> HttpResponse:
    form = ContactForm()
    context = {"form": form}
    return render(request, "contact/contact_form.html", context)


@require_POST
def contact_submit(request: HttpRequest) -> HttpResponse:
    form = ContactForm(request.POST)
    if not form.is_valid():
        return render(request, "contact/contact_form.html", {"form": form})

    form.save()
    data = form.cleaned_data
    send_mail(
        subject="Contact confirmation",
        message=(
            f"Hi {data['name']}, thank you for contacting us.\n"
            f"We will get back to you soon."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[data["email"]],
        fail_silently=False,
    )
    msg_template = _(
        "Thank you for reaching out %(name)s! We'll get back to you at %(email)s."
    )

    messages.success(
        request, msg_template % {"name": data["name"], "email": data["email"]}
    )

    return redirect("home")
