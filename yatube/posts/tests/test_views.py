from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Follow, Group, Post
from . import constans as const

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем запись в БД."""
        super().setUpClass()
        cls.post = Post.objects.create(
            text=const.TEXT,
            author=User.objects.create(
                username=const.USERNAME,
                email=const.EMAIL,
                password=const.PASSWORD),
            id=const.ID,
            group=Group.objects.create(
                title=const.TITLE,
                slug=const.SLUG,
                description=const.DESCRIPTION,
            ),
            image=const.IMAGE,
        )
        cls.post1 = Post.objects.create(
            text=const.TEXT1,
            author=User.objects.create(
                username=const.USERNAME1,
                email=const.EMAIL1,
                password=const.PASSWORD1),
            id=const.ID1,
            group=Group.objects.create(
                title=const.TITLE1,
                slug=const.SLUG1,
                description=const.DESCRIPTION,
            ),
            image=const.IMAGE,
        )

    def setUp(self):
        """Создаем авторизованный клиент"""
        cache.clear()
        self.user = User.objects.create_user(username='TestUser')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        posts_templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list', kwargs={'slug': self.post.group.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': self.post.author.username}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in posts_templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        task_author_0 = first_object.author.username
        task_text_0 = first_object.text
        task_image_0 = first_object.image
        cache.clear()
        self.assertEqual(task_author_0, self.post1.author.username)
        self.assertEqual(task_text_0, self.post1.text)
        self.assertEqual(task_image_0, self.post1.image)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.post.group.slug})
        )
        first_object = response.context['group']
        task_title_0 = first_object.title
        task_slug_0 = first_object.slug
        task_image_0 = response.context['post'].image
        self.assertEqual(task_title_0, self.post.group.title)
        self.assertEqual(task_slug_0, self.post.group.slug)
        self.assertEqual(task_image_0, self.post.image)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.post.author.username})
        )
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        task_image_0 = first_object.image
        self.assertEqual(
            response.context['author'].username, self.post.author.username)
        self.assertEqual(task_text_0, self.post.text)
        self.assertEqual(task_image_0, self.post.image)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context['post'].text, self.post.text)
        self.assertEqual(
            response.context['post'].author.username, self.post.author.username
        )
        self.assertEqual(response.context['post'].id, int(self.post.id))
        self.assertEqual(response.context['post'].image, self.post.image)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_another_group(self):
        """Пост не попал в другую группу."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.post1.group.slug})
        )
        first_object = response.context["page_obj"][0]
        post_text_0 = first_object.text
        self.assertTrue(post_text_0, self.post1.text)

    def test_comments_in_post(self):
        """Новый комментарий добавлен к посту."""
        comment_count = Comment.objects.count()
        form_data = {'text': 'Тестовый комментарий'}
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)

    def test_cache(self):
        post = Post.objects.create(text='Тест кэша', author=self.user)
        post_on_main = self.guest_client.get(reverse('posts:index')).content
        post.delete()
        post_in_cache = self.guest_client.get(reverse('posts:index')).content
        self.assertEqual(post_on_main, post_in_cache)
        cache.clear()
        post_after_clean_cache = self.guest_client.get(
            reverse('posts:index')).content
        self.assertNotEqual(post_on_main, post_after_clean_cache)


class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username=const.USERNAME,
            email=const.EMAIL,
            password=const.PASSWORD,
        )
        cls.group = Group.objects.create(
            title=const.TITLE,
            slug=const.SLUG,
        )
        cls.post = []
        for i in range(13):
            cls.post.append(Post(
                text=f'Test post {i}',
                author=cls.author,
                group=cls.group,
            )
            )
        Post.objects.bulk_create(cls.post)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_contains_posts(self):
        """Проверка: количество постов на первой
        странице равно 10, а на второй - 3."""
        cache.clear()
        urls_list = {
            reverse('posts:index'): 'index',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): 'group_list',
            reverse('posts:profile',
                    kwargs={'username': const.USERNAME}): 'profile',
        }
        for url in urls_list.keys():
            response = self.client.get(url)
            self.assertEqual(len(response.context['page_obj']), 10)
        for url in urls_list.keys():
            response = self.client.get(url + '?page=2')
            self.assertEqual(len(response.context['page_obj']), 3)


class FollowTests(TestCase):
    def setUp(self):
        self.client_following = Client()
        self.client_subscriber = Client()
        self.following = User.objects.create_user(username='following')
        self.subscriber = User.objects.create_user(username='subscriber')
        self.client_following.force_login(self.following)
        self.client_subscriber.force_login(self.subscriber)
        self.post = Post.objects.create(
            author=self.following,
            text='Тестовая запись для проверки сервиса подписок'
        )
        self.post1 = Post.objects.create(
            author=self.subscriber,
            text='Просто второй пост'
        )

    def test_follow(self):
        self.client_subscriber.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.post.author.username}
            ))
        self.assertTrue(
            Follow.objects.filter(
                user=self.subscriber, author=self.following).exists()
        )

    def test_unfollow(self):
        Follow.objects.create(
            user=self.subscriber,
            author=self.following,
        )
        self.client_subscriber.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.following}
            ))
        self.assertFalse(
            Follow.objects.filter(
                user=self.subscriber, author=self.following).exists()
        )


def test_posts_visibility_for_subscribers(self):
    Follow.objects.create(
        user=self.subscriber,
        author=self.following,
    )
    response = self.client_subscriber.get(
        reverse('posts:follow_index')
    )
    self.assertIn(self.post.text, response.context.get('page_obj')[0].text)
    response = self.client_following.get(
        reverse('posts:follow_index')
    )
    self.assertNotIn(self.post, response.context.get('page_obj'))
