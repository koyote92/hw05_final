from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.constraints import UniqueConstraint

from . import constants


User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Группа',
        help_text='Название группы',
    )
    slug = models.SlugField(
        max_length=30,
        unique=True,
        verbose_name='Короткий адрес',
        help_text='Короткий идентификатор группы',
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Текстовое описание группы',
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Текстовое содержимое публикации',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        help_text='Дата публикации поста',
        db_index=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
        help_text='Имя создателя публикации',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Имя группы для публикаций',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.text[:constants.SELF_TEXT_LENGTH]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(
        verbose_name='Текст',
        help_text='Текст комментария',  # Это в форме участвует.
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата комментария',
    )

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.text[:constants.SELF_TEXT_LENGTH]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'author'], name='follow')
        ]
