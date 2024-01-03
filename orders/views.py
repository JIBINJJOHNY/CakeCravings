import json
import stripe
import uuid
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from cart.contexts import cart_contents
from orders.models import Order, OrderItem
from products.models import Product
from profiles.models import Profile
from reviews.models import Review
from decimal import Decimal
from django.utils.html import strip_tags

class AddOrder(View):
    """View for adding order AJAX."""
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                cart = cart_contents(request)
                total = cart['grand_total']

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
                order_key = request.POST.get('order_key')

                total_paid = str(total)
                cart_items = cart['cart_items']

                if Order.objects.filter(order_key=order_key).exists():
                    return JsonResponse({'success': False, 'message': 'Order with the same key already exists.'})
                else:
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
                        total_paid=total_paid,
                    )
                    for cart_item in cart_items:
                        # Assuming 'product' and 'quantity' are keys in your cart item
                        product = cart_item['product']
                        quantity = cart_item['quantity']

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                        )

                    # Update the order total, delivery cost, and grand total
                    order.update_total()

                    # Set billing status to True since the payment is successful
                    order.billing_status = True
                    order.save()

                    # Send confirmation email
                    send_payment_confirmation_email(order.email, order_key, total)

                    # Clear the cart only if the payment was successful
                    cart = request.session.get('cart', {})
                    cart.clear()
                    request.session['cart'] = cart

                    return JsonResponse({'success': True, 'message': 'Order added successfully.'})
            return JsonResponse({'success': False, 'message': 'Invalid request.'})
        else:
            return render(request, 'account/login.html')


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
@method_decorator(login_required, name='dispatch')
class OrderDetailsView(View):
    """View for displaying order details."""

    def get(self, request, order_number, *args, **kwargs):
        print("DEBUG: Inside OrderDetailsView GET method")
        try:
            order = Order.objects.get(order_key=order_number, user=request.user)
            context = {
                'order': order,
                'order_items': order.order_item.all(),
                
            }
            return render(request, 'orders/order_details.html', context)
        except Order.DoesNotExist:
            print("DEBUG: Order not found")
            # Handle the case where the order is not found (redirect or show an error page)
            return render(request, 'orders/order_error.html')
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
        try:
            payment_confirmation(event.data.object.client_secret)
            return HttpResponse(status=200)
        except Exception as e:
            logger.error(f"Error in handling payment_intent.succeeded: {str(e)}")
            return HttpResponse(status=500)
    else:
        logger.warning(f"Unhandled event type: {event.type}")
        return HttpResponse(status=200)
class ErrorView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'orders/order_error.html')

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
        return redirect('orders:error')

def send_payment_confirmation_email(customer_email, order_key, amount_received):
  
    BASE_URL = settings.BASE_URL
    # Format the amount with 2 decimal places
    formatted_amount = "{:.2f}".format(amount_received)

    subject = 'Payment Confirmation'
    order_detail_url = reverse('orders:order_details', args=[order_key])

    # Construct the absolute URL to the logo
    logo_url = 'https://cakecravingss-93e2bca9bc4c.herokuapp.com' + settings.STATIC_URL + 'images/login_page.png'

    # Additional marketing sentence
    marketing_sentence = "At Cake Cravings, we strive to make your moments sweet and memorable. Your order is being prepared with care and attention to detail."

    # Get the order details and items
    order = Order.objects.get(order_key=order_key)
    order_items = order.order_item.all()

    # Construct the list of ordered items
    ordered_items_list = "<ul>"
    for item in order_items:
        ordered_items_list += f"<li><strong>{item.quantity} x {item.product.name}</strong></li>"
    ordered_items_list += "</ul>"

    order_detail_link = f'{BASE_URL}{order_detail_url}'


    # Construct the HTML content inline
    html_content = f"""
        <h1>Thank you for your order!</h1>
        <p>Your payment of ${formatted_amount} has been received. Your order key is {order_key}.</p>
        <p>{marketing_sentence}</p>
        <p>Your Order Details:</p>
        {ordered_items_list}
        <p>Click <a href="{order_detail_link}">here</a> to view your order details.</p>
        <img src="{logo_url}" alt="Bakery Logo" width="100" height="50">
    """

    # Create an EmailMultiAlternatives instance
    msg = EmailMultiAlternatives(subject, strip_tags(html_content), 'jibinjjohny11@gmail.com', [customer_email])
    msg.attach_alternative(html_content, "text/html")

    # Send the email
    msg.send(fail_silently=False)
