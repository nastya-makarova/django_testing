from datetime import timedelta

import pytest

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


COMMENT_COUNT = 10


@pytest.fixture
def author(django_user_model):
    """Фиктсутра возвращает автора комментария."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Фиктсутра возвращает обычного пользователя, не автора комментария."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Фикстура возвращает клиента, авторизованного для автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Фикстура возвращает клиента, авторизованного
    для обычного пользователя не автора.
    """
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """Фикстура возвращает объект новости."""
    return News.objects.create(
        title='Заголовок', text='Текст'
    )


@pytest.fixture
def comment(news, author):
    """Фикстура возвращает объект комментария."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст'
    )


@pytest.fixture
def all_news():
    """Фикстура возвращает объекты новостей для главной страницы."""
    today = timezone.now()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)
    return News.objects.bulk_create(all_news)


@pytest.fixture
def all_comments(news, author):
    """Фикстура возвращает объекты комментариев для страницы новвости."""
    now = timezone.now()
    for index in range(COMMENT_COUNT):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Текст {index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()
