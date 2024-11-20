from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from . import settings
from .forms import CommentForm, PostForm
from .models import Category, Comment, Post
from .mixins import OnlyAuthorMixin, PostMixin, CommentMixin

User = get_user_model()


# Отображение контента:
class IndexView(ListView):
    """Вывод последних опубликованных постов. Видно всем."""

    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    paginate_by = settings.POSTS_PER_PAGE
    queryset = Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=now(),
    ).annotate(comment_count=Count('comments')).order_by('-pub_date')


class PostDetailView(LoginRequiredMixin, DetailView):
    """Вывод отдельного поста.

    Выводит страницу поста с комментариями и формой для комментирования.
    Только для залогиненных пользователей. Неопубликованные посты видит
    только автор.
    """

    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.filter(post=self.object)
        return context

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        if post.author == self.request.user:
            return post
        else:
            return get_object_or_404(
                Post.objects.filter(is_published=True,
                                    pub_date__lte=now(),
                                    category__is_published=True,),
                pk=self.kwargs.get('post_id')
            )


class CategoryView(ListView):
    """Отображение постов в категории. Видно всем."""

    model = Category
    template_name = 'blog/index.html'
    ordering = 'id'
    paginate_by = settings.POSTS_PER_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category.objects.filter(is_published=True),
            slug=self.kwargs['category_slug']
        )
        return context

    def get_queryset(self):
        return Post.objects.select_related(
            'category',
            'location',
            'author',
        ).filter(
            is_published=True, pub_date__lte=now(),
            category__slug=self.kwargs['category_slug']
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        return context

    def get_queryset(self):
        return Post.objects.filter(
            author__username=self.kwargs['username']
        ).select_related(
            'location', 'category', 'author'
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ['username', 'first_name', 'last_name', 'email']

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


# Работа с комментариями:
class CommentCreateView(LoginRequiredMixin, CreateView):
    post_instance = None
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=kwargs.get('post_id'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.post_instance.pk})


class CommentUpdateView(CommentMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(CommentMixin, DeleteView):
    pass
