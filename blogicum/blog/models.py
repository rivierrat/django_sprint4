from django.contrib.auth import get_user_model
from django.db import models

from . import settings


User = get_user_model()


class PublishedCreatedModel(models.Model):
    """Признаки публикации материала.

    Добавляет флаг публикации и время создания контента (поста, категории,
    локации).
    """

    is_published = models.BooleanField(
        verbose_name='Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',
    )

    class Meta:
        abstract = True


class TitleModel(PublishedCreatedModel):
    title = models.CharField(
        max_length=settings.TITLE_MAX_LENGTH,
        verbose_name='Заголовок',
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.title[:settings.TITLE_PREVIEW_LENGTH]


class Post(TitleModel):
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text='Если установить дату и время в будущем — можно '
        'делать отложенные публикации.',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор публикации',
        on_delete=models.CASCADE,
    )
    location = models.ForeignKey(
        'Location',
        verbose_name='Местоположение',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    category = models.ForeignKey(
        'Category',
        verbose_name='Категория',
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)
        default_related_name = 'posts'


class Category(TitleModel):
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text='Идентификатор страницы для URL; разрешены символы '
        'латиницы, цифры, дефис и подчёркивание.',
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Location(PublishedCreatedModel):
    name = models.CharField(
        max_length=settings.LOCATION_MAX_LENGTH,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:settings.LOCATION_PREVIEW_LENGTH]
