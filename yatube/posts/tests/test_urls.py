from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.test import Client, TestCase
from django.urls import reverse
from mixer.backend.django import mixer

User = get_user_model()


class PostUrlsTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user, cls.user_author = mixer.cycle(2).blend(
            User, username=(name for name in ('user', 'kir'))
        )
        cls.group = mixer.blend('posts.Group')
        cls.post = mixer.blend(
            'posts.Post',
            author=cls.user_author,
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(cls.user_author)
        cls.urls = {
            'create_post': reverse('posts:post_create'),
            'edit_post': reverse(
                'posts:post_edit', kwargs={'pk': cls.post.pk}
            ),
            'group_list': reverse(
                'posts:page_post', kwargs={'slug': cls.group.slug}
            ),
            'index': reverse('posts:h_page'),
            'post_detail': reverse(
                'posts:post_detail', kwargs={'pk': cls.post.pk}
            ),
            'profile': reverse('posts:profile', kwargs={'username': cls.user}),
            'missing': '/unexisting_page/',
        }

    def test_http_statuses(self) -> None:
        """
        В зависимости от уровня прав пользователя
        страница возвращает соответствующий ответ.
        """
        httpstatuses = (
            (self.urls.get('create_post'), HTTPStatus.FOUND, self.client),
            (
                self.urls.get('create_post'),
                HTTPStatus.OK,
                self.authorized_client,
            ),
            (self.urls.get('edit_post'), HTTPStatus.FOUND, self.client),
            (
                self.urls.get('edit_post'),
                HTTPStatus.FOUND,
                self.authorized_client,
            ),
            (
                self.urls.get('edit_post'),
                HTTPStatus.OK,
                self.authorized_client_author,
            ),
            (self.urls.get('group_list'), HTTPStatus.OK, self.client),
            (self.urls.get('index'), HTTPStatus.OK, self.client),
            (self.urls.get('post_detail'), HTTPStatus.OK, self.client),
            (self.urls.get('profile'), HTTPStatus.OK, self.client),
            (self.urls.get('missing'), HTTPStatus.NOT_FOUND, self.client),
        )
        for address_url, status_code, status_client in httpstatuses:
            with self.subTest(address_url=address_url):
                self.assertEqual(
                    status_client.get(address_url).status_code,
                    status_code,
                    f'страница {address_url} недоступна',
                )

    def test_templates(self) -> None:
        """
        URL-адрес использует соответствующий шаблон
        для соответствующего пользователя.
        """
        templates = (
            (
                self.urls.get('create_post'),
                'posts/create_post.html',
                self.authorized_client,
            ),
            (
                self.urls.get('edit_post'),
                'posts/create_post.html',
                self.authorized_client_author,
            ),
            (
                self.urls.get('group_list'),
                'posts/group_list.html',
                self.client,
            ),
            (
                self.urls.get('group_list'),
                'posts/group_list.html',
                self.authorized_client,
            ),
            (self.urls.get('index'), 'posts/index.html', self.client),
            (
                self.urls.get('index'),
                'posts/index.html',
                self.authorized_client,
            ),
            (
                self.urls.get('post_detail'),
                'posts/post_detail.html',
                self.client,
            ),
            (
                self.urls.get('post_detail'),
                'posts/post_detail.html',
                self.authorized_client,
            ),
            (self.urls.get('profile'), 'posts/profile.html', self.client),
            (
                self.urls.get('profile'),
                'posts/profile.html',
                self.authorized_client,
            ),
            (
                self.urls.get('missing'),
                'core/404.html',
                self.client,
            ),
        )
        for address_url, template, status_client in templates:
            with self.subTest(address_url=address_url):
                self.assertTemplateUsed(
                    status_client.get(address_url), template
                )

    def test_redirects(self) -> None:
        """Проверка редиректов."""
        redirects = (
            (
                self.urls.get('create_post'),
                redirect_to_login(reverse('posts:post_create')).url,
                self.client,
            ),
            (
                self.urls.get('edit_post'),
                redirect_to_login(
                    reverse('posts:post_edit', kwargs={'pk': self.post.pk})
                ).url,
                self.client,
            ),
            (
                self.urls.get('edit_post'),
                f'/posts/{self.post.pk}/',
                self.authorized_client,
            ),
        )
        for address_url, redirect_page, status_client in redirects:
            with self.subTest(address_url=address_url):
                self.assertRedirects(
                    status_client.get(address_url), redirect_page
                )
