import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, all_news):
    """Метод проверяет количество новостей на главной странице."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, all_news):
    """Метод проверяет, что новости отсортированы
    от самой свежей к самой старой.
    """
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(all_comments, client, get_news_detail_page):
    """Метод проверяет, что комментарии на странице отдельной новости
    отсортированы в хронологическом порядке.
    """
    response = client.get(get_news_detail_page)
    assert 'news' in response.context
    news = response.context['news']
    comments = news.comment_set.all()
    timestamps = [comment.created for comment in comments]
    sorted_timestamps = sorted(timestamps)
    assert sorted_timestamps == timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, get_news_detail_page):
    """Метод проверяет, что анонимному пользователю недоступна форма
    для отправки комментария на странице отдельной новости.
    """
    response = client.get(get_news_detail_page)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, get_news_detail_page):
    """Метод проверяет, что авторизованному пользователю доступна форма
    для отправки комментария на странице отдельной новости.
    """
    response = author_client.get(get_news_detail_page)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
