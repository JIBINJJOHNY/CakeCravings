from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.db.models.functions import Lower
from django.core.paginator import Paginator, Page, EmptyPage, PageNotAnInteger
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Avg
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView
from django.http import HttpResponseBadRequest
from django.views import View
from .forms import ProductForm, ProductImageForm, AddTagForm, AddDiscountForm
from reviews.forms import ReviewForm
from reviews.models import Review
from .models import Product, Category, Tag, Discount
from wishlist.models import Wishlist


def is_manager(user):
    return user.is_authenticated and user.profile.role == 'manager'


@require_GET
def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token})


def all_products(request, category_slug=None):
    """A view to show all products, including sorting and search queries"""

    products = Product.objects.filter(is_active=True)
    query = request.GET.get('q', None)
    sort = request.GET.get('sort', 'name')
    direction = request.GET.get('direction', 'asc')

    # Apply category filter if category_slug is provided
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # Define the default sort key
    default_sort_key = 'name'

    if sort == 'name':
        sort_key = 'name' if direction == 'asc' else '-name'
    elif sort == 'price':
        sort_key = 'price' if direction == 'asc' else '-price'
    elif sort == 'rating':
        sort_key = '-avg_rating' if direction == 'desc' else 'avg_rating'
        products = products.annotate(avg_rating=Avg('reviews__rating')).order_by(sort_key)
    else:
        sort_key = default_sort_key

    # Calculate average rating for all products
    average_rating = products.aggregate(avg_rating=Avg('reviews__rating'))['avg_rating']

    # Order products after calculating average rating
    products = products.order_by(sort_key)

    if query:
        queries = Q(name__icontains=query) | Q(description__icontains=query)
        products = products.filter(queries)

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(products, 9)  # Show 9 products per page

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    # Retrieve all categories for the category list
    all_categories = Category.objects.all()
    total_product_count = Product.objects.filter(is_active=True).count()
    product_counts = Product.objects.values('category__name').annotate(count=Count('id'))

    current_sorting = f'{sort}_{direction}'

    # Include tags for each product in the context
    product_tags = {str(product.id): product.tags.all() for product in products}

    # Include products with tags in the context
    products_with_tags = Product.objects.filter(id__in=product_tags.keys())
    context = {
        'products_with_tags': products_with_tags,
        'product_tags': product_tags,
        'search_term': query,
        'all_categories': all_categories,
        'product_counts': product_counts,
        'current_sorting': current_sorting,
        'selected_category_slug': category_slug,
        'total_product_count': total_product_count,
        'average_rating': average_rating,
        'all_products': products,  # Use the paginated products for rendering
    }
    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    print(f"Product ID: {product_id}")
    product = get_object_or_404(Product, pk=product_id)
    reviews = Review.objects.filter(product=product).order_by('-created_at')

    # Check if the user has already submitted a review for this product
    user_review_exists = False
    if request.user.is_authenticated:
        user_review_exists = reviews.filter(user=request.user).exists()

    wishlist = None
    if request.user.is_authenticated:
        user_wishlist = Wishlist.objects.filter(user=request.user).first()
        if user_wishlist:
            wishlist = user_wishlist.products.filter(id=product.id).exists()

    # Calculate average rating
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    # Declare the review_form variable outside the if statement
    review_form = None
    # Calculate the cart count
    # Calculate the cart count with better error handling
    cart_count = sum(
        item.get('quantity', 0) if isinstance(item, dict) else int(item) if isinstance(item, int) else 0
        for item in request.session.get('cart', {}).values()
        if isinstance(item, (dict, int))
    )
    if request.method == 'POST':
        # Check if the user has already submitted a review
        if not user_review_exists:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                new_review = review_form.save(commit=False)
                new_review.product = product
                new_review.user = request.user
                new_review.save()
                return redirect('product_detail', product_id=product_id)
        else:
            # Display a message indicating that the user can only submit one review
            messages.warning(request, 'You can only submit one review per product.')  # Add this line

    # If the user has already submitted a review, don't display the review form
    if review_form is None:
        review_form = ReviewForm() if not user_review_exists else None

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


@login_required
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
            return redirect(reverse('product_list'))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()
        image_form = ProductImageForm()

    template = 'products/product_add.html'
    context = {'form': form, 'image_form': image_form}

    return render(request, template, context)


@user_passes_test(is_manager)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        image_form = ProductImageForm(request.POST, request.FILES, instance=product.images.first())

        if form.is_valid() and image_form.is_valid():
            form.save()
            image_form.save()
            messages.success(request, 'Product successfully updated!')
            return redirect(reverse('product_list'))

    else:
        form = ProductForm(instance=product)
        image_form = ProductImageForm(instance=product.images.first())

    return render(request, 'products/product_edit.html', {'product': product, 'form': form, 'image_form': image_form})


@user_passes_test(is_manager)
def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('product_list'))


@user_passes_test(is_manager)
def add_tag(request):
    if request.method == 'POST':
        form = AddTagForm(request.POST)
        if form.is_valid():
            tag_name = form.cleaned_data['tag_name'].strip()
            is_active = form.cleaned_data['is_active']  # Retrieve is_active value from the form

            if tag_name:
                tag, created = Tag.objects.get_or_create(name=tag_name, defaults={'is_active': is_active})
                if created:
                    messages.success(request, 'Tag added successfully.')
                else:
                    messages.warning(request, 'Tag already exists.')

                # Redirect to the referring page or the default 'product_list'
                referring_page = request.META.get('HTTP_REFERER', None)
                return redirect(referring_page) if referring_page else redirect('product_list')
            else:
                messages.warning(request, 'Tag name cannot be empty.')
                return HttpResponseBadRequest('Tag name cannot be empty.')
    else:
        form = AddTagForm()

    tags = Tag.get_active_tags()
    return render(request, 'products/tag.html', {'tags': tags, 'form': form})


@user_passes_test(is_manager)
def remove_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    tag.delete()
    messages.success(request, 'Tag removed successfully.')

    # Redirect to the referring page or the default 'product_list'
    referring_page = request.META.get('HTTP_REFERER', None)
    return redirect(referring_page) if referring_page else redirect('product_list')


@user_passes_test(is_manager)
def add_discount(request):
    if request.method == 'POST':
        form = AddDiscountForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Discount added successfully.')
        else:
            messages.error(request, 'Invalid form data. Please check and try again.')
        return redirect(request.path)  # Redirect to the same page

    discounts = Discount.objects.all()  # Retrieve all existing discounts
    return render(request, 'products/discount.html', {'form': AddDiscountForm(), 'discounts': discounts})


@user_passes_test(is_manager)
def remove_discount(request, discount_id):
    if request.method == 'POST':
        discount = get_object_or_404(Discount, id=discount_id)
        discount.delete()
        messages.success(request, 'Discount removed successfully.')
        return redirect(request.path)  # Redirect to the same page

    # If the request method is not POST, render the modal with the existing discounts
    discounts = Discount.objects.all()  # Modify this query based on your needs
    return render(request, 'products/discount.html', {'discounts': discounts})
