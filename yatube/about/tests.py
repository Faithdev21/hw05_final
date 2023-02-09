from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class PostURLTests(TestCase):
    def setUp(self):
        """Создаем авторизованный и неавторизованный клиенты."""
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_exist_at_desired_location(self):
        """Проверяем доступность страниц для гостей
        и авторизованных пользователей."""
        templates_urls = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, address in templates_urls.items():
            with self.subTest(address=address):
                if self.authorized_client:
                    response = self.authorized_client.get(address)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        templates_urls = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, address in templates_urls.items():
            with self.subTest(address=address):
                if self.authorized_client:
                    response = self.authorized_client.get(address)
                    self.assertTemplateUsed(response, template)
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
