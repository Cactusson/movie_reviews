import datetime

import pytest

from reviews.models import Author, Review


@pytest.fixture
def mzs(db):
    return Author.objects.create(name="Matt Zoller Seitz")


@pytest.fixture
def sheila(db):
    return Author.objects.create(name="Sheila O'Malley")


@pytest.fixture
def night_patrol(db, mzs):
    return Review.objects.create(
        title="Night Patrol",
        author=mzs,
        url="https://www.rogerebert.com/reviews/night-patrol-shudder-film-review-2026",
        date=datetime.date(2026, 1, 19),
        content="...",
    )


@pytest.fixture
def sound_of_falling(db, sheila):
    return Review.objects.create(
        title="Sound of Falling",
        author=sheila,
        url="https://www.rogerebert.com/reviews/sound-of-falling-mubi-movie-review-2026",
        date=datetime.date(2026, 1, 16),
        content="...",
    )


@pytest.fixture
def king_of_color(db, mzs):
    return Review.objects.create(
        title="The King of Color",
        author=mzs,
        url="https://www.rogerebert.com/reviews/the-king-of-color-documentary-film-review-2025",
        date=datetime.date(2025, 12, 12),
        content="...",
    )
