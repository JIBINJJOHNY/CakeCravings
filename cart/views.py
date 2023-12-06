from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from products.models import Product
from .contexts import cart_contents
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from decimal import Decimal
from django.http import Http404


def view_cart(request):
    """ A view that renders the cart contents page """

    return render(request, 'cart/cart.html')

def add_to_cart(request):
    """ Add a quantity of the specified product to the shopping cart """

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        redirect_url = request.POST.get('redirect_url')
        size = request.POST.get('product_size')
        quantity = int(request.POST.get('quantity'))

        product_obj = get_object_or_404(Product, pk=product_id)
        cart = request.session.get('cart', {})

        if size:
            if product_id in cart:
                if 'items_by_size' in cart[product_id]:
                    if size in cart[product_id]['items_by_size']:
                        cart[product_id]['items_by_size'][size] += quantity
                        messages.success(request, f'Updated size {size.upper()} {product_obj.name} quantity to {cart[product_id]["items_by_size"][size]}')
                    else:
                        cart[product_id]['items_by_size'][size] = quantity
                        messages.success(request, f'Added size {size.upper()} {product_obj.name} to your cart')
                else:
                    cart[product_id]['items_by_size'] = {size: quantity}
                    messages.success(request, f'Added size {size.upper()} {product_obj.name} to your cart')
            else:
                cart[product_id] = {'items_by_size': {size: quantity}}
                messages.success(request, f'Added size {size.upper()} {product_obj.name} to your cart')
        else:
            if product_id in cart:
                # Check if it's a simple quantity or a dictionary
                if isinstance(cart[product_id], int):
                    cart[product_id] += quantity
                    messages.success(request, f'Updated {product_obj.name} quantity to {cart[product_id]}')
                else:
                    messages.error(request, f'Unexpected cart structure for {product_obj.name}')
            else:
                cart[product_id] = quantity
                messages.success(request, f'Added {product_obj.name} to your cart')

        # Calculate the total count of items in the cart
        total_cart_count = sum(item_count if isinstance(item_count, int) else sum(item_count.get('items_by_size', {}).values()) for item_count in cart.values())

        # Store the total cart count in the session
        request.session['total_cart_count'] = total_cart_count
        request.session['cart'] = cart

        # Return the total cart count as part of the JSON response
        return JsonResponse({'success': True, 'total_cart_count': total_cart_count})

    return JsonResponse({'success': False})


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

def calculate_delivery_cost(selected_delivery_option, total):
    if selected_delivery_option == 'local_delivery':
        return min(Decimal('2.00'), total * Decimal(10 / 100))  # Minimum €2.00 or 10% of total
    elif selected_delivery_option == 'national_delivery':
        return Decimal('5.00')  # Fixed €5.00 for national delivery
    else:
        return Decimal('0.00')  # No delivery cost for pickup

@require_POST
@login_required
def update_delivery_cost(request):
    selected_delivery_option = request.POST.get('selected_delivery_option', 'pickup')
    cart = request.session.get('cake_cravings_cart', {})
    
    total = 0
    for item_id, item_data in cart.items():
        if isinstance(item_data, int):
            product = get_object_or_404(Product, pk=item_id)
            item_total = item_data * product.price
            total += item_total

    delivery_cost = calculate_delivery_cost(selected_delivery_option, total)

    request.session['delivery_option'] = selected_delivery_option
    request.session['delivery_cost'] = float(delivery_cost)  # Convert Decimal to float for JSON serialization

    return JsonResponse({'success': True, 'delivery_cost': float(delivery_cost)})
