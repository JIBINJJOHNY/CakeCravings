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
    cart = request.session.get('cake_cravings_cart', {})
    cart_items = []

    for product_id, item_data in cart.items():
        product = get_object_or_404(Product, pk=product_id)

        if isinstance(item_data, int):
            # Case where item_data is an integer (quantity) without size
            cart_items.append({
                'product': product,
                'size': None,
                'quantity': item_data,
                'total_price': product.price * item_data  # Adjust this based on your pricing logic
            })
        elif 'items_by_size' in item_data:
            # Case where item_data is a dictionary containing sizes and quantities
            for size, quantity in item_data['items_by_size'].items():
                cart_items.append({
                    'product': product,
                    'size': size,
                    'quantity': quantity,
                    'total_price': product.price * quantity  # Adjust this based on your pricing logic
                })

    context = {'cart_items': cart_items}
    return render(request, 'cart/cart.html', context)

@require_POST
def add_to_cart(request):
    """ Add a quantity of the specified product to the cart """

    item_id = request.POST.get('item_id')
    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')
    size = request.POST.get('product_size')

    cart = request.session.get('cake_cravings_cart', {})
    if size:
        if item_id in cart:
            if 'items_by_size' in cart[item_id] and size in cart[item_id]['items_by_size']:
                cart[item_id]['items_by_size'][size] += quantity
                messages.success(request, f'Updated size {size.upper()} {product.name} quantity to {cart[item_id]["items_by_size"][size]}')
            else:
                if 'items_by_size' not in cart[item_id]:
                    cart[item_id]['items_by_size'] = {}
                cart[item_id]['items_by_size'][size] = quantity
                messages.success(request, f'Added size {size.upper()} {product.name} to your cart')
        else:
            cart[item_id] = {'items_by_size': {size: quantity}}
            messages.success(request, f'Added size {size.upper()} {product.name} to your cart')
    else:
        if item_id in cart:
            cart[item_id] += quantity
            messages.success(request, f'Updated {product.name} quantity to {cart[item_id]}')
        else:
            cart[item_id] = quantity
            messages.success(request, f'Added {product.name} to your cart')

    request.session['cake_cravings_cart'] = cart
    return redirect('cart:view_cart')

@require_POST
@login_required
def update_quantity_in_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        new_quantity = int(request.POST.get('new_quantity'))

        try:
            # Retrieve the product
            product = get_object_or_404(Product, id=product_id)

            # Assuming you have a session-based cart
            cart = request.session.get('cake_cravings_cart', {})

            # If the product is in the cart, update its quantity
            if str(product_id) in cart:
                cart[str(product_id)] = new_quantity
                request.session['cake_cravings_cart'] = cart

                # You can also update the total price or perform other calculations here

                # Return success message or any additional data
                return JsonResponse({'success': True, 'message': 'Quantity updated successfully'})

            else:
                # Handle the case where the product is not in the cart
                return JsonResponse({'success': False, 'error': 'Product not found in cart'})

        except Http404 as e:
            # Handle the case where the product does not exist
            return JsonResponse({'success': False, 'error': str(e)})

        except Exception as e:
            # Handle other exceptions (e.g., database errors) here
            return JsonResponse({'success': False, 'error': str(e)})

    else:
        return JsonResponse({'error': 'Invalid request method'})

@require_POST
@login_required
def remove_item_from_cart(request):
    product_id = request.POST.get('product_id')

    cart = request.session.get('cake_cravings_cart', {})
    
    if product_id in cart:
        del cart[product_id]
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
