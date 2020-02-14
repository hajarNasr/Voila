from django.test import TestCase
from django.urls import reverse

class TestProjectsIndexView(TestCase):
    def test_projects_index(self):
        response = self.client.get(reverse("projects:projects_index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects/projects-index.html")