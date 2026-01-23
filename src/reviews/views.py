from django.shortcuts import render

from reviews.models import Review


def home_page(request):
    context = {"reviews": Review.objects.all()}
    print(context["reviews"])
    return render(request, "reviews/home_page.html", context)
