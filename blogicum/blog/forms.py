from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Post

# from django.utils.timezone import now, datetime



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

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['pub_date'] = forms.DateField(
    #         required=True,
    #         widget=forms.DateTimeInput(
    #             attrs={'type': 'date', 'style': 'width:200px',
    #                 , }
    #         )
    #     )


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
