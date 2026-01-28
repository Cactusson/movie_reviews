from django.urls import path

from . import views

app_name = "reviews"
urlpatterns = [
    path("", views.home_page, name="home_page"),
    path("<int:pk>/", views.review_detail, name="review_detail"),
    path("search/", views.search, name="search"),
    path("authors/", views.author_list, name="author_list"),
    path("<str:slug>/", views.author_detail, name="author_detail"),
]
