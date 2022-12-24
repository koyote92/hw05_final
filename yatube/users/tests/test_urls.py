from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus as status_code  # Использую согласно допзаданию.

User = get_user_model()


class UsersURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test-user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_public_pages_url_exists_at_desired_location(self):
        """Проверка доступа к общедоступным страницам."""
        public_pages_urls = (
            '/auth/signup/',
            '/auth/login/',
            '/auth/password_reset/',
        )
        for item in public_pages_urls:
            response = self.guest_client.get(item)
            with self.subTest(item=item):
                self.assertEqual(response.status_code, status_code.OK)

    def test_public_pages_url_uses_correct_template(self):
        """Проверка шаблонов для общедоступных адресов."""
        public_pages_templates = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
        }
        for value, expected in public_pages_templates.items():
            response = self.guest_client.get(value)
            with self.subTest(value=value):
                self.assertTemplateUsed(response, expected)

    def test_authorized_pages_url_exists_at_desired_location(self):
        """Проверка доступа к страницам с использованием авторизации
        (все пользователи)."""
        authorized_pages_urls = (
            '/auth/signup/',
            '/auth/login/',
            '/auth/password_change/',
            '/auth/password_change/done/',
            '/auth/password_reset/',
            '/auth/password_reset/done/',
            '/auth/password_reset/complete/',
            '/auth/logout/',
        )
        for item in authorized_pages_urls:
            response = self.authorized_client.get(item)
            with self.subTest(item=item):
                self.assertEqual(response.status_code, status_code.OK)

    def test_authorized_pages_url_uses_correct_template(self):
        """Проверка доступа к страницам с использованием авторизации
        (все пользователи)."""
        authorized_pages_templates = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/password_reset/complete/':
                'users/password_reset_complete.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        for value, expected in authorized_pages_templates.items():
            response = self.authorized_client.get(value)
            with self.subTest(value=value):
                self.assertTemplateUsed(response, expected)

    def test_authorized_pages_url_redirects_unauthorized(self):
        """Проверка редиректов неавторизованных пользователей со страниц,
        доступных только авторизованным пользователям."""
        auth_pages_urls_redirects_unauthorized = {
            '/auth/password_change/':
                '/auth/login/?next=/auth/password_change/',
            '/auth/password_change/done/':
                '/auth/login/?next=/auth/password_change/done/',
            '/auth/password_reset/done/':
                '/auth/login/?next=/auth/password_reset/done/',
            '/auth/password_reset/complete/':
                '/auth/login/?next=/auth/password_reset/complete/',
        }
        for value, expected in auth_pages_urls_redirects_unauthorized.items():
            response = self.guest_client.get(value)
            with self.subTest(value=value):
                self.assertRedirects(response, expected)
