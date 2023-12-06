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

def view_cart(request):
    cart = request.session.get('cart', {})
    print("Cart Contents:", cart)  # Add this line for debugging
    return render(request, 'cart/cart.html')

def add_to_cart(request):
    """ Add a quantity of the specified product to the shopping cart """
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        redirect_url = request.POST.get('redirect_url')
        size = request.POST.get('product_size')
        quantity = int(request.POST.get('quantity'))

        # Get the product object based on the product_id
        product_obj = get_object_or_404(Product, pk=product_id)
        
        # Get the current cart from the session or initialize an empty cart
        cart = request.session.get('cart', {})

        # Check if the product has a size specified
        if product_obj.has_sizes:
            if product_id in cart:
                # Check if the product already has sizes in the cart
                if 'items_by_size' in cart[product_id]:
                    if size in cart[product_id]['items_by_size']:
                        # Update the quantity if the size already exists
                        cart[product_id]['items_by_size'][size] += quantity
                        messages.success(request, f'Updated size {size.upper()} {product_obj.name} quantity to {cart[product_id]["items_by_size"][size]}')
                    else:
                        # Add a new size to the product in the cart
                        cart[product_id]['items_by_size'][size] = quantity
                        messages.success(request, f'Added size {size.upper()} {product_obj.name} to your cart')
                else:
                    # Initialize the sizes for the product in the cart
                    cart[product_id]['items_by_size'] = {size: quantity}
                    messages.success(request, f'Added size {size.upper()} {product_obj.name} to your cart')
            else:
                # Add a new product with size to the cart
                cart[product_id] = {'items_by_size': {size: quantity}}
                messages.success(request, f'Added size {size.upper()} {product_obj.name} to your cart')
        else:
            # Check if the product without size already exists in the cart
            if product_id in cart:
                # Check if it's a simple quantity or a dictionary
                if isinstance(cart[product_id], int):
                    # Update the quantity for a product without size
                    cart[product_id] += quantity
                    messages.success(request, f'Updated {product_obj.name} quantity to {cart[product_id]}')
                else:
                    # Error handling for unexpected cart structure
                    messages.error(request, f'Unexpected cart structure for {product_obj.name}')
            else:
                # Add a new product without size to the cart
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

def update_cart(request, product_id):
    """
    Update the user's shopping cart
    """
    product = get_object_or_404(Product, pk=product_id)
    cart = request.session.get('cake_cravings_cart', {})

    # Assuming you have a form or some way to get the quantity and size from the user
    quantity = request.POST.get('quantity', 1)
    size = request.POST.get('size', None)

    # Update cart based on whether the product has size or not
    if size:
        if product_id in cart:
            if 'items_by_size' in cart[product_id]:
                cart[product_id]['items_by_size'][size] = int(quantity)
            else:
                cart[product_id]['items_by_size'] = {size: int(quantity)}
        else:
            cart[product_id] = {'items_by_size': {size: int(quantity)}}
    else:
        cart[product_id] = int(quantity)

    request.session['cake_cravings_cart'] = cart
    messages.success(request, 'Cart updated successfully.')
    
    # Redirect back to the product detail page or wherever you want
    return redirect('product_detail', product_id=product_id)

def remove_from_cart(request, item_id):
    """Remove the item from the shopping cart"""

    try:
        product = get_object_or_404(Product, pk=item_id)
        size = None

        if 'product_size' in request.POST:
            size = request.POST['product_size']

        cart = request.session.get('cake_cravings_cart', {})

        if size:
            if item_id in cart and 'items_by_size' in cart[item_id] and size in cart[item_id]['items_by_size']:
                del cart[item_id]['items_by_size'][size]
                if not cart[item_id]['items_by_size']:
                    del cart[item_id]
                messages.success(request, f'Removed size {size.upper()} {product.name} from your cart')
            else:
                messages.warning(request, f'{product.name} in size {size.upper()} not found in your cart')
        else:
            if item_id in cart:
                del cart[item_id]
                messages.success(request, f'Removed {product.name} from your cart')
            else:
                messages.warning(request, f'{product.name} not found in your cart')

        request.session['cake_cravings_cart'] = cart
        return HttpResponse(status=200)

    except Exception as e:
        messages.error(request, f'Error removing item: {e}')
        return HttpResponse(status=500)
        
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
