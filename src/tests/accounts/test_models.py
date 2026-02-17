import pytest
from django.contrib import auth
from django.core.exceptions import ValidationError

from accounts.models import CustomUser, Token


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


@pytest.mark.django_db
class TestTokenModel:
    def test_tokens_are_different(self):
        token1 = Token.objects.create(email="test@example.com")
        token2 = Token.objects.create(email="test@example.com")
        assert token1.uuid != token2.uuid
