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
