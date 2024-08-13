from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.notes = Note.objects.create(
            title='Название заметки',
            text='Текст заметки',
            author=cls.author
        )
        cls.slug_for_args = (cls.notes.slug,)

    def test_pages_availability_for_anonymous_user(self):
        """Метод тестирует доступность для анонимных пользователей
        главной страницы,
        cтраницы регистрации пользователей,
        страниц входа в учётную запись и выхода из неё.
        """
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup'
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Метод проверяет доступность автору страниц:
        страницы успешного добавления заметки, страницы списка заметок,
        страницы создания заметки.
        """
        # Логиним пользователя в клиенте:
        self.client.force_login(self.author)

        # Создаём набор тестовых данных - кортеж кортежей.
        # Каждый вложенный кортеж содержит два элемента:
        # имя пути и позиционные аргументы для функции reverse().
        urls = ('notes:add', 'notes:list', 'notes:success')
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        """Метод проверяет, что cтраницы отдельной заметки, страницы
        редактирования и удаления заметки доступны автору, но недоступны
        другому пользователю.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND)
        )

        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(name=name, user=user):
                    url = reverse(name, args=self.slug_for_args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects(self):
        """Метод проверяет, что при попытке перейти на страницу списка заметок,
        страницу успешного добавления записи, страницу добавления заметки,
        отдельной заметки, редактирования или удаления заметки анонимный
        пользователь перенаправляется на страницу логина.
        """
        urls = (
            ('notes:detail', self.slug_for_args),
            ('notes:edit', self.slug_for_args),
            ('notes:delete', self.slug_for_args),
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None)
        )
        login_url = reverse('users:login')
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                expected_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)
