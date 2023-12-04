from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from products.models import Product
from .contexts import cart_contents
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize

def view_cart(request):
    """ A view that renders the cart contents page """
    context = cart_contents(request)
    return render(request, 'cart/cart.html', context)

def add_to_cart(request, item_id=None):
    """ Add a quantity of the specified product to the cart """
    print("Reached add_to_cart view") 
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))  # Convert to int
        size = None

        # Assuming you have a form element named 'product_size'
        if 'product_size' in request.POST:
            size = request.POST['product_size']

        product = get_object_or_404(Product, pk=product_id)
        cart = request.session.get('cake_cravings_cart', {})

        if size:
            if product_id in cart:
                if size in cart[product_id]['items_by_size']:
                    cart[product_id]['items_by_size'][size] += quantity
                    messages.success(request, f'Updated size {size.upper()} {product.name} quantity to {cart[product_id]["items_by_size"][size]}')
                else:
                    cart[product_id]['items_by_size'][size] = quantity
                    messages.success(request, f'Added size {size.upper()} {product.name} to your cart')
            else:
                cart[product_id] = {'items_by_size': {size: quantity}}
                messages.success(request, f'Added size {size.upper()} {product.name} to your cart')
        else:
            if product_id in cart:
                cart[product_id] += quantity
                messages.success(request, f'Updated {product.name} quantity to {cart[product_id]}')
            else:
                cart[product_id] = quantity
                messages.success(request, f'Added {product.name} to your cart')

        request.session['cake_cravings_cart'] = cart

    # Redirect to the cart view after updating the cart
    return redirect('cart:view_cart')

from django.http import JsonResponse

@require_POST
@login_required
def update_quantity_in_cart(request):
    product_inventory_id = request.POST.get('product_inventory_id')
    new_quantity = int(request.POST.get('new_quantity'))

    cart = request.session.get('cake_cravings_cart', {})
    
    if product_inventory_id in cart:
        cart[product_inventory_id] = new_quantity
        request.session['cake_cravings_cart'] = cart
        context = cart_contents(request)
        serialized_cart_items = serialize('json', context['cart_items'])
        
        return JsonResponse({
            'success': True,
            'message_alert': "Quantity updated successfully.",
            'total': context['total'],
            'product_count': context['product_count'],
            'cart_items': serialized_cart_items,
        })
    else:
        return JsonResponse({'success': False, 'error': 'Product not found in cart'})



@require_POST
@login_required
def remove_item_from_cart(request):
    product_inventory_id = request.POST.get('product_inventory_id')

    cart = request.session.get('cake_cravings_cart', {})
    
    if product_inventory_id in cart:
        del cart[product_inventory_id]
        request.session['cake_cravings_cart'] = cart
        context = cart_contents(request)
        serialized_cart_items = serialize('json', context['cart_items'])
        
        return JsonResponse({
            'success': True,
            'message_alert': "Item removed from the cart.",
            'total': context['total'],
            'product_count': context['product_count'],
            'cart_items': serialized_cart_items,
        })
    else:
        return JsonResponse({'success': False, 'error': 'Product not found in cart'})


def update_delivery_option(request):
    """
    View to update the selected delivery option.
    """
    if request.method == 'POST':
        selected_delivery_option = request.POST.get('delivery_option')
        request.session['delivery_option'] = selected_delivery_option
        context = cart_contents(request)
        return render(request, 'cart/cart.html', context)
    else:
        # Handle non-POST requests or redirect as needed
        # You can customize this based on your requirements
        return render(request, 'cart/cart.html', {})
