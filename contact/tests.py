from django.test import TestCase
from .models import ContactMessage


class ContactMessageModelTests(TestCase):
    """To test ContactMessage Model."""

    def test_create_contact_message_minimal(self):
        msg = ContactMessage.objects.create(
            name="Juan",
            email="[email protected]",
            subject="Question about order",
            message="I have a question about my recent order.",
        )

        self.assertEqual(msg.name, "Juan")
        self.assertEqual(msg.email, "[email protected]")
        self.assertEqual(msg.subject, "Question about order")
        self.assertEqual(msg.message, "I have a question about my recent order.")
        self.assertIsNotNone(msg.created_at)
        self.assertFalse(msg.is_resolved)

    def test_subject_can_be_blank(self):
        msg = ContactMessage.objects.create(
            name="Laura",
            email="[email protected]",
            subject="",
            message="Just saying hi.",
        )

        self.assertEqual(msg.subject, "")
        self.assertEqual(
            str(msg),
            "Laura <[email protected]> - ",
        )

    def test_str_representation(self):
        msg = ContactMessage.objects.create(
            name="Melissa",
            email="[email protected]",
            subject="Support",
            message="Help with my account.",
        )

        self.assertEqual(
            str(msg),
            "Melissa <[email protected]> - Support",
        )


class ContactViewTests(TestCase):
    """Test contact app views."""

    def test_contact_page_renders_form(self):
        from django.urls import reverse

        response = self.client.get(reverse("contact:contact"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<form")
        self.assertIn("form", response.context)

    def test_contact_submit_valid_data(self):
        from django.urls import reverse
        from .models import ContactMessage

        post_data = {
            "name": "Juan",
            "email": "juan@example.com",
            "subject": "Test Subject",
            "message": "Test Message content.",
        }
        response = self.client.post(reverse("contact:contact_submit"), post_data)
        self.assertEqual(response.status_code, 302)
        # Check redirect (which redirects to home page)
        self.assertRedirects(response, reverse("home"))

        # Verify ContactMessage is created in database
        self.assertEqual(ContactMessage.objects.count(), 1)
        msg = ContactMessage.objects.first()
        self.assertEqual(msg.name, "Juan")
        self.assertEqual(msg.email, "juan@example.com")

    def test_contact_submit_invalid_data(self):
        from django.urls import reverse
        from .models import ContactMessage

        # Post invalid data (missing required field 'message' and invalid email)
        post_data = {
            "name": "Juan",
            "email": "invalid-email",
            "subject": "Test Subject",
            "message": "",
        }
        response = self.client.post(reverse("contact:contact_submit"), post_data)
        # Check that it returns 200 and renders the form instead of redirecting
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact/contact_form.html")
        self.assertIn("form", response.context)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertIn("message", form.errors)

        # Verify NO ContactMessage is created in database
        self.assertEqual(ContactMessage.objects.count(), 0)
