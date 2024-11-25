from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Post


User = get_user_model()


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={
                'type': 'date',
                'class': 'form-control'},
                format='%Y-%m-%dT%H:%M')
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
