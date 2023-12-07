from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count
from django.db.models.functions import Lower
from .models import Product, Category
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .forms import ProductForm,ProductImageForm
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView
from reviews.forms import ReviewForm
from reviews.models import Review
from django.db.models import Avg
from wishlist.models import Wishlist



def is_manager(user):
    return user.is_authenticated and user.is_superuser
@require_GET
def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token})

def all_products(request, category_slug=None):
    """ A view to show all products, including sorting and search queries """

    products = Product.objects.filter(is_active=True)
    query = None
    sort = request.GET.get('sort', 'name')
    direction = request.GET.get('direction', 'asc')

    # Apply category filter if category_slug is provided
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    if sort == 'name':
        sort_key = 'name' if direction == 'asc' else '-name'
    elif sort == 'price':
        sort_key = 'price' if direction == 'asc' else '-price'
    elif sort == 'rating':
        # Assuming 'rating' is a field in your Product model
        sort_key = 'rating' if direction == 'asc' else '-rating'
    else:
        # Default to sorting by name in ascending order
        sort_key = 'name'

    products = products.order_by(sort_key)

    if request.GET:
        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))

            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

    # Retrieve all categories for the category list
    all_categories = Category.objects.all()
    # Get total product count
    total_product_count = Product.objects.filter(is_active=True).count()
    print("Total Product Count:", total_product_count)
    # Get product counts for each category
    product_counts = Product.objects.values('category__name').annotate(count=Count('id'))

    current_sorting = f'{sort}_{direction}'
    # Add a success message
    messages.success(request, 'Successfully performed the action.')

    context = {
        'products': products,
        'search_term': query,
        'all_categories': all_categories,
        'product_counts': product_counts,
        'current_sorting': current_sorting,
        'selected_category_slug': category_slug,  # Pass the selected category slug for highlighting in the template
        'total_product_count': total_product_count,  
    }
    return render(request, 'products/products.html', context)



def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    reviews = Review.objects.filter(product=product).order_by('-created_at')
    
    wishlist = None
    if request.user.is_authenticated:
        user_wishlist = Wishlist.objects.filter(user=request.user).first()
        if user_wishlist:
            wishlist = user_wishlist.products.filter(id=product.id).exists()

    # Calculate average rating
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            new_review = review_form.save(commit=False)
            new_review.product = product
            new_review.user = request.user  # Assuming you have user authentication
            new_review.save()
            return redirect('products:product_detail', product_id=product_id)
    else:
        review_form = ReviewForm()

    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'review_form': review_form,
        'average_rating': average_rating,
        'wishlist': wishlist,
    }

    return render(request, 'products/product_detail.html', context)


@user_passes_test(is_manager)
def product_list(request):
    products = Product.objects.filter(is_active=True)
    context = {
        'products': products,
    }
    return render(request, 'products/product_list.html', context)

@user_passes_test(is_manager)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        image_form = ProductImageForm(request.POST, request.FILES)

        if form.is_valid() and image_form.is_valid():
            product = form.save()
            image = image_form.save(commit=False)
            image.product = product
            image.save()

            messages.success(request, 'Successfully added product!')
            return redirect(reverse('products:product_list'))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()
        image_form = ProductImageForm()

    template = 'products/product_add.html'
    context = {'form': form, 'image_form': image_form}

    return render(request, template, context)

def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        image_form = ProductImageForm(request.POST, request.FILES, instance=product.images.first())

        if form.is_valid() and image_form.is_valid():
            form.save()
            image_form.save()
            messages.success(request, 'Product successfully updated!')
            return redirect(reverse('products:product_list'))
            
    else:
        form = ProductForm(instance=product)
        image_form = ProductImageForm(instance=product.images.first())

    return render(request, 'products/product_edit.html', {'product': product, 'form': form, 'image_form': image_form})

@user_passes_test(is_manager)
def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products:product_list'))
