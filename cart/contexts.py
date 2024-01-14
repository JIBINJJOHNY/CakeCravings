from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product
from django.http import Http404

def cart_contents(request):
    cart_items = []
    total = 0
    product_count = 0
    cart = request.session.get('cart', {})
    delivery_option = request.GET.get('delivery_option', 'online')

    for item_id, item_data in cart.items():
        try:
            # Attempt to convert the item_id to an integer
            item_id = int(item_id)
        except ValueError:
            # Handle the case where item_id is not a valid integer
            raise Http404("Invalid product ID")

        product = get_object_or_404(Product, pk=item_id)

        if isinstance(item_data, dict) and 'items_by_size' in item_data:
            for size, quantity in item_data['items_by_size'].items():
                price_for_size = product.get_price_for_size(size)

                total += quantity * price_for_size
                product_count += quantity
                cart_items.append({
                    'item_id': item_id,
                    'quantity': quantity,
                    'product': product,
                    'size': size,
                    'price_for_size': price_for_size,
                })
        else:
            quantity = item_data
            if product.price is not None:
                total += quantity * product.price
                product_count += quantity
                cart_items.append({
                    'item_id': item_id,
                    'quantity': quantity,
                    'product': product,
                })

    # Adjust delivery cost based on the selected delivery option
    if total < settings.FREE_DELIVERY_THRESHOLD:
        if delivery_option == 'online':
            delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        else:
            delivery = 0  # No delivery cost for 'pickup'
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = 0
        free_delivery_delta = 0

    grand_total = delivery + total
    product_count = sum(item['quantity'] for item in cart_items)

    context = {
        'cart_items': cart_items,
        'cart_count': product_count,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
        'delivery_option': delivery_option,
    }

    return context