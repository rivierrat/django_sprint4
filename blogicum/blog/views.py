from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from . import settings
from .forms import CommentForm, PostForm
from .mixins import CommentMixin, OnlyAuthorMixin, PostMixin
from .models import Category, Post, User
from .services.post_utils import annotate_comment_count
from .services.post_utils import filter_published_posts


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

    def get_object(self, post_query=None):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        if post.author == self.request.user:
            return post
        return get_object_or_404(filter_published_posts(Post.objects.all()),
                                 pk=self.kwargs.get('post_id'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class CategoryView(ListView):
    """Отображение постов в категории. Видно всем."""

    model = Category
    template_name = 'blog/index.html'
    paginate_by = settings.POSTS_PER_PAGE

    def get_category(self):
        return get_object_or_404(
            Category,
            is_published=True,
            slug=self.kwargs['category_slug']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context

    def get_queryset(self):
        category = self.get_category()
        return filter_published_posts(
            annotate_comment_count(category.posts)
            )


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
            'blog:profile', args=[self.request.user.username]
        )


class PostUpdateView(PostMixin, UpdateView):
    """Редактирование поста. Только для автора."""

    def get_success_url(self):
        return reverse('blog:post_detail',
                       args=(self.kwargs[self.pk_url_kwarg],))


class PostDeleteView(PostMixin, DeleteView):
    """Удаление поста. Только для автора."""


# Работа с профилем пользователя:
class ProfileView(ListView):
    """Отображение профиля пользователя.

    Владелец видит в своём профиле все посты. Другиие пользователи видят
    только опубликованные посты из опубликованных категорий.
    """

    model = User
    template_name = 'blog/profile.html'
    paginate_by = settings.POSTS_PER_PAGE

    def get_author(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_author()
        return context

    def get_queryset(self):
        author = self.get_author()
        posts = annotate_comment_count(author.posts)
        if self.request.user != author:
            posts = filter_published_posts(posts)
        return posts


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля пользователя."""

    model = User
    template_name = 'blog/user.html'
    fields = ('username', 'first_name', 'last_name', 'email')

    def get_object(self, user_query=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


# Работа с комментариями:
class CommentCreateView(CommentMixin, CreateView):
    """Создание комментария. Только для зарегистрированных пользователей."""

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentUpdateView(CommentMixin, OnlyAuthorMixin, UpdateView):
    """Изменение комментария. Только для автора."""


class CommentDeleteView(CommentMixin, OnlyAuthorMixin, DeleteView):
    """Удаление комментария. Только для автора."""
