from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus as status_code  # Использую согласно допзаданию.

User = get_user_model()


class AboutStaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности статичных адресов."""
        about_pages_urls = ('/about/author/', '/about/tech/')
        for value in about_pages_urls:
            response = self.guest_client.get(value)
            with self.subTest(value=value):
                self.assertEqual(response.status_code, status_code.OK)

    def test_about_url_uses_correct_template(self):
        """Проверка шаблонов для статичных адресов."""
        about_pages_templates = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for value, expected in about_pages_templates.items():
            response = self.guest_client.get(value)
            with self.subTest(value=value):
                self.assertTemplateUsed(
                    response, expected)
