from django.views import View
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Wishlist
from products.models import Product
from django.core import serializers
from django.template.loader import render_to_string


def WishlistPage(request):
    try:
        wishlist = Wishlist.objects.filter(user=request.user) 
    except:
        wishlist = None
    context = {
        "w": wishlist
    }
    return render(request, 'core/wishlist.html', context)
def add_to_wishlist(request):
    product_id = request.GET.get('product_id')
    
    try:
        product = Product.objects.get(id=product_id)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        
        if not wishlist.products.filter(id=product_id).exists():
            wishlist.products.add(product)
            context = {'bool': True}
        else:
            context = {'bool': False}
            
    except Product.DoesNotExist:
        context = {'bool': False}
    print(request.session['cart'])
    return JsonResponse(context)


def remove_wishlist(request):
    product_id = request.GET.get('product_id')
    
    try:
        wishlist = Wishlist.objects.get(user=request.user)
        product = Product.objects.get(id=product_id)
        
        if wishlist.products.filter(id=product_id).exists():
            wishlist.products.remove(product)
            context = {
                'bool': True,
                'wishlist': wishlist.products.all()
            }
        else:
            context = {'bool': False}

    except (Wishlist.DoesNotExist, Product.DoesNotExist):
        context = {'bool': False}

    qs_json = serializers.serialize('json', context['wishlist'])
    template = render_to_string('core/async/wishlist-list.html', context)
    
    return JsonResponse({'data': template, 'wishlist': qs_json})
