import uuid
from unittest import mock

import pytest
from django.contrib import auth
from pytest_django import asserts

from accounts.models import Token


@pytest.mark.django_db
class TestSendLoginEmailView:
    def test_redirects_to_home_page(self, client):
        response = client.post(
            "/accounts/send_login_email/", data={"email": "test@example.com"}
        )
        asserts.assertRedirects(response, "/")

    def test_adds_success_message(self, client):
        response = client.post(
            "/accounts/send_login_email/",
            data={"email": "test@example.com"},
            follow=True,
        )

        message = list(response.context["messages"])[0]
        assert (
            message.message
            == "Check your email, we've sent you a link you can use to log in."
        )
        assert message.tags == "success"

    @mock.patch("accounts.views.send_mail")
    def test_sends_mail_to_address_from_post(self, mock_send_mail, client):
        client.post("/accounts/send_login_email/", data={"email": "test@example.com"})

        assert mock_send_mail.called is True
        (subject, body, from_email, to_list), kwargs = mock_send_mail.call_args
        assert subject == "Your Login Link for Movie Reviews"
        assert from_email == "noreply@movie_reviews"
        assert to_list == ["test@example.com"]

    def test_creates_token_associated_with_email(self, client):
        client.post("/accounts/send_login_email/", data={"email": "test@example.com"})
        token = Token.objects.get()
        assert token.email == "test@example.com"

    @mock.patch("accounts.views.send_mail")
    def test_sends_link_to_login_using_token_uuid(self, mock_send_mail, client):
        client.post("/accounts/send_login_email/", data={"email": "test@example.com"})
        token = Token.objects.get()
        expected_url = f"http://testserver/accounts/login/?token={token.uuid}"
        (subject, body, from_email, to_list), kwargs = mock_send_mail.call_args
        assert expected_url in body


@pytest.mark.django_db
class TestLoginView:
    def test_redirects_to_home_page(self, client):
        response = client.get(f"/accounts/login/?token={uuid.uuid4()}")
        asserts.assertRedirects(response, "/")

    def test_logs_in_if_given_valid_token(self, client):
        anon_user = auth.get_user(client)
        assert not anon_user.is_authenticated

        token = Token.objects.create(email="test@example.com")
        client.get(f"/accounts/login/?token={token.uuid}")

        user = auth.get_user(client)
        assert anon_user != user
        assert user.is_authenticated
        assert user.email == "test@example.com"

    def test_shows_login_error_if_token_invalid(self, client):
        invalid_token = uuid.uuid4()
        response = client.get(f"/accounts/login/?token={invalid_token}", follow=True)
        user = auth.get_user(client)
        assert not user.is_authenticated
        message = list(response.context["messages"])[0]
        assert message.message == "Invalid login link, please request a new one"
        assert message.tags == "error"

    @mock.patch("accounts.views.auth")
    def test_calls_django_auth_authenticate(self, mock_auth, client):
        token = uuid.uuid4()
        client.get(f"/accounts/login/?token={token}")
        assert mock_auth.authenticate.call_args == mock.call(uuid=str(token))
