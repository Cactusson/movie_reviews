import pytest

from reviews.models import Review
from tools.parse_rss import parse_full_rss_feed, parse_one_rss_page


@pytest.mark.django_db
class TestRSSParser:
    def test_all_10_entries_are_retrieved(self, mocked_rss_feed):
        entries = parse_one_rss_page("https://www.rogerebert.com/reviews/feed/")
        assert len(entries) == 10

    def test_no_entries_retrieved_from_empty_feed(self, mocked_rss_feed):
        entries = parse_one_rss_page("https://www.rogerebert.com/reviews/feed/", 3)
        assert len(entries) == 0

    def test_first_entry_is_correct(self, mocked_rss_feed):
        first_entry = parse_one_rss_page("https://www.rogerebert.com/reviews/feed/")[0]
        assert first_entry.title == "The Moment"
        assert first_entry.author == "Monica Castillo"
        assert (
            first_entry.link
            == "https://www.rogerebert.com/reviews/the-moment-charli-xcx-film-review-2026"
        )
        assert first_entry.published == "Sun, 25 Jan 2026 05:28:44 +0000"
        assert first_entry.content

    def test_all_20_entries_are_retrieved_from_full_feed(self, mocked_rss_feed):
        entries = parse_full_rss_feed("https://www.rogerebert.com/reviews/feed/")
        assert len(entries) == 20

    def test_20_new_reviews_saved_in_database_after_parsing(self, mocked_rss_feed):
        assert Review.objects.count() == 0
        parse_full_rss_feed("https://www.rogerebert.com/reviews/feed/")
        assert Review.objects.count() == 20

    def test_parser_will_not_return_any_entries_if_ran_again(self, mocked_rss_feed):
        parse_full_rss_feed("https://www.rogerebert.com/reviews/feed/")
        entries = parse_full_rss_feed("https://www.rogerebert.com/reviews/feed/")
        assert len(entries) == 0

    def test_parser_will_not_stop_at_duplicate_entry(self, mocked_rss_feed):
        """
        Sometimes there are duplicate entries in the RSS feed.
        At first the parser was configured to stop if it encounters one.
        This test makes sure the parser's configuration is up to date.
        """
        assert Review.objects.count() == 0
        entries = parse_full_rss_feed(
            "https://www.rogerebert.com/reviews/feed_with_duplicates/"
        )
        assert len(entries) == 2
        assert Review.objects.count() == 2

    def test_parser_will_ignore_old_entries(self, mocked_rss_feed):
        """
        Parser should stop if it encounters an entry a week old
        (the time period may change in the future)
        """
        assert Review.objects.count() == 0
        entries = parse_full_rss_feed(
            "https://www.rogerebert.com/reviews/feed_with_old_entries/"
        )
        assert len(entries) == 1
        assert Review.objects.count() == 1
