from linecache import cache

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from faker import Faker
from mixer.backend.django import mixer

from posts.models import Follow, Post
from posts.tests.common import image

User = get_user_model()
faker = Faker()


class PostPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user_author = mixer.blend(User)
        cls.group = mixer.blend('posts.Group', description=faker.text())
        cls.post = mixer.blend(
            'posts.Post',
            author=cls.user_author,
            image=image(),
        )
        cls.templates_pages_names = {
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'pk': cls.post.pk},
            ): 'posts/create_post.html',
            reverse(
                'posts:page_post',
                kwargs={'slug': cls.group.slug},
            ): 'posts/group_list.html',
            reverse('posts:h_page'): 'posts/index.html',
            reverse(
                'posts:post_detail',
                kwargs={'pk': cls.post.pk},
            ): 'posts/post_detail.html',
            reverse(
                'posts:profile',
                kwargs={'username': cls.user_author},
            ): 'posts/profile.html',
        }
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user_author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_correct_contecst(self):
        """В шаблон index.html передается правильный контекст."""
        response = self.authorized_client.get(reverse('posts:h_page'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.pub_date, self.post.pub_date)
        self.assertEqual(first_object.author, self.post.author)
        self.assertEqual(first_object.group, self.post.group)

    def test_group_list_page_correct_contecst(self):
        """В шаблон group_list.html передается правильный контекст."""
        response = self.authorized_client.get(
            reverse('posts:page_post', kwargs={'slug': self.group.slug})
        )
        first_object = response.context['group']
        self.assertEqual(first_object.title, self.group.title)
        self.assertEqual(first_object.slug, self.group.slug)
        self.assertEqual(first_object.description, self.group.description)

    def test_profile_page_correct_contecst(self):
        """В шаблон profile.html передается правильный контекст"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user_author})
        )
        first_object = response.context['user_name']
        self.assertEqual(first_object, self.user_author)

    def test_post_detail_page_correct_contecst(self):
        """В шаблон post_detail.html передается правильный контекст"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'pk': self.post.pk})
        )
        first_object = response.context['post']
        self.assertEqual(first_object.pk, self.post.pk)
        self.assertEqual(first_object.image, self.post.image)

    def test_create_post_correct_context(self):
        """В шаблон create_post.html передается правильный контекст.

        При созддании поста авторизованным пользователлем.
        """
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_correct_context(self):
        """В шаблон create_post.html передается правильный контекст.

        При редактирование поста авторизованным пользователлем.
        """
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'pk': self.post.pk})
        )
        first_object = response.context['post']
        self.assertEqual(first_object.pk, self.post.pk)

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_page_cash(self):
        """Тестирование кэша на главной странице."""
        post_for_delete = mixer.blend('posts.Post')
        self.assertEqual(
            self.client.get(reverse('posts:h_page'))
            .context['page_obj'][0]
            .text,
            post_for_delete.text,
        )
        Post.objects.get(text=post_for_delete.text).delete()
        cache.clear()
        self.assertNotEqual(
            self.client.get(reverse('posts:h_page'))
            .context['page_obj'][0]
            .text,
            post_for_delete.text,
        )


class GroupPostPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.author_from_group = mixer.blend(User)
        cls.group = mixer.blend('posts.Group', description=faker.text())
        cls.post = mixer.blend(
            'posts.Post',
            author=cls.author_from_group,
            group=cls.group,
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author_from_group)

    def test_show_post_with_group_on_index_page(self):
        """Пост с группой показывается на главной странице"""
        response = self.authorized_client.get(reverse('posts:h_page'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.group, self.post.group)

    def test_show_post_with_group_on_group_list_page(self):
        """Пост с группой показывается на странице выбранной группы"""
        response = self.authorized_client.get(
            reverse('posts:page_post', kwargs={'slug': self.group.slug})
        )
        posts_of_group = list(self.group.posts.all())
        self.assertEqual(list(response.context['page_obj']), posts_of_group)

    def test_show_post_with_group_on_profile_page(self):
        """Пост с группой показывается на странице профайла пользователя"""
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={'username': self.author_from_group}
            )
        )
        posts_of_group = list(self.author_from_group.posts.all())
        self.assertEqual(list(response.context['page_obj']), posts_of_group)

    def test_do_not_show_post_with_group_on_another_group_page(self):
        """Не попал ли пост в группу, к которой он не относится"""
        another_group = mixer.blend('posts.Group')
        self.assertNotEqual(self.post.group, another_group)


class FollowingViewsTest(TestCase):
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

    def test_subscription_to_authorized_user(self):
        """Проверка подписки авторизованным пользователем."""
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author_following},
            )
        )
        self.assertEqual(
            Follow.objects.all()[0].user, self.authorized_follower
        )
        self.assertEqual(Follow.objects.all()[0].author, self.author_following)

    def test_unsubscription_to_authorized_user(self):
        """Проверка отписки авторизованным пользователем."""
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.author_following},
            )
        )
        self.assertFalse(Follow.objects.all())

    def test_new_post_appears_in_feed_subscribers(self):
        """Запись пользователя появляется в ленте подписчиков."""
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author_following},
            )
        )
        self.assertEqual(
            self.authorized_client.get(reverse('posts:follow_index'))
            .context['page_obj'][0]
            .author,
            self.post.author,
        )

    def test_new_post_not_appears_in_feed_non_subscribers(self):
        """Запись пользователя не появляется в ленте неподписчиков."""
        self.assertTrue(
            not [
                *self.authorized_client.get(
                    reverse('posts:follow_index'),
                ).context.get('page_obj')
            ],
        )


class ImageOnPagesTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.post = mixer.blend(
            'posts.Post',
            author=mixer.blend(User),
            group=mixer.blend('posts.Group'),
            image=image(),
        )
        cls.urls = {
            reverse('posts:page_post', kwargs={'slug': cls.post.group.slug}),
            reverse('posts:h_page'),
            reverse('posts:profile', kwargs={'username': cls.post.author}),
        }

    def test_passing_image_in_dictionary_context(self):
        """Проверка вывода поста с изображениями.

        При выводе поста с картинкой изображение передаётся в словаре context:
        - на главную страницу,
        - на страницу профайла,
        - на страницу группы.
        """
        for url in self.urls:
            with self.subTest(url=url):
                self.assertEqual(
                    self.client.get(url).context['page_obj'][0].image,
                    self.post.image,
                )
