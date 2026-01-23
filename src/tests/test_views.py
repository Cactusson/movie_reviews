import pytest
from bs4 import BeautifulSoup
from pytest_django import asserts


@pytest.mark.django_db
class TestHomePage:
    @pytest.fixture
    def soup(self, client):
        response = client.get("/")
        return BeautifulSoup(response.content, "html.parser")

    def test_uses_home_page_template(self, client):
        response = client.get("/")
        asserts.assertTemplateUsed(response, "reviews/home_page.html")

    def test_displays_review(self, night_patrol, soup):
        reviews = soup.find_all("div", {"class": "review"})
        assert len(reviews) == 1
        review = reviews[0]

        headline = review.find("h2")
        assert headline is not None
        assert headline.string == night_patrol.title

        author = review.find("div", {"class": "author"})
        assert author is not None
        assert night_patrol.author.name in author.text

        url = review.find("div", {"class": "url"})
        assert url is not None
        assert night_patrol.url in url.text

        date = review.find("div", {"class": "date"})
        assert date is not None
        assert night_patrol.formatted_date in date.text
