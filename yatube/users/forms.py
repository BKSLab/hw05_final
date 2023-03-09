from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

        labels = {
            'first_name': ('имя'),
            'last_name': ('Фамилия'),
            'username': ('имя пользователя'),
            'email': ('почта'),
        }
        help_texts = {
            'first_name': ('введите ваше имя'),
            'last_name': ('введите вашу фамилию'),
            'username': ('уникальное имя пользователя'),
            'email': ('адрес электронной почты'),
        }
