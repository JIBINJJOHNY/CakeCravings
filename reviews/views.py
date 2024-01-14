from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Avg
from django.views.decorators.http import require_POST
from .models import Review
from .forms import ReviewForm
from products.models import Product
from django.contrib.auth import get_user
from django.contrib.auth.decorators import login_required

@require_POST
@login_required
def ajax_add_review(request, pid):
    try:
        product = get_object_or_404(Product, pk=pid)

        # Check if the user has already submitted a review for this product
        existing_review = Review.objects.filter(user=request.user, product=product).first()
        if existing_review:
            # Handle the case where the user has already submitted a review
            return JsonResponse({'bool': False, 'error': 'You have already submitted a review for this product.'})

        rating = int(request.POST.get('rating', 0))

        review = Review.objects.create(
            user=request.user,
            product=product,
            rating=rating,
            comment=request.POST['comment'],
        )

        # Calculate the average rating after creating the review
        average_reviews = Review.objects.filter(product=product).aggregate(rating=Avg("rating"))
        average_rating = int(average_reviews['rating']) if average_reviews['rating'] is not None else 0

        context = {
            'user': request.user.username,
            'comment': request.POST['comment'],
            'rating': rating,
            'created_at': review.created_at.strftime("%B %d, %Y %I:%M %p"),
            'average_rating': average_rating,
        }

        return JsonResponse({
            'bool': True,
            'context': context,
        })
    except Exception as e:
        return JsonResponse({'bool': False, 'error': str(e)})

def product_reviews(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product_reviews = Review.objects.filter(product=product).order_by('-created_at')

    # Calculate the average rating
    average_reviews = Review.objects.filter(product=product).aggregate(rating=Avg("rating"))

    return render(request, 'products/product_detail.html', {'product': product, 'reviews': product_reviews, 'review_form': ReviewForm(), 'average_reviews': average_reviews})