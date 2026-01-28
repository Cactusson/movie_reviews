import pytest
from bs4 import BeautifulSoup
from pytest_django import asserts

from reviews.models import Author


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

    def test_title_of_review_is_a_url_to_its_detail_page(self, night_patrol, soup):
        review = soup.find("div", {"class": "review"})
        title = review.find("h2")
        url = title.find("a")
        assert url is not None
        assert url["href"] == night_patrol.get_absolute_url()

    def test_if_review_has_content_home_page_displays_first_sentence(
        self, night_patrol, soup
    ):
        review = soup.find("div", {"class": "review"})
        content = review.find("div", {"class": "review-content"})
        assert content is not None
        assert (
            BeautifulSoup(night_patrol.first_sentence, "html.parser").get_text()
            == content.get_text()
        )


@pytest.mark.django_db
class TestReviewDetail:
    @pytest.fixture
    def soup(self, client, night_patrol):
        response = client.get(f"/{night_patrol.pk}/")
        return BeautifulSoup(response.content, "html.parser")

    def test_uses_review_detail_template(self, client, night_patrol):
        response = client.get(f"/{night_patrol.pk}/")
        asserts.assertTemplateUsed(response, "reviews/review_detail.html")

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

    def test_displays_content_if_exists(self, night_patrol, soup):
        review = soup.find("div", {"class": "review"})
        content = review.find("div", {"class": "review-content"})

        assert content is not None
        assert (
            BeautifulSoup(night_patrol.content, "html.parser").get_text()
            in content.get_text()
        )

    def test_name_of_author_is_url_to_this_author_detail_page(self, night_patrol, soup):
        review = soup.find("div", {"class": "review"})
        author = review.find("div", {"class": "author"})
        author_url = author.find("a")
        assert author_url is not None
        assert author_url["href"] == night_patrol.author.get_absolute_url()


@pytest.mark.django_db
class TestAuthorDetail:
    @pytest.fixture
    def soup(self, client, mzs, night_patrol, king_of_color, sound_of_falling):
        response = client.get(f"/{mzs.slug}/")
        return BeautifulSoup(response.content, "html.parser")

    def test_uses_author_detail_template(self, client, mzs):
        response = client.get(f"/{mzs.slug}/")
        asserts.assertTemplateUsed(response, "reviews/author_detail.html")

    def test_author_name_is_present_in_title_and_page(self, mzs, soup):
        assert mzs.name in soup.title.string
        headline = soup.find("h1")
        assert headline is not None
        assert mzs.name in headline.get_text()

    def test_only_reviews_by_author_are_present_on_page(self, mzs, soup):
        reviews = soup.find_all("div", {"class": "review"})
        assert len(reviews) == 2
        titles = []
        for review in reviews:
            title = review.find("h2")
            assert title is not None
            titles.append(title.string)
        assert titles == [review.title for review in mzs.reviews.all()]

    def test_counter_of_reviews_is_present(self, mzs, soup):
        headline = soup.find("h1")
        assert headline is not None
        counter = headline.find("span")
        assert str(mzs.reviews.count()) in counter.string


@pytest.mark.django_db
class TestAuthorList:
    @pytest.fixture()
    def soup(self, client, mzs, sheila, night_patrol, king_of_color, sound_of_falling):
        response = client.get("/authors/")
        return BeautifulSoup(response.content, "html.parser")

    def test_uses_author_list_template(self, client):
        response = client.get("/authors/")
        asserts.assertTemplateUsed(response, "reviews/author_list.html")

    def test_all_authors_are_listed(self, soup, mzs, sheila):
        list_of_authors = soup.find("ul", {"class": "author-list"})
        assert list_of_authors is not None
        assert len(list_of_authors.find_all("li")) == 2
        for author in list_of_authors.find_all("li"):
            name = author.find("a")
            assert name is not None
            assert name.string in [mzs.name, sheila.name]

    def test_authors_are_ordered_by_name(self, soup, mzs, sheila):
        list_of_authors = soup.find("ul", {"class": "author-list"})
        assert list_of_authors is not None
        assert list_of_authors.find_all("li")[0].find("a").string == sheila.name
        assert list_of_authors.find_all("li")[1].find("a").string == mzs.name

    def test_each_author_has_counter_of_reviews(self, soup):
        list_of_authors = soup.find("ul", {"class": "author-list"})
        assert list_of_authors is not None
        for author in list_of_authors.find_all("li"):
            name = author.find("a").string
            counter = author.find("span", {"class": "counter"}).string
            assert Author.objects.get(name=name).reviews.count() == int(counter)
