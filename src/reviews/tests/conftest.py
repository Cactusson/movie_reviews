import datetime

import pytest

from reviews.models import Author, Review


@pytest.fixture
def mzs(db):
    return Author.objects.create(name="Matt Zoller Seitz")


@pytest.fixture
def night_patrol(db, mzs):
    return Review.objects.create(
        title="Night Patrol",
        author=mzs,
        url="https://www.rogerebert.com/reviews/night-patrol-shudder-film-review-2026",
        date=datetime.date(2026, 1, 19),
        content="...",
    )
