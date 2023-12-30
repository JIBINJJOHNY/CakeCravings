import json
import stripe
import uuid
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from cart.contexts import cart_contents
from orders.models import Order, OrderItem
from products.models import Product
from profiles.models import Profile
from reviews.models import Review
from decimal import Decimal

# Set up logging
logger = logging.getLogger(__name__)

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

                try:
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

                    # Send confirmation email
                    send_payment_confirmation_email(order.email, order_key, total_final_with_delivery)

                    # Clear the cart only if the payment was successful
                    cart = request.session.get('cart', {})
                    cart.clear()
                    request.session['cart'] = cart

                except Exception as e:
                    # Handle the error, log it, and return a JsonResponse with an error message
                    logger.error(f"An error occurred while creating the order: {str(e)}")
                    return JsonResponse({'success': False, 'message': 'Error processing the order'})

                return JsonResponse({'success': True, 'order_key': order_key})
            return JsonResponse({'success': False})
        else:
            return JsonResponse({'success': False, 'message': 'User not authenticated'})
@login_required
def basket_view(request):
    try:
        # Attempt to get the latest order for the user
        try:
            latest_order = Order.objects.filter(user=request.user).latest('created')
        except Order.DoesNotExist:
            # If the order doesn't exist, create a new one
            latest_order = Order.objects.create(user=request.user)

        cart = cart_contents(request)

        # Check if the delivery option is 'pickup' and adjust the total accordingly
        if cart['delivery_option'] == 'pickup':
            total_final = cart['total']  # Use the total without delivery cost for 'pickup'
        else:
            total_final = cart['grand_total']  # Use the grand total for 'online'

        print("Cart Contents:")
        print(cart)
        print("Total Final:", total_final)

        total_sum = "{:.2f}".format(total_final)
        total = int(total_final * 100)
        stripe_public_key = settings.STRIPE_PUBLIC_KEY
        stripe.api_key = settings.STRIPE_SECRET_KEY

        intent = stripe.PaymentIntent.create(
            amount=total,
            currency='eur',
            metadata={'userid': request.user.id}
        )

        # Fetch user information from the latest order
        user_info = {
            'full_name': latest_order.full_name,
            'email': latest_order.email,
            'phone': latest_order.phone,
            'address1': latest_order.address1,
            'address2': latest_order.address2,
            'country': latest_order.country,
            'county_region_state': latest_order.county_region_state,
            'city': latest_order.city,
            'zip_code': latest_order.zip_code,
        }

        # Fetch the primary address from the user's profile
        try:
            primary_address = Profile.objects.get(user=request.user, is_primary_address=True)
        except Profile.DoesNotExist:
            primary_address = None

        context = {
            'my_profile': None,  # You can remove this line since we're not using the Profile model
            'primary_address': primary_address,
            'user_info': user_info,
            'total_sum': total_sum,
            'client_secret': intent.client_secret,
            'stripe_public_key': stripe_public_key,
        }

        return render(request, 'orders/payment.html', context)
    except Exception as e:
        logger.error(f"An error occurred in basket_view: {str(e)}")
        return HttpResponse("An error occurred.")

class OrderConfirmation(View):
    """View for the order placed page."""
    def get(self, request, *args, **kwargs):
        return render(request, 'orders/order_confirmation.html')

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

def payment_confirmation(client_secret):
    try:
        payment_intent = stripe.PaymentIntent.retrieve(client_secret)
        order_key = payment_intent.metadata.order_key
        order = Order.objects.get(order_key=order_key)
        
        # Send payment confirmation email
        send_payment_confirmation_email(order.email, order_key, payment_intent.amount_received / 100)

        # Redirect to the order confirmation page
        return redirect('orders:order_confirmation')
    except Exception as e:
        logger.error(f"An error occurred in payment_confirmation: {str(e)}")
        # Handle the error and redirect accordingly
        return redirect('some_error_page')

def send_payment_confirmation_email(customer_email, order_key, amount_received):
    # Format the amount with 2 decimal places
    formatted_amount = "{:.2f}".format(amount_received)

    subject = 'Payment Confirmation'
    message = f'Thank you for your order! Your payment of {formatted_amount} has been received. Your order key is {order_key}.'
    from_email = 'jibinjjohny11@gmail.com' 
    recipient_list = [customer_email]

    send_mail(subject, message, from_email, recipient_list)
