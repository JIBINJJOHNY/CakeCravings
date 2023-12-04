from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from .models import Order, OrderItem
from .forms import OrderForm

def checkout(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.save()

            # Save order items
            bag = request.session.get('bag', {})
            for item_id, item_data in bag.items():
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
                    messages.error(request, "One of the products in your bag wasn't found in our database.")
                    order.delete()
                    return redirect(reverse('view_bag'))

            # Clear the bag
            del request.session['bag']

            messages.success(request, 'Order placed successfully!')
            return redirect(reverse('checkout_success', args=[order.order_id]))
        else:
            messages.error(request, 'There was an error with your order. Please double-check your information.')
    else:
        form = OrderForm()

    template = 'checkout/checkout.html'
    context = {
        'form': form,
    }

    return render(request, template, context)

def checkout_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }
    return render(request, template, context)
