from django.test import TestCase
from voila.forms import ContactForm     

class TestContactForm(TestCase):
    def test_contact_form_is_valid_when_valid_data(self):
        contact_form = ContactForm({"name":"Person", "email":"person@email.com", "message":"I am a message in the contact form."})

        self.assertTrue(contact_form.is_valid())
        self.assertEqual(contact_form.cleaned_data["name"], "Person")
        self.assertEqual(contact_form.cleaned_data["email"],"person@email.com")
        self.assertEqual(contact_form.cleaned_data["message"], "I am a message in the contact form.")

    def test_contact_form_is_not_valid_when_blank_data(self):
        contact_form = ContactForm({})
        self.assertFalse(contact_form.is_valid())

        self.assertEqual(contact_form.errors, {
            "name": ["This field is required."],
            "email": ["This field is required."],
            "message": ["This field is required."],
        })

        contact_form = ContactForm({"name":"Person"})
        self.assertFalse(contact_form.is_valid()) 
        self.assertEqual(contact_form.errors, {
            "email": ["This field is required."],
            "message": ["This field is required."],
        })

        contact_form = ContactForm({"name":"Person", "email": "person@email.com"})
        self.assertFalse(contact_form.is_valid()) 
        self.assertEqual(contact_form.errors, {
            "message": ["This field is required."],
        })