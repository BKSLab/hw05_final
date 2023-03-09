from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from mixer.backend.django import mixer

User = get_user_model()


NUMBER_TEST_POSTS = 13


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.posts = mixer.cycle(NUMBER_TEST_POSTS).blend(
            'posts.Post',
            author=mixer.blend(User, username='kir'),
            group=mixer.blend('posts.Group', slug='test-slug-page'),
        )
        for post in cls.posts:
            cls.reverse_names_paginate = {
                reverse(
                    'posts:page_post',
                    kwargs={'slug': post.group.slug},
                ),
                reverse('posts:h_page'),
                reverse('posts:profile', kwargs={'username': post.author}),
            }
        cls.authorized_client = Client()

    def test_first_and_second_pages_paginate(self):
        """
        Постраничный вывод постов на главной странице, странице группы
        и на странице профиля.
        """
        for reverse_name in self.reverse_names_paginate:
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(
                    len(
                        self.authorized_client.get(reverse_name).context[
                            'page_obj'
                        ]
                    ),
                    settings.OBJECTS_PER_PAGE,
                )
                self.assertEqual(
                    len(
                        self.authorized_client.get(
                            reverse_name + '?page=2'
                        ).context['page_obj']
                    ),
                    NUMBER_TEST_POSTS - settings.OBJECTS_PER_PAGE,
                )
