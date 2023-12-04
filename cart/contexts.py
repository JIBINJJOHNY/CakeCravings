from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.conf import settings
from products.models import Product

def cart_contents(request):
    cart_items = []
    total = 0
    product_count = 0
    cart = request.session.get('cake_cravings_cart', {})
    selected_delivery_option = request.session.get('delivery_option', 'pickup')

    for item_id, item_data in cart.items():
        if isinstance(item_data, int):
            product = get_object_or_404(Product, pk=item_id)
            item_total = item_data * product.price
            total += item_total
            product_count += item_data
            cart_items.append({
                'product_id': item_id,
                'quantity': item_data,
                'product': product,
                'item_total': item_total,
            })

    # Set delivery cost based on the selected delivery option
    if selected_delivery_option == 'local_delivery':
        delivery_cost = min(Decimal('2.00'), total * Decimal(10 / 100))  # Minimum €2.00 or 10% of total
    elif selected_delivery_option == 'national_delivery':
        delivery_cost = Decimal('5.00')  # Fixed €5.00 for national delivery
    else:
        delivery_cost = Decimal('0.00')  # No delivery cost for pickup

    if total < settings.FREE_DELIVERY_THRESHOLD:
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        free_delivery_delta = 0

    grand_total = delivery_cost + total

    context = {
        'cart_items': cart_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery_cost,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
        'selected_delivery_option': selected_delivery_option,
    }

    return context
