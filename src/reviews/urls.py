from django.urls import path

from . import views

app_name = "reviews"
urlpatterns = [
    path("", views.home_page, name="home_page"),
    path("<int:pk>/", views.review_detail, name="review_detail"),
]
