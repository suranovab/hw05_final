from django import forms
from .models import Post, Comment
from django.contrib.auth import get_user_model

User = get_user_model()


class PostForm(forms.ModelForm):
    """Форма создания поста."""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': 'Сообщение', 'group': 'Группа'}
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }


class CommentForm(forms.ModelForm):
    """Форма содания комментария."""

    class Meta:
        model = Comment
        fields = ('text',)
