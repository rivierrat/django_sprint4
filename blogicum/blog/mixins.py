from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from .models import Category, Comment, Post
from .forms import CommentForm, PostForm
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.db.models import Count


class OnlyAuthorMixin(UserPassesTestMixin):
    """Даёт доступ к контенту только его автору."""

    def test_func(self):
        return self.get_object().author == self.request.user


class PostMixin(OnlyAuthorMixin, LoginRequiredMixin):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    form_class = PostForm

    def handle_no_permission(self):
        # instance = get_object_or_404(Post, pk=kwargs.get('post_id'),)
        # if instance.author != request.user:
        return redirect('blog:post_detail', self.kwargs.get('post_id'))
        # return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.filter(post=self.object)
        return context

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class CommentMixin (LoginRequiredMixin):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, id=kwargs['comment_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.object.post.id})
