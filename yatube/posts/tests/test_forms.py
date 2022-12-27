import shutil
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from http import HTTPStatus

from ..models import Post, Group, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
        )
        cls.url_post_create = reverse('posts:post_create')
        cls.url_post_update = reverse(
            'posts:post_update',
            kwargs={'post_id': 1},
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test-user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded_image = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )

    def test_create_post(self):
        form_data = {
            'text': 'Тестовый текст формы',
            'group': self.test_group.id,
            'image': self.uploaded_image
        }
        response = self.authorized_client.post(self.url_post_create,
                                               data=form_data, follow=True)
        post = Post.objects.last()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(1, Post.objects.count())
        self.assertEqual(post.text, 'Тестовый текст формы')
        self.assertEqual(post.author.username, 'test-user')
        self.assertEqual(post.group.title, 'Тестовая группа')
        self.assertTrue(post.image)

    def test_edit_post(self):
        post = Post.objects.create(
            text='Изначальный текст!!!',
            author=self.user,
            group=self.test_group
        )
        group = Group.objects.create(
            title='Изменённая тестовая группа',
            slug='second-test-slug',
        )
        form_data = {
            'text': 'Изменённый текст',
            'group': group.id,
            'image': self.uploaded_image,
        }
        response = self.authorized_client.post(
            self.url_post_update,
            data=form_data,
            follow=True,
        )
        edited_post = Post.objects.last()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(post.text, edited_post.text)
        self.assertEqual(edited_post.text, 'Изменённый текст')
        self.assertEqual(edited_post.group.title, 'Изменённая тестовая группа')
        self.assertEqual(edited_post.group.slug, 'second-test-slug')
        self.assertTrue(edited_post.image)

    def test_clean_text(self):
        form_data = {
            'text': 'Тест',
        }
        response = self.authorized_client.post(
            self.url_post_create,
            data=form_data,
        )
        self.assertEqual(0, Post.objects.count())
        self.assertFormError(
            response,
            'form',
            'text',
            'Текст публикации не может быть короче 10 символов.'
        )


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_author = User.objects.create_user(
            username='test-author',
        )
        cls.test_post = Post.objects.create(
            text='Тестовый текст комментируемого поста',
            author=cls.test_author
        )
        cls.url_add_comment = reverse(
            'posts:add_comment',
            kwargs={'post_id': cls.test_post.id}
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test-user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_add_comment(self):
        form_data = {
            'text': 'Это тестовый комментарий'
        }
        response = self.authorized_client.post(
            self.url_add_comment,
            data=form_data,
            follow=True,
        )
        comment = self.test_post.comments.last()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(comment.text, 'Это тестовый комментарий')

    def test_clean_text(self):
        form_data = {
            'text': 'Тест',
        }
        response = self.authorized_client.post(
            self.url_add_comment,
            data=form_data,
        )
        self.assertEqual(0, Comment.objects.count())
        self.assertFormError(
            response,
            'form',
            'text',
            'Текст комментария не может быть короче 10 символов.'
        )
