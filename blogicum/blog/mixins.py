from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse

from .forms import CommentForm, PostForm
from .models import Comment, Post


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
        return redirect('blog:post_detail',
                        self.kwargs[self.pk_url_kwarg])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.get_object())
        return context

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class CommentMixin(LoginRequiredMixin):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
    form_class = CommentForm

    def get_success_url(self):
        return reverse('blog:post_detail',
                       args=[self.kwargs['post_id']])
