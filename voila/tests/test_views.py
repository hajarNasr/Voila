from django.test import TestCase
from django.urls import reverse
from django.core import mail
from voila.settings import MY_EMAIL as my_email
from voila.forms import ContactForm

class TestPageNotFoundView(TestCase):
    def test_page_not_found_renders_404(self):
        response = self.client.get("doesnt_exist_view")
        self.assertTemplateUsed("404.html")  

class TestBaseView(TestCase):
    def test_base_view_when_get_method(self):
        response = self.client.get(reverse("base_view"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "base.html")
        self.assertTrue(isinstance(response.context["form"], ContactForm))

    def test_sending_email_to_my_email_when_someone_submits_valid_contact_form(self):
        message = "Hey, I am sending this post method to base view just for tests."
        response = self.client.post(reverse("base_view"), {
            "name": "Person",
            "email": "person@email.com",
            "message": message,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Hello")
        self.assertEqual(mail.outbox[0].body, message)
        self.assertEqual(mail.outbox[0].from_email, "person@email.com")
        self.assertEqual(mail.outbox[0].to[0], my_email)
        self.assertTemplateUsed(response, 'thanks-for-your-email.html')
        self.assertEqual(response.context["name"], "Person")
   
