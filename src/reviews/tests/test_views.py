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
        headline = reviews[0].find("h2")
        assert headline is not None
        assert headline.string == night_patrol.title
