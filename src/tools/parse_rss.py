import datetime

import feedparser
import requests
from django.utils import timezone

from reviews.models import Author, Review


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
            review = Review(
                title=entry.title,
                author=author,
                url=entry.link,
                date=date,
                content=entry.content,
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
