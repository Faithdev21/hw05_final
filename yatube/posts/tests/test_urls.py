from http import HTTPStatus

from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Group, Post
from . import constans as const

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создадим запись в БД для проверки доступности
        адреса posts/post_id/."""
        super().setUpClass()
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.create(
                username=const.USERNAME,
                email=const.EMAIL,
                password=const.PASSWORD),
            id=const.ID,
        )
        cls.group = Group.objects.create(
            title=const.TITLE,
            slug=const.SLUG,
            description=const.DESCRIPTION,
        )

    def setUp(self):
        """Создаем авторизованный и неавторизованный клиенты."""
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_exist_at_desired_location(self):
        """Проверяем доступность страниц для гостей
        и авторизованных пользователей."""
        posts_templates_url = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': self.post.author.username}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': f'{self.post.id}'}
            ),
        }
        for template, address in posts_templates_url.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_and_edit_post(self):
        """Проверяем создание и редактирование поста."""
        new_post = Post.objects.create(
            author=self.user,
            text='Text to edit',
            group=self.post.group,
        )
        reverse_name = (
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': new_post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for name in reverse_name:
            response = self.authorized_client.get(name)
            for field, expected in form_fields.items():
                with self.subTest(field=field):
                    form_field = response.context.get('form').fields.get(field)
                    self.assertIsInstance(form_field, expected)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        posts_templates_url_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': self.post.author.username}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': f'{self.post.id}'}
            ),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, address in posts_templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_comments_url_exists_at_desired_location(self):
        Comment.objects.create(
            text='Тестовый комментарий',
            author=self.user,
            post_id=self.post.id,
        )
        response = self.guest_client.get(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id})
        )
        self.assertRedirects(
            response, reverse('users:login') + '?next=' + reverse(
                'posts:add_comment', kwargs={'post_id': self.post.id}))
