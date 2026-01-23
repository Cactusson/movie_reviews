from django.shortcuts import render


def home_page(request):
    return render(request, "reviews/home_page.html")
