import asyncio
import datetime
import re
from abc import ABC
from dataclasses import dataclass
from typing import cast

import aiohttp
import feedparser
from django.conf import settings
from django.utils import timezone
from feedparser.util import FeedParserDict

from reviews.models import Author, LetterboxdUser, ParserControl, Review
from reviews.notifications import notify_users


@dataclass
class Entry:
    author: str
    title: str
    url: str
    date: datetime.date


def collect_parsers() -> list[tuple[str, type[Parser]]]:
    parsers = []
    for url, parser_class in settings.RSS_PARSERS.items():
        if parser_class not in globals():
            raise ValueError(f"Parser `{parser_class}` was not found.")
        parsers.append((url, globals()[parser_class]))
    return parsers


def collect_movies_from_feeds(
    ignore_cutoff_date: bool = False,
) -> list[Review]:
    if ParserControl.is_parsing_running():
        print("Parser is already running.")
        return []

    try:
        ParserControl.start_running()
        new_reviews: list[Review] = []
        entries = asyncio.run(collect_movies_from_feeds_async(ignore_cutoff_date))
        for entry in entries:
            author = Author.objects.get_or_create(name=entry.author)[0]
            review, created = Review.objects.get_or_create(
                title=entry.title,
                author=author,
                url=entry.url,
                date=entry.date,
            )
            if created:
                new_reviews.append(review)

        notify_users(new_reviews)
        update_letterboxd_entries()

        return new_reviews
    finally:
        ParserControl.stop_running()


def update_letterboxd_entries():
    for letterboxd_user in LetterboxdUser.objects.all():
        letterboxd_user.parse_letterboxd_rss()


async def collect_movies_from_feeds_async(ignore_cutoff_date: bool) -> list[Entry]:
    tasks = [
        parser_class().parse_full_rss_feed(url, ignore_cutoff_date)
        for url, parser_class in collect_parsers()
    ]
    results = await asyncio.gather(*tasks)
    return [entry for entries in results for entry in entries]


class Parser(ABC):
    async def parse_full_rss_feed(
        self, url: str, ignore_cutoff_date: bool = False
    ) -> list[Entry]:
        if not url.endswith("/"):
            url += "/"
        new_entries: list[Entry] = []
        page = 1

        cutoff_date = timezone.now() - datetime.timedelta(days=7)

        while True:
            entries_from_current_page = await self.parse_one_rss_page(url, page=page)
            if len(entries_from_current_page) == 0:
                return new_entries

            for entry in entries_from_current_page:
                if not self.is_entry_a_review(entry):
                    continue
                assert type(entry.published) is str  # to make mypy happy
                date = datetime.datetime.strptime(
                    entry.published, "%a, %d %b %Y %H:%M:%S %z"
                )
                if date.year < settings.CUTOFF_YEAR or (
                    not ignore_cutoff_date and date < cutoff_date
                ):
                    return new_entries
                if entry.author:
                    new_entry = Entry(
                        author=self.extract_author(entry),
                        title=self.extract_title(entry),
                        url=self.extract_url(entry),
                        date=date,
                    )
                    new_entries.append(new_entry)
            page += 1

    async def parse_one_rss_page(self, url: str, page: int = 1) -> list[FeedParserDict]:
        max_retries = 2
        async with aiohttp.ClientSession() as session:
            for _ in range(max_retries + 1):
                async with session.get(url, params={"paged": page}) as response:
                    if response.status == 404:
                        return []
                    if response.status >= 500:
                        await asyncio.sleep(10)
                        continue
                    response.raise_for_status()
                    feed = feedparser.parse(await response.text())
                    return cast(list[FeedParserDict], feed.entries)
        return []

    def extract_author(self, entry: FeedParserDict) -> str:
        assert type(entry.author) is str
        return entry.author

    def extract_title(self, entry: FeedParserDict) -> str:
        assert type(entry.title) is str
        return entry.title

    def extract_url(self, entry: FeedParserDict) -> str:
        assert type(entry.link) is str
        return entry.link

    def is_entry_a_review(self, entry: FeedParserDict) -> bool:
        return True


class RogerEbertParser(Parser):
    pass


class IndieWireParser(Parser):
    MOVIE_TITLE_PATTERN = re.compile(r"^(‘|’)(.*?)’ Review: ")

    def extract_title(self, entry: FeedParserDict) -> str:
        assert type(entry.title) is str
        match = self.MOVIE_TITLE_PATTERN.search(entry.title)
        if match is not None:
            return match.group(2)
        else:
            return entry.title

    def is_entry_a_review(self, entry: FeedParserDict) -> bool:
        assert type(entry.title) is str
        return self.MOVIE_TITLE_PATTERN.search(entry.title) is not None


class LarsenOnFilmParser(Parser):
    def extract_author(self, entry: FeedParserDict) -> str:
        return "Josh Larsen"

    def is_entry_a_review(self, entry: FeedParserDict) -> bool:
        return "Top Ten Films of " not in entry.title


class MovieBloggerParser(Parser):
    MOVIE_TITLE_PATTERN_1 = re.compile(r"^(.*?) \(\d{4}\) Film Review")
    MOVIE_TITLE_PATTERN_2 = re.compile(r"^Movie Review: (.*?) \(\d{4}\)")

    def extract_title(self, entry: FeedParserDict) -> str:
        assert type(entry.title) is str
        match = self.MOVIE_TITLE_PATTERN_1.search(entry.title)
        if match is not None:
            return match.group(1)
        else:
            match = self.MOVIE_TITLE_PATTERN_2.search(entry.title)
            if match is not None:
                return match.group(1)
            else:
                return entry.title

    def extract_url(self, entry: FeedParserDict) -> str:
        assert type(entry.link) is str
        if "?utm" in entry.link:
            return entry.link[: entry.link.index("?utm")]
        return entry.link

    def is_entry_a_review(self, entry: FeedParserDict) -> bool:
        return "Short Film Review" not in entry.title and "TV Review" not in entry.title


class ThePlaylistParser(IndieWireParser):
    pass
