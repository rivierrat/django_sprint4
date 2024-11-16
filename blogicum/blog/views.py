from django.shortcuts import get_object_or_404, render
from django.utils.timezone import now

from . import settings

from blog.models import Category, Post


def select_published_posts(requested_posts):
    """Отбор опубликованных постов."""
    return requested_posts.select_related(
        'author',
        'category',
        'location',
    ).filter(
        is_published=True,
        pub_date__lte=now(),
        category__is_published=True,
    )


def index(request):
    """Вывод последних опубликованных постов."""
    return render(request, 'blog/index.html', {
        'post_list': select_published_posts(Post.objects.all(),)
        [:settings.POSTS_ON_MAIN]
    })


def post_detail(request, post_id):
    """Вывод страницы поста.

    Если пост не опубликован или не существует, вернёт 404.
    """
    return render(request, 'blog/detail.html', {
        'post': get_object_or_404(select_published_posts
                                  (Post.objects.all(),), pk=post_id,),
    })


def category_posts(request, category_slug):
    """Вывод постов в категории.

    Показывает записи, опубликованные в выбранной категории. Если запрошенная
    категория не опубликована, вернёт 404.
    """
    category = get_object_or_404(
        Category.objects.all(),
        slug=category_slug,
        is_published=True,
    )

    return render(request, 'blog/category.html', {
        'category': category,
        'post_list': select_published_posts(category.posts,)
    },)
