from django.shortcuts import get_object_or_404, render

from reviews.models import Review


def home_page(request):
    context = {"reviews": Review.objects.all()}
    return render(request, "reviews/home_page.html", context)


def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    context = {"review": review}
    return render(request, "reviews/review_detail.html", context)
