from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from .models import Order, OrderItem
from .forms import OrderForm

def checkout(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)

            # Add the delivery information to the order
            order.selected_delivery_option = request.GET.get('delivery_option', 'pickup')
            order.delivery_cost = request.GET.get('delivery_cost', 0)

            order.save()

            # Save order items
            cart = request.session.get('cake_cravings_cart', {})
            for item_id, item_data in cart.items():
                try:
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_item = OrderItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_item.save()
                    else:
                        for size, quantity in item_data['items_by_size'].items():
                            order_item = OrderItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                size=size,
                            )
                            order_item.save()
                except Product.DoesNotExist:
                    messages.error(request, "One of the products in your cart wasn't found in our database.")
                    order.delete()
                    return redirect(reverse('view_cart'))

            # Clear the cart
            del request.session['cake_cravings_cart']

            messages.success(request, 'Order placed successfully!')
            return redirect(reverse('checkout_success', args=[order.order_id]))
        else:
            messages.error(request, 'There was an error with your order. Please double-check your information.')
    else:
        form = OrderForm()

    # Pass the delivery option and cost to the template
    selected_delivery_option = request.GET.get('delivery_option', 'pickup')
    delivery_cost = request.GET.get('delivery_cost', 0)

    template = 'orders/checkout.html'
    context = {
        'form': form,
        'selected_delivery_option': selected_delivery_option,
        'delivery_cost': delivery_cost,
    }

    return render(request, template, context)


def checkout_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    template = 'orders/checkout_success.html'
    context = {
        'order': order,
    }
    return render(request, template, context)
