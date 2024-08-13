import pytest

from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, get_news_detail_page, form_data
):
    """Метод проверяет, что анонимный пользователь
    не может отправить комментарий.
    """
    url = get_news_detail_page
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(
    author_client, author, get_news_detail_page, form_data, news
):
    """Метод проверяет, что авторизованный пользователь
    может отправить комментарий.
    """
    url = get_news_detail_page
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


def test_user_cant_use_bad_words(author_client, get_news_detail_page):
    """Метод проверяет, что, если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    bad_words_data = {
        'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
    }
    response = author_client.post(get_news_detail_page, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(
    author_client, comment_id_for_args, get_url_to_comments
):
    """Метод проверяет, что авторизованный пользователь может
    удалять свои комментарии.
    """
    url = reverse('news:delete', args=comment_id_for_args)
    response = author_client.post(url)
    assertRedirects(response, get_url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def not_author_cant_delete_comment_of_another_user(
    not_author_client, comment_id_for_args
):
    """Метод проверяет, что авторизованный пользователь не может
    удалять чужие комментарии.
    """
    url = reverse('news:delete', args=comment_id_for_args)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
    author_client, comment_id_for_args,
    form_data, get_url_to_comments, comment
):
    """Метод проверяет, что авторизованный пользователь может
    редактировать свои комментарии.
    """
    url = reverse('news:edit', args=comment_id_for_args)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, get_url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def not_author_cant_edit_comment_of_another_user(
    not_author_client, comment_id_for_args, form_data, comment
):
    """Метод проверяет, что авторизованный пользователь не может
    редактировать чужие комментарии.
    """
    url = reverse('notes:edit', args=comment_id_for_args)
    response = not_author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != form_data['text']
