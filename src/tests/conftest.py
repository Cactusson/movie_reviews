import datetime
import os

import pytest
import responses
import time_machine
from playwright.sync_api import sync_playwright

from reviews.models import Author, Review
from tests.data_provider import DataProvider

os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


def create_review(data):
    author = Author.objects.get(name=data["author"])
    return Review.objects.create(
        title=data["title"],
        author=author,
        url=data["url"],
        date=datetime.date.fromisoformat(data["date"]),
        content=data.get("content", None),
    )


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

    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        # have to add mocked responses 100 times because otherwise they won't work more than once in one test
        # is there a better way?
        for _ in range(100):
            rsps.add(
                responses.GET,
                "https://www.indiewire.com/c/criticism/movies/feed/?paged=2",
                body=rss_content_empty,
                status=200,
                content_type="application/xml",
            )
            rsps.add(
                responses.GET,
                "https://www.indiewire.com/c/criticism/movies/feed/",
                body=rss_content_indiewire,
                status=200,
                content_type="application/xml",
            )
            rsps.add(
                responses.GET,
                "https://www.rogerebert.com/reviews/feed_with_old_entries/?paged=2",
                body=rss_content_empty,
                status=200,
                content_type="application/xml",
            )
            rsps.add(
                responses.GET,
                "https://www.rogerebert.com/reviews/feed_with_old_entries/",
                body=rss_content_with_old_entries,
                status=200,
                content_type="application/xml",
            )
            rsps.add(
                responses.GET,
                "https://www.rogerebert.com/reviews/feed_with_duplicates/?paged=2",
                body=rss_content_empty,
                status=200,
                content_type="application/xml",
            )
            rsps.add(
                responses.GET,
                "https://www.rogerebert.com/reviews/feed_with_duplicates/",
                body=rss_content_with_duplicates,
                status=200,
                content_type="application/xml",
            )
            rsps.add(
                responses.GET,
                "https://www.rogerebert.com/reviews/feed/?paged=3",
                body=rss_content_empty,
                status=200,
                content_type="application/xml",
            )
            rsps.add(
                responses.GET,
                "https://www.rogerebert.com/reviews/feed/?paged=2",
                body=rss_content_page_2,
                status=200,
                content_type="application/xml",
            )
            rsps.add(
                responses.GET,
                "https://www.rogerebert.com/reviews/feed/",
                body=rss_content_page_1,
                status=200,
                content_type="application/xml",
            )

        yield rsps


@pytest.fixture(autouse=True, scope="session")
def set_date_to_jan_26_2026():
    traveller = time_machine.travel(datetime.datetime(2026, 1, 26))
    traveller.start()
