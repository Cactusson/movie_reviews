from django.urls import path

from . import views

app_name = "reviews"
urlpatterns = [
    path("", views.home_page, name="home_page"),
    path("all/", views.full_feed, name="full_feed"),
    path("<int:pk>/", views.review_detail, name="review_detail"),
    path("search/", views.search, name="search"),
    path("profile/", views.profile, name="profile"),
    path("letterboxd/", views.letterboxd, name="letterboxd"),
    path("authors/", views.author_list, name="author_list"),
    path("<str:slug>/", views.author_detail, name="author_detail"),
    path("<str:slug>/follow/", views.author_follow, name="author_follow"),
    path("<str:slug>/unfollow/", views.author_unfollow, name="author_unfollow"),
]
