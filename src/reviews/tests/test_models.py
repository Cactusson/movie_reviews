import pytest
from django.core.exceptions import ValidationError

from reviews.models import Author, Review


@pytest.mark.django_db
class TestReviewModel:
    def test_title_is_required(self):
        review = Review()
        with pytest.raises(ValidationError):
            review.save()

    # def test_author_is_required(self):
    #     review = Review(title="Night Patrol")
    #     with pytest.raises(ValidationError):
    #         review.save()


@pytest.mark.django_db
class TestAuthorModel:
    def test_name_is_required(self):
        author = Author()
        with pytest.raises(ValidationError):
            author.save()
