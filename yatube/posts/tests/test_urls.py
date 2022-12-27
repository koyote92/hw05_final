from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache
from http import HTTPStatus

from ..models import Post, Group, Comment

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.test_author = User.objects.create_user(
            username='test-author',
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.test_author)
        cls.test_post = Post.objects.create(
            text='Тестовый текст',
            group=cls.test_group,
            author=cls.test_author,
        )
        cls.url_index = '/'
        cls.url_group = f'/group/{cls.test_group.slug}/'
        cls.url_profile = f'/profile/{cls.test_author.username}/'
        cls.url_post_details = f'/posts/{cls.test_post.id}/'
        cls.url_post_create = '/create/'
        cls.url_post_update = f'/posts/{cls.test_post.id}/edit/'
        cls.url_post_delete = f'/posts/{cls.test_post.id}/delete/'
        cls.url_add_comment = f'/posts/{cls.test_post.id}/comment/'
        cls.url_follow = '/follow/'
        cls.url_profile_follow = f'/profile/{cls.test_author.username}/follow/'
        cls.url_profile_unfollow = (
            f'/profile/{cls.test_author.username}/unfollow/'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test-user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.test_comment = Comment.objects.create(
            text='Текст тестового коммента',
            author=self.user,
            post=self.test_post,
        )
        self.url_comment_delete = (f'/posts/{self.test_post.id}/comment/'
                                   f'{self.test_comment.id}/delete/')

    def test_public_pages_url_exists_at_desired_location(self):
        """Проверка доступа к общедоступным страницам."""
        public_pages_urls = (
            self.url_index,
            self.url_group,
            self.url_profile,
            self.url_post_details,
        )
        for value in public_pages_urls:
            response = self.guest_client.get(value)
            with self.subTest(value=value):
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_public_pages_url_uses_correct_template(self):
        """Проверка шаблонов для общедоступных адресов."""
        public_pages_templates = {
            self.url_index: 'posts/index.html',
            self.url_group: 'posts/group_list.html',
            self.url_profile: 'posts/profile.html',
            self.url_post_details: 'posts/post_details.html',
        }
        for value, expected in public_pages_templates.items():
            cache.clear()
            response = self.guest_client.get(value)
            with self.subTest(value=value):
                self.assertTemplateUsed(
                    response, expected)

    def test_authorized_pages_url_exists_at_desired_location(self):
        """Проверка доступа к страницам с использованием авторизации
        (все пользователи)."""
        authorized_pages_urls = (
            self.url_post_create,
            self.url_add_comment,
            self.url_profile_follow,
            self.url_profile_unfollow,
            self.url_follow,
        )
        for item in authorized_pages_urls:
            response = self.authorized_client.get(item, follow=True)
            with self.subTest(item=item):
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_pages_url_uses_correct_template(self):
        """Проверка шаблонов страниц с использованием авторизации
        (все пользователи)."""
        authorized_pages_templates = {
            self.url_post_create: 'posts/create_post.html',
            self.url_add_comment: 'posts/post_details.html',
            self.url_follow: 'posts/follow.html',
        }
        for value, expected in authorized_pages_templates.items():
            response = self.authorized_client.get(value)
            with self.subTest(value=value):
                self.assertTemplateUsed(response, expected)

    def test_authorized_pages_url_redirects_unauthorized(self):
        """Проверка редиректов неавторизованных пользователей со страниц,
        доступных только авторизованным пользователям."""
        auth_pages_urls_redirects_unauthorized = {
            self.url_post_create: '/auth/login/?next=/create/',
            self.url_post_update:
                f'/auth/login/?next=/posts/{self.test_post.id}/edit/',
            self.url_post_delete:
                f'/auth/login/?next=/posts/{self.test_post.id}/delete/',
            self.url_add_comment:
                f'/auth/login/?next=/posts/{self.test_post.id}/comment/',
            self.url_comment_delete:
                f'/auth/login/?next=/posts/{self.test_post.id}/comment/'
                f'{self.test_comment.id}/delete/'
        }
        for value, expected in auth_pages_urls_redirects_unauthorized.items():
            response = self.guest_client.get(value)
            with self.subTest(value=value):
                self.assertRedirects(response, expected)

    def test_author_pages_url_exists_at_desired_location(self):  # Нужен автор.
        """Проверка доступа к страницам с использованием авторизации (страницы
        автора)."""
        test_author = PostsURLTests.authorized_client
        author_pages_urls = {
            self.url_post_update: '/posts/create_post.html/',
        }
        for value, expected in author_pages_urls.items():
            response = test_author.get(value)
            with self.subTest(value=value):
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_pages_url_uses_correct_template(self):  # Нужен автор.
        """Проверка шаблонов страниц с использованием авторизации (страницы
        автора)."""
        test_author = PostsURLTests.authorized_client
        author_pages_templates = {
            self.url_post_update: 'posts/create_post.html',
        }
        for value, expected in author_pages_templates.items():
            response = test_author.get(value)
            with self.subTest(value=value):
                self.assertTemplateUsed(response, expected)

    def test_authorized_non_author_redirects_on_only_author_actions(self):
        """Проверка редиректа, когда авторизованный пользователь пытается
        редактировать или удалить чужую публикацию."""
        author_only_urls = {
            self.url_post_update: self.url_post_details,
            self.url_post_delete: self.url_post_details,
            self.url_comment_delete: self.url_post_details
        }
        for value, expected in author_only_urls.items():
            response = self.authorized_client.get(value)
            with self.subTest(value=value):
                self.assertRedirects(response, expected)
