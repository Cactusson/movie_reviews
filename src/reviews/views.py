from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from reviews.models import Author, Review


def home_page(request):
    context = {"reviews": Review.objects.all()}
    return render(request, "reviews/home_page.html", context)


def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    context = {"review": review}
    return render(request, "reviews/review_detail.html", context)


def author_list(request):
    authors = Author.objects.all().annotate(reviews_counter=Count("reviews"))
    authors = sorted(authors, key=lambda author: author.last_name)
    context = {"authors": authors}
    return render(request, "reviews/author_list.html", context)


def author_detail(request, slug):
    author = get_object_or_404(Author, slug=slug)
    context = {"author": author}
    return render(request, "reviews/author_detail.html", context)
