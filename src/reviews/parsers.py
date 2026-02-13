import datetime
import re
from abc import ABC

import feedparser
import requests
from django.conf import settings
from django.utils import timezone

from reviews.models import Author, Review

MOVIE_TITLE_PATTERN = re.compile(r"^‘(.*?)’ Review: ")


def collect_parsers() -> list[tuple[str, type[Parser]]]:
    parsers = []
    for url, parser_class in settings.RSS_PARSERS.items():
        if parser_class not in globals():
            raise ValueError(f"Parser `{parser_class}` was not found.")
        parsers.append((url, globals()[parser_class]))
    return parsers


def collect_movies_from_feeds(ignore_cutoff_date: bool = False) -> list[Review]:
    new_reviews = []
    for url, parser_class in collect_parsers():
        parser = parser_class()
        reviews = parser.parse_full_rss_feed(url, ignore_cutoff_date)
        new_reviews.extend(reviews)
    return new_reviews


class Parser(ABC):
    def parse_full_rss_feed(
        self, url: str, ignore_cutoff_date: bool = False
    ) -> list[Review]:
        if not url.endswith("/"):
            url += "/"
        new_reviews = []
        page = 1

        cutoff_date = timezone.now() - datetime.timedelta(days=7)

        while True:
            entries_from_current_page = self.parse_one_rss_page(url, page=page)
            if len(entries_from_current_page) == 0:
                return new_reviews

            for entry in entries_from_current_page:
                assert type(entry.published) is str  # to make mypy happy
                date = datetime.datetime.strptime(
                    entry.published, "%a, %d %b %Y %H:%M:%S %z"
                )
                if not ignore_cutoff_date and date < cutoff_date:
                    return new_reviews
                author = Author.objects.get_or_create(name=entry.author)[0]
                title = self.extract_title(entry)
                content = entry.get("content", None)
                if content is not None:
                    content = content[0]["value"]
                review = Review(
                    title=title,
                    author=author,
                    url=entry.link,
                    date=date,
                    content=content,
                )
                if not Review.objects.filter(
                    title=review.title,
                    author=review.author,
                    url=review.url,
                    date=review.date,
                ).exists():
                    review.save()
                    new_reviews.append(review)
            page += 1

    def parse_one_rss_page(
        self, url: str, page: int = 1
    ) -> list[feedparser.util.FeedParserDict]:
        response = requests.get(url, timeout=10, params={"paged": page})
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        return feed.entries

    def extract_title(self, entry: feedparser.util.FeedParserDict) -> str:
        assert type(entry.title) is str
        return entry.title


class RogerEbertParser(Parser):
    pass


class IndieWireParser(Parser):
    def extract_title(self, entry: feedparser.FeedParserDict) -> str:
        assert type(entry.title) is str
        match = MOVIE_TITLE_PATTERN.search(entry.title)
        if match is not None:
            return match.group(1)
        else:
            return entry.title
