from django.contrib import auth, messages
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse

from accounts.models import Token


def send_login_email(request):
    email = request.POST["email"]
    token = Token.objects.create(email=email)
    url = request.build_absolute_uri(
        reverse("accounts:login") + "?token=" + str(token.uuid)
    )
    message_body = f"Use this link to log in:\n\n{url}"
    send_mail(
        "Your Login Link for Movie Reviews",
        message_body,
        "noreply@movie_reviews",
        [email],
    )
    messages.success(
        request, "Check your email, we've sent you a link you can use to log in."
    )
    return redirect("/")


def login(request):
    if user := auth.authenticate(uuid=request.GET["token"]):
        auth.login(request, user)
    else:
        messages.error(request, "Invalid login link, please request a new one")
    return redirect("/")
