from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.views import redirect_to_login
from django.test import Client, TestCase
from django.urls import reverse
from faker import Faker
from mixer.backend.django import mixer
from requests import request

from posts.models import Comment, Follow, Post
from posts.tests.common import image

User = get_user_model()
fake = Faker()


class PostFormTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user_author = mixer.blend(User)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user_author)

    def test_create_post_form(self):
        """Валидная форма создает запись в Post."""
        group = mixer.blend('posts.Group')
        data = {'text': fake.text(), 'group': group.pk, 'image': image()}
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user_author}),
        )
        self.assertTrue(Post.objects.filter(text=data['text']))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_form(self):
        """Форма при редактирование поста изменяет существующий пост."""
        group = mixer.blend('posts.Group')
        post = Post.objects.create(
            author=self.user_author,
            text=fake.text(),
            group=group,
        )
        group_two = mixer.blend('posts.Group')
        data = {
            'text': fake.text(),
            'group': group_two.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'pk': post.pk}),
            data=data,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'pk': post.pk}),
        )
        modified_post = Post.objects.get(pk=post.pk)
        self.assertEqual(modified_post.text, data['text'])
        self.assertEqual(modified_post.author, post.author)
        self.assertEqual(modified_post.group, group_two)

    def test_create_post_by_unauthorized_user(self):
        """Неавторизованный пользователь не может создать пост."""
        data = {
            'text': fake.text(),
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=data,
            follow=True,
        )
        self.assertRedirects(
            response, redirect_to_login(reverse('posts:post_create')).url
        )
        self.assertFalse(Post.objects.filter(text=data['text']))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_by_unauthorized_user(self):
        """Неавторизованный пользователь не может редактировать пост."""
        post = mixer.blend(
            'posts.Post',
            author=self.user_author,
        )
        data = {
            'text': fake.text(),
        }
        response = self.client.post(
            reverse('posts:post_edit', kwargs={'pk': post.pk}),
            data=data,
        )
        self.assertRedirects(
            response,
            redirect_to_login(
                reverse('posts:post_edit', kwargs={'pk': post.pk})
            ).url,
        )
        self.assertFalse(Post.objects.filter(text=data['text']))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_edit_post_by_non_author(self):
        """Не автор поста не может редактировать пост."""
        post = mixer.blend(
            'posts.Post',
            author=self.user_author,
        )
        data = {
            'author': mixer.blend(User),
            'text': fake.text(),
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'pk': post.pk}),
            data=data,
        )
        self.assertRedirects(
            response, reverse('posts:post_detail', kwargs={'pk': post.pk})
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_create_comment_by_unauthorized_user(self):
        """Неавторизованный пользователь не может оставлять комментарии."""
        post = mixer.blend('posts.Post')
        data = {
            'text': fake.text(),
        }

        response = self.client.post(
            reverse('posts:add_comment', kwargs={'pk': post.pk}),
            data=data,
            follow=True,
        )
        self.assertFalse(Comment.objects.filter(text=data['text']))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_comment_by_anonymous_user(self):
        """Анонимный пользователь не может оставлять комментарии."""
        post = mixer.blend('posts.Post')
        client = Client()
        request.user = AnonymousUser()
        request.session = {}
        data = {
            'text': fake.text(),
        }
        response = client.post(
            reverse('posts:add_comment', kwargs={'pk': post.pk}),
            data=data,
            follow=True,
        )
        self.assertFalse(Comment.objects.filter(text=data['text']))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_comment(self):
        """После добавления комментария, он появляется на странице поста."""
        post = mixer.blend('posts.Post')
        data = {
            'text': fake.text(),
            'author': self.user_author,
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'pk': post.pk}),
            data=data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'pk': post.pk}),
        )
        self.assertTrue(Comment.objects.filter(text=data['text']))
        self.assertEqual(response.status_code, HTTPStatus.OK)


class FollowingTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.authorized_follower, cls.author_following = mixer.cycle(2).blend(
            User,
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.authorized_follower)
        cls.post = mixer.blend(
            'posts.Post',
            author=cls.author_following,
        )

    def test_user_cannot_follow_himself(self):
        """Пользователь не может подписываться сам на себя."""
        authorized_client = Client()
        authorized_client.force_login(self.author_following)
        authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author_following},
            ),
        )
        self.assertFalse(
            Follow.objects.filter(
                author=self.author_following,
                user=self.author_following,
            ).exists()
        )

    def test_user_cannot_resubscribe(self):
        """Пользователь не может подписаться повторно на одного автора."""
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author_following},
            ),
        )
        subscription = Follow.objects.get(
            user=self.authorized_follower,
            author=self.author_following,
        )
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author_following},
            ),
        )
        self.assertNotEqual(
            Follow.objects.get(
                user=self.authorized_follower,
                author=self.author_following,
            ).pk,
            subscription.pk + 1,
        )

    def test_anonymous_user_cannot_follow_author(self):
        """Анонимный пользователь не может подписаться на автора."""
        client = Client()
        request.user = AnonymousUser()
        request.session = {}
        client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author_following},
            ),
        )
        self.assertFalse(
            Follow.objects.filter(
                user=None,
                author=self.author_following,
            ).exists()
        )

    def test_user_cannot_subscribe_to_anonymous(self):
        """Пользователь не может подписаться на анонима."""
        data = {
            'text': fake.text,
        }
        self.client.post(
            reverse('posts:post_create'),
            data=data,
            follow=True,
        )
        post = Post.objects.filter(text=data['text'])
        if post.exists():
            self.authorized_client.get(
                reverse(
                    'posts:profile_follow',
                    kwargs={'username': post.author},
                ),
            )
            self.assertTrue(
                Follow.objects.filter(
                    author=post.author,
                    user=self.authorized_follower,
                ).exists()
            )
        self.assertFalse(
            Post.objects.filter(
                text=data['text'],
            ).exists()
        )
