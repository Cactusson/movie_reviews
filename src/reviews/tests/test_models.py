import datetime

import pytest
from django.core.exceptions import ValidationError

from reviews.models import Author, Review


@pytest.mark.django_db
class TestReviewModel:
    def test_title_is_required(self, mzs):
        review = Review(
            author=mzs,
            url="https://www.rogerebert.com/reviews/night-patrol-shudder-film-review-2026",
            date=datetime.date(2026, 1, 19),
            content="...",
        )
        with pytest.raises(ValidationError):
            review.save()

    def test_author_is_required(self):
        review = Review(
            title="Night Patrol",
            url="https://www.rogerebert.com/reviews/night-patrol-shudder-film-review-2026",
            date=datetime.date(2026, 1, 19),
            content="...",
        )
        with pytest.raises(ValidationError):
            review.save()

    def test_url_is_required(self, mzs):
        review = Review(
            author=mzs,
            title="Night Patrol",
            date=datetime.date(2026, 1, 19),
            content="...",
        )
        with pytest.raises(ValidationError):
            review.save()

    def test_date_is_required(self, mzs):
        review = Review(
            author=mzs,
            title="Night Patrol",
            url="https://www.rogerebert.com/reviews/night-patrol-shudder-film-review-2026",
            content="...",
        )
        with pytest.raises(ValidationError):
            review.save()

    def test_content_is_not_required(self, mzs):
        review = Review(
            title="Night Patrol",
            author=mzs,
            url="https://www.rogerebert.com/reviews/night-patrol-shudder-film-review-2026",
            date=datetime.date(2026, 1, 19),
        )
        review.save()  # does not raise an error

    def test_object_is_created_successfully(self, mzs):
        review = Review(
            title="Night Patrol",
            author=mzs,
            url="https://www.rogerebert.com/reviews/night-patrol-shudder-film-review-2026",
            date=datetime.date(2026, 1, 19),
            content="...",
        )
        review.save()  # does not raise an error

    def test_string_representation(self, night_patrol):
        assert str(night_patrol) == night_patrol.title

    def test_cannot_create_two_reviews_with_same_data(self, night_patrol):
        review = Review(
            title=night_patrol.title,
            author=night_patrol.author,
            url=night_patrol.url,
            date=night_patrol.date,
        )
        with pytest.raises(ValidationError):
            review.save()

    def test_content_is_none_by_default(self, mzs):
        review = Review.objects.create(
            title="Night Patrol",
            author=mzs,
            url="https://www.rogerebert.com/reviews/night-patrol-shudder-film-review-2026",
            date=datetime.date(2026, 1, 19),
        )
        assert review.content is None


@pytest.mark.django_db
class TestAuthorModel:
    def test_name_is_required(self):
        author = Author()
        with pytest.raises(ValidationError):
            author.save()

    def test_object_is_created_successfully(self):
        author = Author(name="Matt Zoller Seitz")
        author.save()  # does not raise an error

    def test_string_representation(self, mzs):
        assert str(mzs) == mzs.name

    def test_cannot_create_two_authors_with_same_name(self, mzs):
        author = Author(name=mzs.name)
        with pytest.raises(ValidationError):
            author.save()

    def test_author_is_related_to_review(self, night_patrol, mzs):
        assert mzs == night_patrol.author
