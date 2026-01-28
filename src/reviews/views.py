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


def search(request):
    search_term = request.GET.get("q", "")
    if search_term == "":
        found_in_authors = Author.objects.none()
        found_in_titles = Review.objects.none()
    else:
        found_in_authors = Author.objects.filter(name__icontains=search_term).annotate(
            reviews_counter=Count("reviews")
        )
        found_in_authors = sorted(found_in_authors, key=lambda author: author.last_name)
        found_in_titles = Review.objects.filter(title__icontains=search_term)
    context = {
        "search_term": search_term,
        "found_in_authors": found_in_authors,
        "found_in_authors_count": len(found_in_authors),
        "found_in_titles": found_in_titles,
        "found_in_titles_count": found_in_titles.count(),
    }
    return render(request, "reviews/search_results.html", context)
