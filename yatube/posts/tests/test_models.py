from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from mixer.backend.django import mixer

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.post = mixer.blend('posts.Post')

    def test_models_post_have_correct_object_names(self):
        """Проверяем, что у моделм Post корректно работает __str__."""
        self.assertEqual(
            self.post.__str__(),
            self.post.text[:settings.SHOW_CHARACTERS],  # fmt: skip
        )


class GroupModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.group = mixer.blend('posts.Group')

    def test_models_group_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        self.assertEqual(
            self.group.__str__(),
            self.group.title[:settings.SHOW_CHARACTERS],  # fmt: skip
        )


class CommentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.comment = mixer.blend('posts.Comment')

    def test_models_group_have_correct_object_names(self):
        """Проверяем, что у модели Comment корректно работает __str__."""
        self.assertEqual(
            self.comment.__str__(),
            self.comment.text[:settings.SHOW_CHARACTERS],  # fmt: skip
        )


class FollowModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.subscription = mixer.blend('posts.Follow')

    def test_models_group_have_correct_object_names(self):
        """Проверяем, что у модели Follow корректно работает __str__."""
        self.assertEqual(
            self.subscription.__str__(),
            self.subscription.user.get_username()[: settings.SHOW_CHARACTERS],
        )
