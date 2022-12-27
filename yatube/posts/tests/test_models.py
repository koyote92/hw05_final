from django.contrib.auth import get_user_model
from django.test import TestCase

from .. import constants
from ..models import Group, Post, Comment

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(username='auth')
        cls.test_group = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.test_post = Post.objects.create(
            author=cls.test_user,
            text='Тестовый пост и ещё несколько лишних символов для теста',
        )
        cls.test_comment = Comment.objects.create(
            author=cls.test_user,
            text='Тестовый комментарий чуть больше пятнадцати символов',
            post=cls.test_post
        )

    def test_models_have_correct_object_names(self):
        """Проверяем __str__ у моделей Post и Group."""
        post = PostModelTest.test_post
        group = PostModelTest.test_group
        comment = PostModelTest.test_comment
        models_title = {
            str(post): post.text[:constants.SELF_TEXT_LENGTH],
            str(group): group.title,
            str(comment): comment.text[:constants.SELF_TEXT_LENGTH],
        }
        for title, expected in models_title.items():
            with self.subTest():
                self.assertEqual(title, expected)

    def test_post_verbose_names(self):
        """verbose_name в полях модели post совпадает с ожидаемым."""
        post = PostModelTest.test_post
        field_verbose_names = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verbose_names.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_group_verbose_names(self):
        """verbose_name в полях модели group совпадает с ожидаемым."""
        group = PostModelTest.test_group
        field_verbose_names = {
            'title': 'Группа',
            'slug': 'Короткий адрес',
            'description': 'Описание',
        }
        for value, expected in field_verbose_names.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_comment_verbose_names(self):
        """verbose_name в полях модели comment совпадает с ожидаемым."""
        comment = PostModelTest.test_comment
        field_verbose_names = {
            'post': 'Пост',
            'author': 'Автор',
            'text': 'Текст',
            'created': 'Дата комментария',
        }
        for value, expected in field_verbose_names.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).verbose_name, expected)

    def test_post_help_texts(self):
        """help_text в полях модели post совпадает с ожидаемым."""
        post = PostModelTest.test_post
        field_help_texts = {
            'text': 'Текстовое содержимое публикации',
            'pub_date': 'Дата публикации поста',
            'author': 'Имя создателя публикации',
            'group': 'Имя группы для публикаций',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_group_help_texts(self):
        """help_text в полях модели group совпадает с ожидаемым."""
        group = PostModelTest.test_group
        field_help_texts = {
            'title': 'Название группы',
            'slug': 'Короткий идентификатор группы',
            'description': 'Текстовое описание группы',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_comment_help_texts(self):
        """help_text в полях модели comment совпадает с ожидаемым."""
        comment = PostModelTest.test_comment
        field_help_texts = {
            'text': 'Текст комментария',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).help_text, expected)
