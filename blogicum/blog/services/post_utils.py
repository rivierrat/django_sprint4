"""Вспомогательные функции для обработки постов."""
from django.db.models import Count
from django.utils.timezone import now


def filter_published_posts(posts):
    """Отбор только опубликованных постов."""
    return posts.filter(
        is_published=True,
        pub_date__lte=now(),
        category__is_published=True,)


def annotate_comment_count(posts):
    """Аннотирование постов количеством комментариев и сортировка по дате."""
    return posts.select_related(
        'author', 'category', 'location',
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
