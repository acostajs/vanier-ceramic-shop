import pytest
from django.urls import reverse
from django.test import Client
from contact.models import ContactMessage


@pytest.mark.django_db
def test_create_contact_message_minimal() -> None:
    """Test creating a ContactMessage with minimal details."""
    msg = ContactMessage.objects.create(
        name="Juan",
        email="juan@example.com",
        subject="Order Question",
        message="A quick query.",
    )
    assert msg.name == "Juan"
    assert msg.email == "juan@example.com"
    assert msg.subject == "Order Question"
    assert msg.message == "A quick query."
    assert msg.is_resolved is False


@pytest.mark.django_db
def test_subject_can_be_blank_and_str() -> None:
    """Test message representation when subject is blank."""
    msg = ContactMessage.objects.create(
        name="Laura", email="laura@example.com", subject="", message="Hello."
    )
    assert msg.subject == ""
    assert str(msg) == "Laura <laura@example.com> - "


def test_contact_page_renders_form(client: Client) -> None:
    """Test GET request to contact page renders the contact form."""
    response = client.get(reverse("contact:contact"))
    assert response.status_code == 200
    assert b"<form" in response.content
    assert "form" in response.context


@pytest.mark.django_db
def test_contact_submit_valid_data(client: Client) -> None:
    """Test valid contact form submission redirects and creates a message."""
    post_data = {
        "name": "Melissa",
        "email": "melissa@example.com",
        "subject": "Support",
        "message": "Need help with order.",
    }
    response = client.post(reverse("contact:contact_submit"), post_data)
    assert response.status_code == 302
    assert response.url == reverse("home")
    assert ContactMessage.objects.count() == 1
    msg = ContactMessage.objects.first()
    assert msg is not None
    assert msg.name == "Melissa"
    assert msg.email == "melissa@example.com"


@pytest.mark.django_db
def test_contact_submit_invalid_data(client: Client) -> None:
    """Test invalid form submission shows errors and does not create a message."""
    post_data = {
        "name": "Melissa",
        "email": "invalid-email",
        "subject": "Support",
        "message": "",
    }
    response = client.post(reverse("contact:contact_submit"), post_data)
    assert response.status_code == 200
    assert "form" in response.context
    form = response.context["form"]
    assert form.is_valid() is False
    assert "email" in form.errors
    assert "message" in form.errors
    assert ContactMessage.objects.count() == 0
