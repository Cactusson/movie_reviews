from unittest.mock import patch

import pytest
from django.test import override_settings

from reviews.models import Review
from reviews.parsers import IndieWireParser, Parser, collect_movies_from_feeds


@patch.multiple(Parser, __abstractmethods__=set())
@pytest.mark.django_db
class TestParser:
    @pytest.fixture
    def parser(self):
        return Parser()

    @pytest.mark.asyncio
    async def test_all_10_entries_are_retrieved(self, parser, mocked_rss_feed):
        entries = await parser.parse_one_rss_page(
            "https://www.rogerebert.com/reviews/feed/"
        )
        assert len(entries) == 10

    @pytest.mark.asyncio
    async def test_no_entries_retrieved_from_empty_feed(self, parser, mocked_rss_feed):
        entries = await parser.parse_one_rss_page(
            "https://www.rogerebert.com/reviews/feed/", 3
        )
        assert len(entries) == 0

    @pytest.mark.asyncio
    async def test_first_entry_is_correct(self, parser, mocked_rss_feed):
        entries = await parser.parse_one_rss_page(
            "https://www.rogerebert.com/reviews/feed/"
        )
        first_entry = entries[0]
        assert first_entry.title == "The Moment"
        assert first_entry.author == "Monica Castillo"
        assert (
            first_entry.link
            == "https://www.rogerebert.com/reviews/the-moment-charli-xcx-film-review-2026"
        )
        assert first_entry.published == "Sun, 25 Jan 2026 05:28:44 +0000"

    @pytest.mark.asyncio
    async def test_all_20_entries_are_retrieved_from_full_feed(
        self, parser, mocked_rss_feed
    ):
        entries = await parser.parse_full_rss_feed(
            "https://www.rogerebert.com/reviews/feed/"
        )
        assert len(entries) == 20

    @override_settings(
        RSS_PARSERS={"https://www.rogerebert.com/reviews/feed/": "RogerEbertParser"}
    )
    def test_20_new_reviews_saved_in_database_after_parsing(
        self, parser, mocked_rss_feed
    ):
        assert Review.objects.count() == 0
        collect_movies_from_feeds()
        assert Review.objects.count() == 20

    # @override_settings(
    #     RSS_PARSERS={"https://www.rogerebert.com/reviews/feed/": "RogerEbertParser"}
    # )
    # @pytest.mark.asyncio
    # async def test_parser_will_not_return_any_entries_if_run_again(
    #     self, parser, mocked_rss_feed
    # ):
    #     collect_movies_from_feeds()
    #     entries = await parser.parse_full_rss_feed(
    #         "https://www.rogerebert.com/reviews/feed/"
    #     )
    #     assert len(entries) == 0

    @override_settings(
        RSS_PARSERS={
            "https://www.rogerebert.com/reviews/feed_with_duplicates/": "RogerEbertParser"
        }
    )
    def test_parser_will_not_stop_at_duplicate_entry(self, parser, mocked_rss_feed):
        """
        Sometimes there are duplicate entries in the RSS feed.
        At first the parser was configured to stop if it encounters one.
        This test makes sure the parser's configuration is up to date.
        """
        assert Review.objects.count() == 0
        collect_movies_from_feeds()
        assert Review.objects.count() == 2

    @override_settings(
        RSS_PARSERS={
            "https://www.rogerebert.com/reviews/feed_with_old_entries/": "RogerEbertParser"
        }
    )
    def test_parser_will_ignore_old_entries(self, parser, mocked_rss_feed):
        """
        Parser should stop if it encounters an entry a week old
        (the time period may change in the future)
        """
        assert Review.objects.count() == 0
        collect_movies_from_feeds()
        assert Review.objects.count() == 1

    @override_settings(
        CUTOFF_YEAR=2021,
        RSS_PARSERS={
            "https://www.rogerebert.com/reviews/feed_cutoff_date/": "RogerEbertParser"
        },
    )
    def test_parser_will_stop_after_cutoff_year(self, parser, mocked_rss_feed):
        assert Review.objects.count() == 0
        collect_movies_from_feeds(ignore_cutoff_date=True)
        assert Review.objects.count() == 1


@pytest.mark.django_db
class TestIndieWireParser:
    @pytest.fixture
    def parser(self):
        return IndieWireParser()

    @pytest.mark.asyncio
    async def test_parser_will_extract_movie_title_from_indiewire_entry(
        self, parser, mocked_rss_feed
    ):
        """
        &#8216;The Gallerist&#8217; Review: Natalie Portman Takes Cheap Shots at the Art World in a Schematic, Unfunny Satire
        to
        The Gallerist
        """
        entries = await parser.parse_full_rss_feed(
            "https://www.indiewire.com/c/criticism/movies/feed/"
        )
        assert len(entries) == 12
        assert entries[0].title == "The Gallerist"
        assert entries[1].title == "Bedford Park"

    @pytest.mark.asyncio
    async def test_parser_will_ignore_not_reviews(self, parser, mocked_rss_feed):
        entries = await parser.parse_full_rss_feed(
            "https://www.indiewire.com/c/criticism/movies/feed_with_not_reviews/"
        )
        assert len(entries) == 11
