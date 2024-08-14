from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


COMMENT_TEXT = 'Текст комментария'


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news):
    """Метод проверяет, что анонимный пользователь
    не может отправить комментарий.
    """
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data={'text': COMMENT_TEXT})
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(author_client, author, news):
    """Метод проверяет, что авторизованный пользователь
    может отправить комментарий.
    """
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data={'text': COMMENT_TEXT})
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.author == author
    assert comment.news == news


def test_user_cant_use_bad_words(author_client, news):
    """Метод проверяет, что, если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    bad_words_data = {
        'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
    }
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(
    author_client, comment, news
):
    """Метод проверяет, что авторизованный пользователь может
    удалять свои комментарии.
    """
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    expected_url = reverse('news:detail', args=(news.id,)) + '#comments'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def not_author_cant_delete_comment_of_another_user(not_author_client, comment):
    """Метод проверяет, что авторизованный пользователь не может
    удалять чужие комментарии.
    """
    url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
    author_client, news, comment
):
    """Метод проверяет, что авторизованный пользователь может
    редактировать свои комментарии.
    """
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, data={'text': COMMENT_TEXT})
    expected_url = reverse('news:detail', args=(news.id,)) + '#comments'
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT


def not_author_cant_edit_comment_of_another_user(not_author_client, comment):
    """Метод проверяет, что авторизованный пользователь не может
    редактировать чужие комментарии.
    """
    url = reverse('notes:edit', args=(comment.id,))
    response = not_author_client.post(url, data={'text': COMMENT_TEXT})
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != COMMENT_TEXT
