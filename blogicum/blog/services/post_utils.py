"""Вспомогательные функции для обработки постов."""
from django.db.models import Count
from django.utils.timezone import now

from blog.models import Post


def filter_published_posts(posts=Post.objects.all()):
    """Отбор только опубликованных постов."""
    return posts.filter(
        is_published=True,
        pub_date__lte=now(),
        category__is_published=True,)


def annotate_comment_count(posts=Post.objects.all()):
    """Аннотирование постов количеством комментариев и сортировка."""
    return posts.select_related(
        'author', 'category', 'location',
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
