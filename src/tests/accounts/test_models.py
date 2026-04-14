import pytest
from django.contrib import auth
from django.core.exceptions import ValidationError

from accounts.models import CustomUser, Token
from reviews.models import LetterboxdUser


@pytest.mark.django_db
class TestCustomUserModel:
    def test_email_is_required(self):
        user = CustomUser()
        with pytest.raises(ValidationError):
            user.full_clean()

    def test_model_is_configured_for_django_auth(self):
        assert auth.get_user_model() == CustomUser

    def test_user_is_valid_with_email_only(self):
        CustomUser.objects.create(email="test@example.com")
        assert CustomUser.objects.count() == 1

    def test_email_is_primary_key(self):
        user = CustomUser(email="test@example.com")
        assert user.pk == "test@example.com"

    def test_two_users_can_have_same_letterboxd_account(self, mocked_letterboxd_feed):
        first_user = CustomUser.objects.create(email="first@example.com")
        second_user = CustomUser.objects.create(email="second@example.com")
        letterboxd_user = LetterboxdUser.objects.create(name="alice")
        first_user.letterboxd_user = letterboxd_user
        first_user.save()
        second_user.letterboxd_user = letterboxd_user
        second_user.save()  # does not raise an error


@pytest.mark.django_db
class TestTokenModel:
    def test_tokens_are_different(self):
        token1 = Token.objects.create(email="test@example.com")
        token2 = Token.objects.create(email="test@example.com")
        assert token1.uuid != token2.uuid
