from typing import cast

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from reviews.models import Author, Review


def home_page(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated and request.user.follows.count() > 0:
        reviews = Review.objects.filter(author__in=request.user.follows.all())
    else:
        reviews = Review.objects.all()
    paginator = Paginator(reviews, settings.REVIEWS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj}
    return render(request, "reviews/home_page.html", context)


def review_detail(request: HttpRequest, pk: int) -> HttpResponse:
    review = get_object_or_404(Review, pk=pk)
    context = {"review": review}
    return render(request, "reviews/review_detail.html", context)


def author_list(request: HttpRequest) -> HttpResponse:
    authors = Author.objects.all().annotate(reviews_counter=Count("reviews"))
    authors_list = sorted(authors, key=lambda author: author.last_name)
    context = {"authors": authors_list}
    return render(request, "reviews/author_list.html", context)


def author_detail(request: HttpRequest, slug: str) -> HttpResponse:
    author = get_object_or_404(Author, slug=slug)
    reviews = author.reviews.all()
    paginator = Paginator(reviews, settings.REVIEWS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"author": author, "page_obj": page_obj}
    return render(request, "reviews/author_detail.html", context)


def search(request: HttpRequest) -> HttpResponse:
    search_term = request.GET.get("q", "")
    if search_term == "":
        found_in_authors = Author.objects.none()
        found_in_titles = Review.objects.none()
    else:
        found_in_authors = Author.objects.filter(name__icontains=search_term).annotate(
            reviews_counter=Count("reviews")
        )
        found_in_authors_list = sorted(
            found_in_authors, key=lambda author: author.last_name
        )
        found_in_titles = Review.objects.filter(title__icontains=search_term)
    context = {
        "search_term": search_term,
        "found_in_authors": found_in_authors_list,
        "found_in_authors_count": len(found_in_authors_list),
        "found_in_titles": found_in_titles,
        "found_in_titles_count": found_in_titles.count(),
    }
    return render(request, "reviews/search_results.html", context)


@login_required
def author_follow(request: HttpRequest, slug: str) -> HttpResponse:
    author = get_object_or_404(Author, slug=slug)
    user = cast(AbstractBaseUser, request.user)
    author.followers.add(user)
    return redirect(author.get_absolute_url())


@login_required
def author_unfollow(request: HttpRequest, slug: str) -> HttpResponse:
    author = get_object_or_404(Author, slug=slug)
    user = cast(AbstractBaseUser, request.user)
    author.followers.remove(user)
    return redirect(author.get_absolute_url())
