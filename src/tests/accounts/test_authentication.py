import uuid

import pytest
from django.http import HttpRequest

from accounts.authentication import PasswordlessAuthenticationBackend
from accounts.models import CustomUser, Token


@pytest.mark.django_db
class TestAuthenticate:
    def test_returns_None_if_no_such_token(self):
        result = PasswordlessAuthenticationBackend().authenticate(
            HttpRequest(), uuid.uuid4()
        )
        assert result is None

    def test_returns_new_user_with_correct_email_if_token_exists(self):
        email = "test@example.com"
        token = Token.objects.create(email=email)
        user = PasswordlessAuthenticationBackend().authenticate(
            HttpRequest(), token.uuid
        )
        new_user = CustomUser.objects.get(email=email)
        assert user == new_user

    def test_returns_existing_user_with_correct_email_if_token_exists(self):
        email = "test@example.com"
        existing_user = CustomUser.objects.create(email=email)
        token = Token.objects.create(email=email)
        user = PasswordlessAuthenticationBackend().authenticate(
            HttpRequest(), token.uuid
        )
        assert user == existing_user


@pytest.mark.django_db
class TestGetUser:
    def test_gets_user_by_email(self):
        CustomUser.objects.create(email="first@example.com")
        desired_user = CustomUser.objects.create(email="second@example.com")
        found_user = PasswordlessAuthenticationBackend().get_user("second@example.com")
        assert found_user == desired_user

    def test_returns_None_if_no_user_with_that_email(self):
        assert PasswordlessAuthenticationBackend().get_user("test@example.com") is None
