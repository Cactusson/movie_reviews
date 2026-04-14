import datetime
import os

import pytest
import responses
import time_machine
from aioresponses import aioresponses
from django.contrib.auth import get_user_model
from django.db import connections
from playwright.sync_api import sync_playwright

from reviews.models import Author, Review
from tests.data_provider import DataProvider

os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

USER_MODEL = get_user_model()


def create_review(data):
    author = Author.objects.get(name=data["author"])
    return Review.objects.create(
        title=data["title"],
        author=author,
        url=data["url"],
        date=datetime.date.fromisoformat(data["date"]),
    )


@pytest.fixture()
def close_db_connections():
    yield
    for conn in connections.all():
        conn.close()


@pytest.fixture(scope="session")
def test_data():
    provider = DataProvider("tests/fixtures/test_data.json")
    return {"reviews": provider.get("reviews")}


@pytest.fixture
def page(request):
    headed = request.config.getoption("--headed")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not headed)
        page = browser.new_page()
        yield page
        browser.close()


@pytest.fixture
def first_user(db):
    return USER_MODEL.objects.create(email="test@example.com")


@pytest.fixture
def second_user(db):
    return USER_MODEL.objects.create(email="test2@example.com")


@pytest.fixture
def mzs(db):
    return Author.objects.create(name="Matt Zoller Seitz")


@pytest.fixture
def sheila(db):
    return Author.objects.create(name="Sheila O'Malley")


@pytest.fixture
def night_patrol(db, mzs, test_data):
    return create_review(test_data["reviews"].get("Night Patrol"))


@pytest.fixture
def sound_of_falling(db, sheila, test_data):
    return create_review(test_data["reviews"]["Sound of Falling"])


@pytest.fixture
def king_of_color(db, mzs, test_data):
    return create_review(test_data["reviews"]["The King of Color"])


@pytest.fixture
def mocked_rss_feed():
    with aioresponses() as m:
        with open("tests/fixtures/test_feed_page_1.xml") as file:
            rss_content_page_1 = file.read()
        with open("tests/fixtures/test_feed_page_2.xml") as file:
            rss_content_page_2 = file.read()
        with open("tests/fixtures/test_feed_empty.xml") as file:
            rss_content_empty = file.read()
        with open("tests/fixtures/test_feed_with_duplicates.xml") as file:
            rss_content_with_duplicates = file.read()
        with open("tests/fixtures/test_feed_with_old_entries.xml") as file:
            rss_content_with_old_entries = file.read()
        with open("tests/fixtures/test_feed_indiewire.xml") as file:
            rss_content_indiewire = file.read()
        with open("tests/fixtures/test_feed_older_than_cutoff_year.xml") as file:
            rss_content_cutoff_year = file.read()
        with open("tests/fixtures/test_feed_contains_not_reviews.xml") as file:
            rss_content_with_not_reviews = file.read()

        # have to add mocked responses 100 times because otherwise they won't work more than once in one test
        # is there a better way?
        for _ in range(100):
            m.get(
                "https://www.indiewire.com/c/criticism/movies/feed/?paged=2",
                body=rss_content_empty,
                status=200,
            )
            m.get(
                "https://www.indiewire.com/c/criticism/movies/feed/?paged=1",
                body=rss_content_indiewire,
                status=200,
            )
            m.get(
                "https://www.rogerebert.com/reviews/feed_with_old_entries/?paged=2",
                body=rss_content_empty,
                status=200,
            )
            m.get(
                "https://www.rogerebert.com/reviews/feed_with_old_entries/?paged=1",
                body=rss_content_with_old_entries,
                status=200,
            )
            m.get(
                "https://www.rogerebert.com/reviews/feed_with_duplicates/?paged=2",
                body=rss_content_empty,
                status=200,
            )
            m.get(
                "https://www.rogerebert.com/reviews/feed_with_duplicates/?paged=1",
                body=rss_content_with_duplicates,
                status=200,
            )
            m.get(
                "https://www.rogerebert.com/reviews/feed/?paged=3",
                body=rss_content_empty,
                status=200,
            )
            m.get(
                "https://www.rogerebert.com/reviews/feed/?paged=2",
                body=rss_content_page_2,
                status=200,
            )
            m.get(
                "https://www.rogerebert.com/reviews/feed/?paged=1",
                body=rss_content_page_1,
                status=200,
            )
            m.get(
                "https://www.rogerebert.com/reviews/feed_cutoff_date/?paged=2",
                body=rss_content_empty,
                status=200,
            )
            m.get(
                "https://www.rogerebert.com/reviews/feed_cutoff_date/?paged=1",
                body=rss_content_cutoff_year,
                status=200,
            )
            m.get(
                "https://www.indiewire.com/c/criticism/movies/feed_with_not_reviews/?paged=2",
                body=rss_content_empty,
                status=200,
            )
            m.get(
                "https://www.indiewire.com/c/criticism/movies/feed_with_not_reviews/?paged=1",
                body=rss_content_with_not_reviews,
                status=200,
            )
        yield m


@pytest.fixture
def mocked_letterboxd_feed():
    with open("tests/fixtures/test_feed_letterboxd.xml") as file:
        rss_content = file.read()
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        rsps.add(
            responses.GET,
            "https://letterboxd.com/alice/rss/",
            body=rss_content,
            status=200,
            content_type="application/xml",
        )
        yield rsps


@pytest.fixture(autouse=True, scope="session")
def set_date_to_jan_26_2026():
    traveller = time_machine.travel(datetime.datetime(2026, 1, 26))
    traveller.start()
