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


@pytest.mark.django_db
class TestHomePageAsLoggedInUser:
    def soup(self, client):
        response = client.get("/")
        return BeautifulSoup(response.content, "html.parser")

    def test_user_sees_all_reviews_if_does_not_follow_any_authors(
        self, client, first_user, night_patrol, sound_of_falling
    ):
        client.force_login(first_user)
        soup = self.soup(client)
        reviews = soup.find_all("div", {"class": "review"})
        assert len(reviews) == 2

    def test_user_sees_only_reviews_of_authors_he_follows(
        self, client, first_user, night_patrol, sound_of_falling
    ):
        night_patrol.author.follow(first_user)
        client.force_login(first_user)
        soup = self.soup(client)
        reviews = soup.find_all("div", {"class": "review"})
        assert len(reviews) == 1
        titles = [review.find("h2").string for review in reviews]
        assert night_patrol.title in titles
        assert sound_of_falling.title not in titles

    def test_each_user_sees_reviews_by_author_he_follows(
        self, client, first_user, second_user, night_patrol, sound_of_falling
    ):
        night_patrol.author.follow(first_user)
        sound_of_falling.author.follow(second_user)

        client.force_login(first_user)
        soup = self.soup(client)
        reviews = soup.find_all("div", {"class": "review"})
        assert len(reviews) == 1
        titles = [review.find("h2").string for review in reviews]
        assert night_patrol.title in titles
        assert sound_of_falling.title not in titles

        client.force_login(second_user)
        soup = self.soup(client)
        reviews = soup.find_all("div", {"class": "review"})
        assert len(reviews) == 1
        titles = [review.find("h2").string for review in reviews]
        assert sound_of_falling.title in titles
        assert night_patrol.title not in titles


@pytest.mark.django_db
class TestFullFeed:
    def soup(self, client):
        response = client.get("/all/")
        return BeautifulSoup(response.content, "html.parser")

    def test_uses_home_page_template(self, client):
        response = client.get("/all/")
        asserts.assertTemplateUsed(response, "reviews/home_page.html")

    def test_user_subscribed_to_one_author_sees_full_feed_anyway(
        self, client, first_user, night_patrol, sound_of_falling
    ):
        night_patrol.author.follow(first_user)
        client.force_login(first_user)
        soup = self.soup(client)
        reviews = soup.find_all("div", {"class": "review"})
        assert len(reviews) == 2
        titles = [review.find("h2").string for review in reviews]
        assert night_patrol.title in titles
        assert sound_of_falling.title in titles


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
        return self.prepare_soup(client, mzs)

    def prepare_soup(self, client, author):
        response = client.get(f"/{author.slug}/")
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

    def test_follow_button_is_present_if_user_is_logged_in(
        self, client, mzs, first_user
    ):
        client.force_login(first_user)
        soup = self.prepare_soup(client, mzs)
        follow_button = soup.find("a", {"class": "follow-button"})
        assert follow_button is not None

    def test_follow_button_is_not_present_if_user_is_logged_out(self, soup):
        follow_button = soup.find("a", {"class": "follow-button"})
        assert follow_button is None

    def test_follow_button_is_not_present_if_user_already_follows_author(
        self, client, mzs, first_user
    ):
        mzs.follow(first_user)
        client.force_login(first_user)
        soup = self.prepare_soup(client, mzs)
        follow_button = soup.find("a", {"class": "follow-button"})
        assert follow_button is None

    def test_unfollow_button_is_not_present_if_user_is_logged_out(self, soup):
        unfollow_button = soup.find("a", {"class": "unfollow-button"})
        assert unfollow_button is None

    def test_unfollow_button_is_not_present_if_user_does_not_follow_author(
        self, client, mzs, first_user
    ):
        client.force_login(first_user)
        soup = self.prepare_soup(client, mzs)
        unfollow_button = soup.find("a", {"class": "unfollow-button"})
        assert unfollow_button is None

    def test_unfollow_button_is_present_if_user_follows_author(
        self, client, mzs, first_user
    ):
        mzs.follow(first_user)
        client.force_login(first_user)
        soup = self.prepare_soup(client, mzs)
        unfollow_button = soup.find("a", {"class": "unfollow-button"})
        assert unfollow_button is not None


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

    def test_authors_are_ordered_by_last_name(self, soup, mzs, sheila):
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


@pytest.mark.django_db
class TestSearch:
    @pytest.fixture(autouse=True)
    def populate_db(self, mzs, sheila, night_patrol, king_of_color, sound_of_falling):
        pass

    def soup(self, client, search_term=""):
        response = client.get(f"/search/?q={search_term}")
        return BeautifulSoup(response.content, "html.parser")

    def test_uses_search_results_template(self, client):
        response = client.get("/search/")
        asserts.assertTemplateUsed(response, "reviews/search_results.html")

    def test_no_matches_for_search_term(self, client):
        soup = self.soup(client, search_term="hello")
        assert soup.find("p", {"data-testid": "no-search-results"}) is not None

    def test_no_matches_for_empty_search_term(self, client):
        soup = self.soup(client, search_term="")
        assert soup.find("p", {"data-testid": "no-search-results"}) is not None

    def test_one_match_for_authors_none_for_titles(self, client):
        soup = self.soup(client, search_term="Seitz")
        assert soup.find("p", string="Found in authors: 1") is not None
        assert soup.find("p", string="Found in titles: 0") is None

    def test_found_authors_are_listed_and_ordered_by_last_name(
        self, client, mzs, sheila
    ):
        soup = self.soup(client, search_term="ma")
        assert soup.find("p", string="Found in authors: 2") is not None
        list_of_authors = soup.find("ul", {"class": "author-list"})
        assert list_of_authors is not None
        assert len(list_of_authors.find_all("li")) == 2
        for author in list_of_authors.find_all("li"):
            name = author.find("a")
            assert name is not None
            assert name.string in [mzs.name, sheila.name]
        listed_authors = [
            author.find("a").string for author in list_of_authors.find_all("li")
        ]
        assert listed_authors == sorted(
            listed_authors, key=lambda author: author.split()[-1]
        )

    def test_found_reviews_are_listed(self, client, sound_of_falling, king_of_color):
        soup = self.soup(client, search_term="ing")
        assert soup.find("p", string="Found in titles: 2") is not None
        reviews = soup.find_all("div", {"class": "review"})
        assert len(reviews) == 2

        for review in reviews:
            title = review.find("h2")
            assert title is not None
            assert title.string in [sound_of_falling.title, king_of_color.title]
