from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post
from . import constans as const

User = get_user_model()


class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestName')
        cls.post = Post.objects.create(
            text=const.TEXT,
            author=cls.user,
            id=const.ID,
        )
        cls.group = Group.objects.create(
            title=const.TITLE,
            slug=const.SLUG,
            description=const.DESCRIPTION,
        )

        cls.image = const.IMAGE

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_create_count(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        test_author = self.user
        test_group = self.group
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.post.author.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(form_data['text'], self.post.text)
        self.assertEqual(self.post.author, test_author)
        self.assertEqual(form_data['group'], test_group.id)

    def test_guest_create_post(self):
        form_data = {
            'text': 'Test guest post',
            'group': self.group.id
        }
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertFalse(
            Post.objects.filter(
                text='Test guest post'
            ).exists()
        )

    def test_post_edit_create_record(self):
        new_post = self.post
        form_data = {
            'text': 'Data from post',
            'group': self.group.id,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        test_post_1 = Post.objects.get(id=self.post.id)
        self.client.get(reverse(
            'posts:post_edit', kwargs={'post_id': test_post_1.id})
        )
        form_data = {
            'text': 'Editing text',
            'group': self.group.id,
        }
        response_edit = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': test_post_1.id}),
            data=form_data,
            follow=True,
        )
        test_post_2 = Post.objects.get(id=self.group.id)
        self.assertEqual(form_data['text'], test_post_2.text)
        self.assertEqual(response_edit.status_code, HTTPStatus.OK)
        self.assertIsNot(new_post, test_post_2)

    def test_create_new_post(self):
        """Создание записи в БД поста с картинкой."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Пост с картинкой',
            'group': self.group.id,
            'image': self.image,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.post.author.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
