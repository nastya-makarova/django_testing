from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
def test_pages_availability_for_anonymous_user(client, name, args,  news):
    """Метод проверяет, что доступность анонимному пользователю главной
    страницы, страницы отдельной нововсти, cтраниц регистрации пользователей,
    входа в учётную запись и выхода).
    """
    if args is not None:
        url = reverse(name, args=(news.id,))
    else:
        url = reverse(name, args=args)

    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND)
    )
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client, expected_status, comment
):
    """Метод проверяет, что страницы удаления и редактирования
    комментария доступны автору комментария и не доступны для
    другого пользователя.
    """
    urls = (
        ('news:edit', (comment.id,)),
        ('news:delete', (comment.id,))
    )
    for name, args in urls:
        url = reverse(name, args=args)
        response = parametrized_client.get(url)
        assert response.status_code == expected_status


@pytest.mark.django_db
def test_redirect_for_anonymous_client(client, comment):
    """Метод проверяет, что при попытке перейти на страницу редактирования
    или удаления комментария анонимный пользователь перенаправляется на
    страницу авторизации.
    """
    urls = (
        ('news:edit', (comment.id,)),
        ('news:delete', (comment.id,))
    )
    login_url = reverse('users:login')
    for name, args in urls:
        url = reverse(name, args=args)
        redirect_url = f'{login_url}?next={url}'
        response = client.get(url)
        assertRedirects(response, redirect_url)
