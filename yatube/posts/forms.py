from django.contrib.auth import get_user_model
from django.forms import ModelForm, Select, Textarea

from posts.models import Comment, Post

User = get_user_model()


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

        widgets = {
            'text': Textarea(
                attrs={
                    'name': 'text',
                    'cols': '40',
                    'rows': '10',
                    'class': 'form-control',
                    'required id': 'id_text',
                },
            ),
            'group': Select(
                attrs={
                    'name': 'group',
                    'class': 'form-control',
                    'id': 'id_group',
                },
            ),
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
