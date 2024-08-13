from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()


class TestListPage(TestCase):

    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заметка',
            text='Просто текст',
            author=cls.author,
        )

    def test_notes_list_for_different_users(self):
        """Метод проверяет, что отдельная заметка передаётся
        на страницу со списком заметок; в список заметок одного
        пользователя не попадают заметки другого пользователя;
        """
        users_notes_in_list = (
            (self.author, True),
            (self.reader, False)
        )
        for user, note_in_list in users_notes_in_list:
            with self.subTest(user=user):
                self.client.force_login(user)
                response = self.client.get(self.LIST_URL)
                object_list = response.context['object_list']
                self.assertEqual((self.note in object_list), note_in_list)

    def test_pages_contains_form(self):
        """Метод проверяет, что на страницы создания и
        редактирования заметки передаются формы.
        """
        urls_args = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        self.client.force_login(self.author)
        for name, arg in urls_args:
            url = reverse(name, args=arg)
            response = self.client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)
