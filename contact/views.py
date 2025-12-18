from django.shortcuts import render, redirect
from django.core.mail import send_mail
from .forms import ContactForm
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST


def contact(request):
    form = ContactForm()
    context = {"form": form}
    return render(request, "contact/contact_form.html", context)


@require_POST
def contact_submit(request):
    form = ContactForm(request.POST)
    if not form.is_valid():
        return redirect("contact:contact")

    form.save()
    data = form.cleaned_data
    send_mail(
        subject="Contact confirmation",
        message=(
            f"Hi {data['name']}, thank you for contacting us.\n"
            f"We will get back to you soon."
        ),
        from_email="from@example.com",
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
