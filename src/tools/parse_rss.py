import datetime
import re

import feedparser
import requests
from django.utils import timezone

from reviews.models import Author, Review

INDIEWIRE_TITLE_PATTERN = re.compile(r"^‘(.*?)’ Review: ")


def extract_title(entry: feedparser.util.FeedParserDict) -> str:
    assert type(entry.title) is str
    if (
        "indiewire" in entry.link
        and INDIEWIRE_TITLE_PATTERN.search(entry.title) is not None
    ):
        return INDIEWIRE_TITLE_PATTERN.search(entry.title).group(1)
    else:
        return entry.title


def parse_full_rss_feed(url: str, ignore_cutoff_date: bool = False) -> list[Review]:
    if not url.endswith("/"):
        url += "/"
    new_reviews = []
    page = 1

    cutoff_date = timezone.now() - datetime.timedelta(days=7)

    while True:
        entries_from_current_page = parse_one_rss_page(url, page=page)
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
            title = extract_title(entry)
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


def parse_one_rss_page(url: str, page: int = 1) -> list[feedparser.util.FeedParserDict]:
    response = requests.get(url, timeout=10, params={"paged": page})
    response.raise_for_status()
    feed = feedparser.parse(response.content)
    return feed.entries
