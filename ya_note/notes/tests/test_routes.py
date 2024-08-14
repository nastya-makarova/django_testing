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
        cls.urls_without_args = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None)
        )
        cls.urls_with_args = (
            ('notes:detail', (cls.notes.slug,)),
            ('notes:edit', (cls.notes.slug,)),
            ('notes:delete', (cls.notes.slug,)),
        )
        cls.urls = cls.urls_with_args + cls.urls_without_args

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
        self.client.force_login(self.author)
        for name, args in self.urls_without_args:
            with self.subTest(name=name):
                url = reverse(name, args=args)
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
            for name, args in self.urls_with_args:
                with self.subTest(name=name, user=user):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects(self):
        """Метод проверяет, что при попытке перейти на страницу списка заметок,
        страницу успешного добавления записи, страницу добавления заметки,
        отдельной заметки, редактирования или удаления заметки анонимный
        пользователь перенаправляется на страницу логина.
        """
        login_url = reverse('users:login')
        for name, args in self.urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                expected_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)
