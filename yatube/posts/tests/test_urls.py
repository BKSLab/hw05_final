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
        cls.user, cls.user_author = mixer.cycle(2).blend(User)
        cls.group = mixer.blend('posts.Group')
        cls.post = mixer.blend(
            'posts.Post',
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(cls.post.author)
        cls.urls = {
            'comment': reverse(
                'posts:add_comment',
                kwargs={'pk': cls.post.pk},
            ),
            'create_post': reverse('posts:post_create'),
            'edit_post': reverse(
                'posts:post_edit',
                kwargs={'pk': cls.post.pk},
            ),
            'follow': reverse('posts:follow_index'),
            'group_list': reverse(
                'posts:page_post',
                kwargs={'slug': cls.group.slug},
            ),
            'index': reverse('posts:h_page'),
            'missing': '/unexisting_page/',
            'post_detail': reverse(
                'posts:post_detail',
                kwargs={'pk': cls.post.pk},
            ),
            'profile': reverse('posts:profile', kwargs={'username': cls.user}),
            'profile_follow': reverse(
                'posts:profile_follow',
                kwargs={'username': cls.user},
            ),
            'profile_unfollow': reverse(
                'posts:profile_unfollow',
                kwargs={'username': cls.user},
            ),
        }

    def test_http_statuses(self) -> None:
        """Тест получаемого кода ответа страниц.

        В зависимости от уровня прав пользователя
        страница возвращает соответствующий код ответа.
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
            (
                self.urls.get('follow'),
                HTTPStatus.OK,
                self.authorized_client_author,
            ),
            (self.urls.get('follow'), HTTPStatus.FOUND, self.client),
            (
                self.urls.get('profile_follow'),
                HTTPStatus.FOUND,
                self.authorized_client_author,
            ),
            (self.urls.get('profile_follow'), HTTPStatus.FOUND, self.client),
            (
                self.urls.get('profile_unfollow'),
                HTTPStatus.FOUND,
                self.authorized_client_author,
            ),
            (self.urls.get('profile_unfollow'), HTTPStatus.FOUND, self.client),
            (
                self.urls.get('comment'),
                HTTPStatus.FOUND,
                self.authorized_client_author,
            ),
            (self.urls.get('comment'), HTTPStatus.FOUND, self.client),
        )
        for address_url, status_code, client in httpstatuses:
            with self.subTest(
                address_url=address_url,
                status_code=status_code,
            ):
                self.assertEqual(
                    client.get(address_url).status_code,
                    status_code,
                    f'страница {address_url} недоступна',
                )

    def test_templates(self) -> None:
        """URL-адрес использует соответствующий шаблон.

        В зависимости от прав и статуса пользователя
        используется соответствующий шаблон.
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
            (
                self.urls.get('follow'),
                'posts/follow.html',
                self.authorized_client,
            ),
        )
        for address_url, template, status_client in templates:
            with self.subTest(
                address_url=address_url,
                template=template,
            ):
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
            (
                self.urls.get('follow'),
                redirect_to_login(reverse('posts:follow_index')).url,
                self.client,
            ),
            (
                self.urls.get('profile_follow'),
                reverse('posts:follow_index'),
                self.authorized_client,
            ),
            (
                self.urls.get('profile_follow'),
                redirect_to_login(
                    reverse(
                        'posts:profile_follow',
                        kwargs={'username': self.user},
                    )
                ).url,
                self.client,
            ),
            (
                self.urls.get('profile_unfollow'),
                redirect_to_login(
                    reverse(
                        'posts:profile_unfollow',
                        kwargs={'username': self.user},
                    )
                ).url,
                self.client,
            ),
            (
                self.urls.get('comment'),
                reverse(
                    'posts:post_detail',
                    kwargs={'pk': self.post.pk},
                ),
                self.authorized_client,
            ),
            (
                self.urls.get('comment'),
                redirect_to_login(
                    reverse(
                        'posts:add_comment',
                        kwargs={'pk': self.post.pk},
                    )
                ).url,
                self.client,
            ),
        )
        for address_url, redirect_page, status_client in redirects:
            with self.subTest(
                address_url=address_url,
                redirect_page=redirect_page,
            ):
                self.assertRedirects(
                    status_client.get(address_url), redirect_page
                )
