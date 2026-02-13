from unittest.mock import patch

import pytest

from reviews.models import Review
from reviews.parsers import IndieWireParser, Parser


@patch.multiple(Parser, __abstractmethods__=set())
@pytest.mark.django_db
class TestParser:
    @pytest.fixture
    def parser(self):
        return Parser()

    def test_all_10_entries_are_retrieved(self, parser, mocked_rss_feed):
        entries = parser.parse_one_rss_page("https://www.rogerebert.com/reviews/feed/")
        assert len(entries) == 10

    def test_no_entries_retrieved_from_empty_feed(self, parser, mocked_rss_feed):
        entries = parser.parse_one_rss_page(
            "https://www.rogerebert.com/reviews/feed/", 3
        )
        assert len(entries) == 0

    def test_first_entry_is_correct(self, parser, mocked_rss_feed):
        first_entry = parser.parse_one_rss_page(
            "https://www.rogerebert.com/reviews/feed/"
        )[0]
        assert first_entry.title == "The Moment"
        assert first_entry.author == "Monica Castillo"
        assert (
            first_entry.link
            == "https://www.rogerebert.com/reviews/the-moment-charli-xcx-film-review-2026"
        )
        assert first_entry.published == "Sun, 25 Jan 2026 05:28:44 +0000"
        assert first_entry.content

    def test_all_20_entries_are_retrieved_from_full_feed(self, parser, mocked_rss_feed):
        entries = parser.parse_full_rss_feed("https://www.rogerebert.com/reviews/feed/")
        assert len(entries) == 20

    def test_20_new_reviews_saved_in_database_after_parsing(
        self, parser, mocked_rss_feed
    ):
        assert Review.objects.count() == 0
        parser.parse_full_rss_feed("https://www.rogerebert.com/reviews/feed/")
        assert Review.objects.count() == 20

    def test_parser_will_not_return_any_entries_if_ran_again(
        self, parser, mocked_rss_feed
    ):
        parser.parse_full_rss_feed("https://www.rogerebert.com/reviews/feed/")
        entries = parser.parse_full_rss_feed("https://www.rogerebert.com/reviews/feed/")
        assert len(entries) == 0

    def test_parser_will_not_stop_at_duplicate_entry(self, parser, mocked_rss_feed):
        """
        Sometimes there are duplicate entries in the RSS feed.
        At first the parser was configured to stop if it encounters one.
        This test makes sure the parser's configuration is up to date.
        """
        assert Review.objects.count() == 0
        entries = parser.parse_full_rss_feed(
            "https://www.rogerebert.com/reviews/feed_with_duplicates/"
        )
        assert len(entries) == 2
        assert Review.objects.count() == 2

    def test_parser_will_ignore_old_entries(self, parser, mocked_rss_feed):
        """
        Parser should stop if it encounters an entry a week old
        (the time period may change in the future)
        """
        assert Review.objects.count() == 0
        entries = parser.parse_full_rss_feed(
            "https://www.rogerebert.com/reviews/feed_with_old_entries/"
        )
        assert len(entries) == 1
        assert Review.objects.count() == 1

    def test_content_is_optional(self, parser, mocked_rss_feed):
        entries = parser.parse_full_rss_feed(
            "https://www.indiewire.com/c/criticism/movies/feed/"
        )
        for entry in entries:
            assert entry.content is None


@pytest.mark.django_db
class TestIndieWireParser:
    @pytest.fixture
    def parser(self):
        return IndieWireParser()

    def test_parser_will_extract_movie_title_from_indiewire_entry(
        self, parser, mocked_rss_feed
    ):
        """
        &#8216;The Gallerist&#8217; Review: Natalie Portman Takes Cheap Shots at the Art World in a Schematic, Unfunny Satire
        to
        The Gallerist
        """
        entries = parser.parse_full_rss_feed(
            "https://www.indiewire.com/c/criticism/movies/feed/"
        )
        assert len(entries) == 12
        assert entries[0].title == "The Gallerist"
        assert entries[1].title == "Bedford Park"
