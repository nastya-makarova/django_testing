import pytest

from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


COMMENT_COUNT = 10
COMMENT_TEXT = 'Текст комментария'


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
    news = News.objects.create(
        title='Заголовок', text='Текст'
    )
    return news


@pytest.fixture
def comment(news, author):
    """Фикстура возвращает объект комментария."""
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст'
    )
    return comment


@pytest.fixture
def news_id_for_args(news):
    """Фикстура возвращает id новости."""
    return (news.id,)


@pytest.fixture
def get_news_detail_page(news):
    """Фикстура возвращает страницу новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def comment_id_for_args(comment):
    """Фикстура возвращает id комментария."""
    return (comment.id,)


@pytest.fixture
def all_news():
    """Фикстура возвращает объекты новостей для главной страницы."""
    today = datetime.today()
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


@pytest.fixture
def form_data():
    """Фикстура возвращает словарь модели Comment"""
    return {'text': COMMENT_TEXT}


@pytest.fixture
def get_url_to_comments(get_news_detail_page):
    """Фикстура возвращает адрес блока с комментариями."""
    return get_news_detail_page + '#comments'
