from django.views import View
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Wishlist
from products.models import Product
from django.core import serializers
from django.template.loader import render_to_string
from django.http import HttpResponse


def view_wishlist(request):
    user = request.user
    if user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=user)
        wishlist_products = wishlist.products.all()
    else:
        wishlist_products = []

    context = {
        'wishlist_products': wishlist_products,
    }

    return render(request, 'wishlist/wishlist.html', context)


@login_required
def plus_wishlist(request):
    if request.method == 'GET':
        print('Plus Wishlist view called')
        prod_id = request.GET['prod_id']
        print(f'Product ID: {prod_id}')
        product = get_object_or_404(Product, id=prod_id)
        user = request.user

        # Use products instead of product
        wishlist, created = Wishlist.objects.get_or_create(user=user)
        wishlist.add_to_wishlist(product)

        data = {
            'message': 'Wishlist Added Successfully',
        }
        return JsonResponse(data)


def minus_wishlist(request):
    if request.method == 'GET':
        print('Minus Wishlist view called')
        prod_id = request.GET['prod_id']
        product = Product.objects.get(id=prod_id)
        user = request.user

        # Retrieve the user's wishlist
        wishlist, created = Wishlist.objects.get_or_create(user=user)

        # Remove the product from the wishlist
        removed = wishlist.remove_from_wishlist(product)

        data = {
            'message': 'Wishlist Remove Successfully',
            'removed': removed,  # Add this to indicate whether the removal was successful
        }
        return JsonResponse(data)


def wishlist_delete(request, product_id):
    user = request.user
    if user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=user)
        product = get_object_or_404(Product, id=product_id)
        wishlist.products.remove(product)

    return redirect('wishlist:view_wishlist')
