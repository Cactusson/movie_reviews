import datetime
from dataclasses import dataclass

import feedparser
import requests


@dataclass
class Review:
    title: str
    author: str
    url: str
    date: datetime.date
    content: str | None


def parse_full_rss_feed(url: str) -> list[Review]:
    entries = []
    page = 1
    while True:
        entries_from_current_page = parse_one_rss_page(url, page=page)
        if len(entries_from_current_page) == 0:
            return entries
        entries.extend(entries_from_current_page)
        page += 1


def parse_one_rss_page(url: str, page: int = 1) -> list[Review]:
    response = requests.get(url, timeout=10, params={"paged": page})
    response.raise_for_status()
    feed = feedparser.parse(response.content)
    return [
        Review(
            title=entry.title,
            author=entry.author,
            url=entry.link,
            date=datetime.datetime.strptime(
                entry.published, "%a, %d %b %Y %H:%M:%S %z"
            ).date(),
            content=entry.content,
        )
        for entry in feed.entries
    ]
