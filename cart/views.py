from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages
from django.conf import settings
from decimal import Decimal
from products.models import Product
from .contexts import cart_contents
from django.http import JsonResponse
from django.views.decorators.http import require_POST

def view_cart(request):
    delivery_option = request.GET.get('delivery_option', 'online')
    context = cart_contents(request)
    context['delivery_option'] = delivery_option  # Make sure it's added to the context
    request.session['delivery_option'] = delivery_option

    return render(request, 'cart/cart.html', context)

def add_to_cart(request, item_id):
    """ Add a quantity of the specified product to the shopping cart """
    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')
    size = None

    if 'product_size' in request.POST:
        size = request.POST['product_size']

    cart = request.session.get('cart', {})

    if size:
        if item_id in cart:
            if 'items_by_size' in cart[item_id] and size in cart[item_id]['items_by_size']:
                cart[item_id]['items_by_size'][size] += quantity
                messages.success(request, f'Updated size {size.upper()} {product.name} quantity to {cart[item_id]["items_by_size"][size]}')
            else:
                cart[item_id].setdefault('items_by_size', {})[size] = quantity
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

    # Explicitly assign the modified cart back to the session
    request.session['cart'] = cart
    request.session.modified = True

    # Print the delivery_option value
    delivery_option = request.GET.get('delivery_option', 'online')
    print(f"Delivery Option (add_to_cart): {delivery_option}")

    # Calculate the updated cart count, including products with sizes
    cart_count = sum(
        (
            (
                (
                    item_data.get('quantity')
                    if isinstance(item_data, dict) and 'items_by_size' not in item_data
                    else sum(item_data.get('items_by_size', {}).values())
                )
                if isinstance(item_data, dict)
                else item_data
            )
            for item_data in cart.values()
        )
    )

    print(f"Cart Count: {cart_count}")

    # Include messages in the JsonResponse data
    messages_list = [{'message': str(message), 'tag': message.tags} for message in messages.get_messages(request)]
    response_data = {
        'success': True,
        'cart_count': cart_count,
        'messages': messages_list,
        'total': float(product.discounted_price) * quantity if product.discounted_price else float(product.price) * quantity,
    }

    return JsonResponse(response_data)

def get_cart_count(request):
    context = cart_contents(request)
    cart_count = context.get('cart_count', 0)
    print(f"Cart Count (get_cart_count): {cart_count}")
    return JsonResponse({'success': True, 'cart_count': cart_count})

def adjust_cart(request, item_id):
    """Adjust the quantity of the specified product to the specified amount"""
    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity'))
    size = None
    if 'product_size' in request.POST:
        size = request.POST['product_size']
    cart = request.session.get('cart', {})
    delivery_option = request.GET.get('delivery_option', 'online')
    if size:
        if quantity > 0:
            cart[item_id]['items_by_size'][size] = quantity
            messages.success(request, f'Updated size {size.upper()} {product.name} quantity to {cart[item_id]["items_by_size"][size]}')
        else:
            del cart[item_id]['items_by_size'][size]
            if not cart[item_id]['items_by_size']:
                cart.pop(item_id)
            messages.success(request, f'Removed size {size.upper()} {product.name} from your cart')
    else:
        if quantity > 0:
            cart[item_id] = quantity
            messages.success(request, f'Updated {product.name} quantity to {cart[item_id]}')
        else:
            cart.pop(item_id)
            messages.success(request, f'Removed {product.name} from your cart')
    request.session['cart'] = cart
    # Print the delivery_option value
    delivery_option = request.GET.get('delivery_option', 'online')
    print(f"Delivery Option (adjust_cart): {delivery_option}")
    return redirect(f'{reverse("view_cart")}?delivery_option={delivery_option}')

def remove_from_cart(request, item_id):
    """Remove the item from the shopping cart"""

    try:
        product = get_object_or_404(Product, pk=item_id)
        size = None
        if 'product_size' in request.POST:
            size = request.POST['product_size']

       # Check if the order is placed or not
        if request.user.is_authenticated and hasattr(request.user, 'orders') and request.user.orders.filter(status='Placed').exists():
            # Order is placed, don't remove from the cart
            messages.error(request, "Cannot remove items from the cart after the order is placed.")
        else:
            # Continue with removing from the cart
            cart = request.session.get('cart', {})

            if size:
                del cart[item_id]['items_by_size'][size]
                if not cart[item_id]['items_by_size']:
                    cart.pop(item_id)
                messages.success(request, f'Removed size {size.upper()} {product.name} from your cart')
            else:
                cart.pop(item_id)
                messages.success(request, f'Removed {product.name} from your cart')

            request.session['cart'] = cart
            messages.success(request, f'Removed {product.name} from your cart')

        return HttpResponse(status=200)

    except Exception as e:
        messages.error(request, f'Error removing item: {e}')
        return HttpResponse(status=500)
    

@require_POST
def update_delivery_option(request):
    try:
        delivery_option = request.POST.get('delivery_option')

        # Update the delivery option in the session or database
        request.session['delivery_option'] = delivery_option

        # ... (Your existing logic for calculating delivery cost and total)

        # Update the response with the new delivery cost and total
        response_data = {
            'success': True,
            'delivery_cost': str(delivery_cost),  # Convert to string for JSON compatibility
            'total': str(total),  # Convert to string for JSON compatibility
        }

        return JsonResponse(response_data)

    except Exception as e:
        # Log the error for debugging
        print(f"Error in update_delivery_option view: {str(e)}")
        return JsonResponse({'success': False, 'error': 'An error occurred'})

    