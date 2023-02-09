from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post
from . import constans as const

User = get_user_model()


class PostModelTest(TestCase):
    """Тестируем Models."""

    @classmethod
    def setUpClass(cls):
        """Создаём тестовую запись в БД и сохраняем
        созданную запись в качестве переменной класса."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title=const.TITLE,
            slug=const.SLUG,
            description=const.DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=const.TEXT,
        )

    def test_verbose_name(self):
        """Verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {
            'author': const.AUTHOR,
            'group': const.GROUP,
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """Help_text в полях совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'Введите текст сюда',
            'group': 'Группа, к которой будет относиться пост',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    self.post._meta.get_field(value).help_text, expected)

    def test_posts_have_correct_object_names(self):
        """Проверяем, что у Post корректно работает __str__."""
        expected_object_name = self.post.text[:15]
        self.assertEqual(expected_object_name, str(self.post))

    def test_groups_have_correct_object_names(self):
        """Проверяем, что у Group корректно работает __str__."""
        expected_object_name = self.group.title
        self.assertEqual(expected_object_name, str(self.group))
