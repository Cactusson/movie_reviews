from django.contrib.auth import views as auth_views
from django.urls import path

from accounts import views

app_name = "accounts"
urlpatterns = [
    path("send_login_email/", views.send_login_email, name="send_login_email"),
    path("login/", views.login, name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
]
