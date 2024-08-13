from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class BaseTestClass(TestCase):

    NOTE_TITLE = 'Название заметки'
    NOTE_TEXT = 'Текст заметки'
    NOTE_ADD_URL = reverse('notes:add')
    REDIRECT_URL = reverse('notes:success')
    NOTE_SLUG = 'new-slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG
        }


class TestNoteCreation(BaseTestClass):

    def test_anonymous_user_cant_create_note(self):
        """Метод проверяет, что анонимный пользователь
        не может создать заметку.
        """
        response = self.client.post(self.NOTE_ADD_URL, data=self.form_data)
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={self.NOTE_ADD_URL}'
        self.assertRedirects(response, redirect_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_user_can_create_note(self):
        """Метод проверяет, что залогиненный пользователь
        может создать заметку.
        """
        response = self.auth_client.post(
            self.NOTE_ADD_URL,
            data=self.form_data
        )
        self.assertRedirects(response, self.REDIRECT_URL)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.author)


class TestSlug(BaseTestClass):

    def test_not_unique_slug(self):
        """Метод  проверяет, что невозможно создать
        две заметки с одинаковым slug.
        """
        note = Note.objects.create(
            title=self.NOTE_TITLE,
            text=self.NOTE_TEXT,
            slug='note-slug',
            author=self.author
        )
        self.form_data['slug'] = note.slug
        response = self.auth_client.post(
            self.NOTE_ADD_URL, data=self.form_data
        )
        self.assertFormError(
            response, 'form', 'slug',
            errors=(note.slug + WARNING)
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_empty_slug(self):
        """Метод проверяет, если при создании заметки
        не заполнен slug, то он формируется автоматически.
        """
        self.form_data.pop('slug')
        response = self.auth_client.post(
            self.NOTE_ADD_URL, data=self.form_data
        )
        self.assertRedirects(response, self.REDIRECT_URL)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(BaseTestClass):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text='Текст для заметки',
            author=cls.author
        )
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_author_can_delete_note(self):
        """Метод проверяет, что авторизованный пользователь может
        удалять свои заметки.
        """
        response = self.auth_client.delete(self.delete_url)
        self.assertRedirects(response, self.REDIRECT_URL)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_other_user_cant_delete_note(self):
        """Метод проверяет, что авторизованный пользователь
        не может удалять чужие заметки.
        """
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_other_user_cant_edit_note(self):
        """Метод проверяет, что авторизованный пользователь
        не может редактировать чужие заметки.
        """
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(note_from_db.title, self.note.title)
        self.assertEqual(note_from_db.text, self.note.text)
        self.assertEqual(note_from_db.slug, self.note.slug)

    def test_author_can_edit_note(self):
        """Метод проверяет, что авторизованный пользователь
        может редактировать свои заметки.
        """
        response = self.auth_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.REDIRECT_URL)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
