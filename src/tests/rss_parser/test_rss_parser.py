import datetime

from tools.parse_rss import Review, parse_full_rss_feed, parse_one_rss_page


class TestRSSParser:
    def test_all_10_entries_are_retrieved(self, mocked_rss_feed):
        entries = parse_one_rss_page("https://www.rogerebert.com/reviews/feed/")
        assert len(entries) == 10

    def test_no_entries_retrieved_from_empty_feed(self, mocked_rss_feed):
        entries = parse_one_rss_page("https://www.rogerebert.com/reviews/feed/", 3)
        assert len(entries) == 0

    def test_first_entry_is_correct(self, mocked_rss_feed):
        first_entry = parse_one_rss_page("https://www.rogerebert.com/reviews/feed/")[0]
        assert type(first_entry) is Review
        assert first_entry.title == "The Moment"
        assert first_entry.author == "Monica Castillo"
        assert (
            first_entry.url
            == "https://www.rogerebert.com/reviews/the-moment-charli-xcx-film-review-2026"
        )
        assert first_entry.date == datetime.date(2026, 1, 25)
        assert first_entry.content

    def test_all_20_entries_are_retrieved_from_full_feed(self, mocked_rss_feed):
        entries = parse_full_rss_feed("https://www.rogerebert.com/reviews/feed/")
        assert len(entries) == 20
