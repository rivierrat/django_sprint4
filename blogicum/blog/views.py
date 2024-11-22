from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from . import settings
from .forms import CommentForm, PostForm
from .mixins import CommentMixin, OnlyAuthorMixin, PostMixin
from .models import Category, Post

User = get_user_model()


def filter_published_posts(requested_posts):
    """Отбор опубликованных постов и сортировка от новых к старым."""
    return requested_posts.select_related(
        'author', 'category', 'location',
    ).filter(is_published=True,
             pub_date__lte=now(),
             category__is_published=True,).order_by('-pub_date')


def annotate_comment_count(posts):
    """Аннотирование постов количеством комментариев."""
    return posts.annotate(
        comment_count=Count('comments')
    )


# Отображение контента:
class IndexView(ListView):
    """Вывод последних опубликованных постов. Видно всем."""

    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    paginate_by = settings.POSTS_PER_PAGE
    queryset = filter_published_posts(
        annotate_comment_count(Post.objects.all())
    )


class PostDetailView(LoginRequiredMixin, DetailView):
    """Вывод отдельного поста.

    Выводит страницу поста с комментариями и формой для комментирования.
    Только для залогиненных пользователей. Неопубликованные посты видит
    только автор.
    """

    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        if post.author == self.request.user:
            return post
        else:
            return get_object_or_404(
                filter_published_posts(Post.objects.all()),
                pk=self.kwargs.get('post_id')
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class CategoryView(ListView):
    """Отображение постов в категории. Видно всем."""

    model = Category
    template_name = 'blog/index.html'
    ordering = 'id'
    paginate_by = settings.POSTS_PER_PAGE

    @staticmethod
    def get_category(self):
        return get_object_or_404(Category.objects.filter(
            is_published=True),
            slug=self.kwargs['category_slug']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category(self)
        return context

    def get_queryset(self):
        category = self.get_category(self)
        return filter_published_posts(
            annotate_comment_count(category.posts).select_related(
                'category',
                'location',
                'author',
            )).filter(category__slug=self.kwargs['category_slug'])


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание нового поста. Только для залогиненных пользователей."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostUpdateView(PostMixin, UpdateView):
    """Редактирование поста. Только для автора."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.get_object())
        return context

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'post_id': self.object.pk}
        )


class PostDeleteView(PostMixin, DeleteView):
    """Удаление поста. Только для автора."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # показываем удаляемый пост:
        context['form'] = PostForm(instance=self.get_object())
        return context


# Работа с профилем пользователя:
class ProfileView(ListView):
    """Отображение профиля пользователя."""

    model = User
    template_name = 'blog/profile.html'
    ordering = 'id'
    paginate_by = settings.POSTS_PER_PAGE

    @staticmethod
    def get_profile(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_profile(self)
        return context

    def get_queryset(self):
        posts = self.get_profile(self).posts
        if self.request.user.username != self.kwargs['username']:
            posts = filter_published_posts(posts)
        return annotate_comment_count(posts).order_by('-pub_date')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ('username', 'first_name', 'last_name', 'email')

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


# Работа с комментариями:
class CommentCreateView(CommentMixin, CreateView):

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentUpdateView(CommentMixin, OnlyAuthorMixin, UpdateView):
    pass


class CommentDeleteView(CommentMixin, OnlyAuthorMixin, DeleteView):
    pass
