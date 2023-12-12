# Views for payment app.
from decimal import Decimal
import json
from django.urls import reverse
from django.http import HttpResponseRedirect
import stripe
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from profiles.models import Profile
from cart.contexts import cart_contents
from orders.models import Order, OrderItem
from products.models import Discount,Product
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.shortcuts import get_object_or_404
from orders.models import Order, OrderItem
from django.core.paginator import Paginator
import uuid 
from reviews.models import Review

class AddOrder(View):
    """View for adding order AJAX."""

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                cart_data = cart_contents(request)
                total_final = cart_data['grand_total']
                delivery_cost = Decimal(request.POST.get('delivery_cost', '0.0'))
                total_final_with_delivery = total_final + delivery_cost

                user = request.user
                full_name = request.POST.get('full_name')
                email = request.POST.get('email')
                phone = request.POST.get('phone')
                address1 = request.POST.get('address1')
                address2 = request.POST.get('address2')
                country = request.POST.get('country')
                county_region_state = request.POST.get('county_region_state')
                city = request.POST.get('city')
                zip_code = request.POST.get('zip_code')

                # Generate a unique order key using UUID
                order_key = str(uuid.uuid4())

                cart_items_json = request.POST.get('cart_items', '[]')
                cart_items = json.loads(cart_items_json)

                # Check if the order_key already exists
                existing_order = Order.objects.filter(order_key=order_key).first()

                if existing_order:
                    # Update the existing order
                    existing_order.total_paid = total_final_with_delivery
                    existing_order.billing_status = True
                    existing_order.save()
                else:
                    # Create a new order
                    order = Order.objects.create(
                        user=user,
                        full_name=full_name,
                        email=email,
                        phone=phone,
                        address1=address1,
                        address2=address2,
                        country=country,
                        county_region_state=county_region_state,
                        city=city,
                        zip_code=zip_code,
                        order_key=order_key,
                        total_paid=total_final_with_delivery,
                        billing_status=True,
                    )

                    for cart_item in cart_items:
                        product = get_object_or_404(Product, pk=cart_item['item_id'])
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=cart_item['quantity'],
                            size=cart_item.get('size'),
                        )

                return JsonResponse({'success': True, 'order_key': order_key})
            return JsonResponse({'success': False})
        else:
            return JsonResponse({'success': False, 'message': 'User not authenticated'})
@login_required
def basket_view(request):
    """View for payment page."""
    my_profile = get_object_or_404(Profile, user=request.user)
    cart = cart_contents(request)
    total_final = cart['grand_total']
    total_sum = "{:.2f}".format(total_final)
    total = int(total_final * 100) 
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe.api_key = settings.STRIPE_SECRET_KEY

    intent = stripe.PaymentIntent.create(
        amount=total,
        currency='eur',
        metadata={'userid': request.user.id}
    )
    # check if user has address details
    if any([my_profile.street_address1, my_profile.street_address2, my_profile.town_or_city, my_profile.county, my_profile.postcode]):
        primary_address = {
            'street_address1': my_profile.street_address1,
            'street_address2': my_profile.street_address2,
            'town_or_city': my_profile.town_or_city,
            'county': my_profile.county,
            'postcode': my_profile.postcode,
        }
        context = {
            'my_profile': my_profile,
            'primary_address': primary_address,
            'total_sum': total_sum,
            'client_secret': intent.client_secret,
            'stripe_public_key': stripe_public_key,
        }
        return render(request, 'orders/payment.html', context)

    context = {
        'my_profile': my_profile,
        'total_sum': total_sum,
        'client_secret': intent.client_secret,
        'stripe_public_key': stripe_public_key,
    }
    return render(request, 'orders/payment.html', context)

def order_placed(request):

 # Clear the cart
    cart = request.session.get('cart', {})
    cart.clear()
    request.session['cart'] = cart
    # Send email confirmation
    subject = 'Order Placed Successfully'

    # Create HTML content directly
    order_number = order.order_key
    html_content = f'''
        <h1>Order Placed Successfully</h1>
        <p>Thank you for shopping with us. Your order number is: {order_number}</p>
        <!-- You can customize the HTML content as needed -->
    '''

    plain_message = strip_tags(html_content)
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [my_profile.user.email]  # Replace with the actual user's email

    # Attach HTML content to the email
    email = EmailMultiAlternatives(subject, plain_message, from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    email.send()

    return render(request, 'orders/order_placed.html')

class OrdersView(View):
    """View for user orders page."""
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
            p = Paginator(Order.objects.filter(user=user).filter(
                billing_status=True
            ), 15)
            page = request.GET.get('page')
            orders = p.get_page(page)
            return render(
                request, 'orders/user_orders.html', {'orders': orders}
            )
        else:
            return render(
                request, 'account/login.html',
            )

class OrderDetailsView(View):
    """View for user order details page."""

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            order = get_object_or_404(
                Order,
                order_key=kwargs['order_number']
            )
            # get order items
            order_items = OrderItem.objects.filter(order=order)
            all_items = Order.get_order_items(order)
            # check if the order is completed
            user_reviews_for_this_order = Review.objects.filter(
                order=order,
                user=request.user
            )
            # get which products are in these reviews
            products_in_reviews = []
            for review in user_reviews_for_this_order:
                products_in_reviews.append(review.product)
            context = {
                'order': order,
                'order_items': order_items,
                'all_items': all_items,
                'products_in_reviews': products_in_reviews,
            }
            # Add the reverse URL statement here
            order_details_url = reverse('orders:order_details', kwargs={'order_number': order.order_key})
            if order.user == request.user:
                return HttpResponseRedirect(order_details_url)
            else:
                return render(
                    request, 'profiles/access_denied.html',
                )
        else:
            return render(
                request, 'account/login.html',
            )


def get_or_create_order(request):
    """
    Retrieve or create an Order instance for the current user.
    """
    user = request.user

    # Check if an order already exists for the user
    existing_order = Order.objects.filter(user=user, billing_status=True).first()

    if existing_order:
        return existing_order
    else:
        # If no order exists, create a new one
        new_order = Order.objects.create(user=user, billing_status=True, total_paid=0)
        return new_order

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    event = None
    
    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
    except ValueError as e:
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'payment_intent.succeeded':
        payment_confirmation(event.data.object.client_secret)
    else:
        print('Unhandled event type {}'.format(event.type))

    return HttpResponse(status=200)