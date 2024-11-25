from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from . import settings
from .forms import CommentForm, PostForm
from .mixins import CommentMixin, OnlyAuthorMixin, PostMixin
from .models import Category, Post
from .services.postutils import annotate_comment_count as annotate
from .services.postutils import filter_published_posts as filter_pub


User = get_user_model()


# Отображение контента:
class IndexView(ListView):
    """Вывод последних опубликованных постов. Видно всем."""

    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    paginate_by = settings.POSTS_PER_PAGE
    queryset = filter_pub(annotate(Post.objects.all()))


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
        return get_object_or_404(filter_pub(Post.objects.all()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class CategoryView(ListView):
    """Отображение постов в категории. Видно всем."""

    model = Category
    template_name = 'blog/index.html'
    ordering = '-pub_date'
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
        return filter_pub(annotate(category.posts)).filter(
            category__slug=self.kwargs['category_slug']
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
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostUpdateView(PostMixin, UpdateView):
    """Редактирование поста. Только для автора."""

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', args=[self.kwargs['post_id']])


class PostDeleteView(PostMixin, DeleteView):
    """Удаление поста. Только для автора."""

    pass


# Работа с профилем пользователя:
class ProfileView(ListView):
    """Отображение профиля пользователя."""

    model = User
    template_name = 'blog/profile.html'
    ordering = '-pub_date'
    paginate_by = settings.POSTS_PER_PAGE

    def get_profile(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_profile()
        return context

    def get_queryset(self):
        author = self.get_profile()
        posts = annotate(author.posts)
        if self.request.user != author:
            posts = filter_pub(posts)
        return posts


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
