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
from django.utils.html import strip_tags
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin
from cart.contexts import cart_contents
from orders.models import Order, OrderItem
from products.models import Product
from profiles.models import Profile
from reviews.models import Review
from decimal import Decimal
from .forms import OrderForm


# Set up the logger
logger = logging.getLogger(__name__)


class AddOrder(View):
    """View for adding order AJAX."""
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                cart = cart_contents(request)
                total = cart['grand_total']
                delivery_option = request.POST.get('delivery_option', 'online')  # Get the delivery option
                
                # Debug statement
                print(f"Delivery Option (AddOrder - Received from Cart): {delivery_option}")

                # Create PaymentIntent
                try:
                    intent = stripe.PaymentIntent.create(
                        amount=int(total * 100),  # Convert to cents
                        currency='eur',
                        metadata={'userid': request.user.id, 'delivery_option': delivery_option}
                    )
                except stripe.error.CardError as e:
                    # Handle card error
                    return JsonResponse({'success': False, 'message': str(e)})

                # Retrieve delivery_option from metadata
                print(request.POST)
                delivery_option = request.POST.get('delivery_option', 'online')
                print(f"Delivery Option (AddOrder - After PaymentIntent): {delivery_option}")

                user = request.user
                full_name = request.POST.get('full_name')
                email = request.POST.get('email')
                phone = request.POST.get('phone')
                address1 = request.POST.get('address1')
                address2 = request.POST.get('address2')
                country = request.POST.get('country')
                
                # Debug statement
                state = request.POST.get('state')
                print(f"State (AddOrder): {state}")

                city = request.POST.get('city')
                zip_code = request.POST.get('zip_code')
                order_key = request.POST.get('order_key')

                # Calculate the total amount without delivery cost
                total_amount = cart['total']

                # Calculate the delivery cost separately
                delivery_cost = total - total_amount

                # Determine the delivery option
                delivery_option = request.POST.get('delivery_option', 'online')

                # Include delivery cost in total_paid for online delivery
                if delivery_option == 'online':
                    total_paid = str(total_amount + delivery_cost)
                else:
                    total_paid = str(total_amount)

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
                        state=state,
                        city=city,
                        zip_code=zip_code,
                        order_key=order_key,
                        total_paid=total_paid,
                        delivery_option=delivery_option,  # Set the delivery option
                    )
                    for cart_item in cart_items:
                        # Assuming 'product', 'quantity', and 'size' are keys in your cart item
                        product = cart_item['product']
                        quantity = cart_item['quantity']
                        selected_size = cart_item.get('size', 'S')  # Replace 'S' with the default size if not present

                        # Get the price for the selected size
                        price_for_size = product.get_discounted_price_for_size(selected_size)

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            size=selected_size,
                            price=price_for_size,  # Set the price for the selected size
                        )

                    # Update the order total, delivery cost, and grand total
                    order.update_total()

                    # Set billing status to True since the payment is successful
                    order.billing_status = True
                    order.save()

                    # Send confirmation email
                    send_payment_confirmation_email(order.email, order_key, total_paid)

                    # Clear the cart only if the payment was successful
                    request.session['cart'] = {}
                    return JsonResponse({'success': True, 'message': 'Order added successfully'})
            return JsonResponse({'success': False, 'message': 'Invalid request'})
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

        # Inside the basket_view function
        delivery_option = request.GET.get('delivery_option', 'online')

        # Fetch other cart details from cart_contents
        cart = cart_contents(request)
  

        # Update the cart with the latest delivery option
        cart['delivery_option'] = delivery_option

        # Initialize my_profile and primary_address
        my_profile = None
        primary_address = None

        # Check if the user has a profile
        try:
            my_profile = Profile.objects.get(user=request.user)
            primary_address = my_profile if my_profile.is_primary_address else None
        except Profile.DoesNotExist:
            pass

        # Check if the delivery option is 'pickup' and adjust the total accordingly
        if 'delivery_option' in cart and cart['delivery_option'] == 'pickup':
            total_final = cart.get('total', 0)  # Use the total without delivery cost for 'pickup'
            delivery_cost = 0  # Set delivery cost to 0 for 'pickup'
        else:
            total_final = cart.get('grand_total', 0)  # Use the grand total for 'online'
            delivery_cost = cart.get('delivery', 0)  # Include delivery cost for 'online'

        # Apply any discount logic here
        discount_amount = cart.get('discount', 0)
        total_final -= discount_amount

        total_sum = "{:.2f}".format(total_final)
        total = int(total_final * 100)
        stripe_public_key = settings.STRIPE_PUBLIC_KEY
        stripe.api_key = settings.STRIPE_SECRET_KEY

        intent = stripe.PaymentIntent.create(
            amount=total,
            currency='eur',
            metadata={'userid': request.user.id, 'delivery_option': delivery_option}
        )

        # Fetch user information from the latest order
        user_info = {
            'full_name': latest_order.full_name,
            'email': latest_order.email,
            'phone': latest_order.phone,
            'address1': latest_order.address1,
            'address2': latest_order.address2,
            'country': latest_order.country,
            'state': latest_order.state,
            'city': latest_order.city,
            'zip_code': latest_order.zip_code,
        }

        context = {
            'my_profile': my_profile,
            'primary_address': primary_address,
            'user_info': user_info,
            'total_sum': total_sum,
            'delivery_cost': delivery_cost,
            'delivery_option': delivery_option,  # Use the variable directly
            'client_secret': intent.client_secret,
            'stripe_public_key': stripe_public_key,
            'form': OrderForm(),
            'discount_amount': discount_amount,  # Include discount amount in context
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

        # Ensure amount_received is a float
        amount_received = float(payment_intent.amount_received) / 100

        # Send payment confirmation email
        send_payment_confirmation_email(order.email, order_key, amount_received)

        # Redirect to the order confirmation page
        return redirect('orders:order_confirmation')
    except Exception as e:
        logger.error(f"An error occurred in payment_confirmation: {str(e)}")
        # Handle the error and redirect accordingly
        return redirect('orders:error')


def send_payment_confirmation_email(customer_email, order_key, amount_received):
    BASE_URL = settings.BASE_URL

    # Ensure amount_received is a float
    amount_received = float(amount_received)

    formatted_amount = "{:.2f}".format(amount_received)

    subject = 'Payment Confirmation'
    order_detail_url = reverse('orders:order_details', args=[order_key])
    logo_url = 'https://cakecravingss-93e2bca9bc4c.herokuapp.com' + settings.STATIC_URL + 'images/login_page.png'
    marketing_sentence = "At Cake Cravings, we strive to make your moments sweet and memorable."

    order = Order.objects.get(order_key=order_key)
    order_items = order.order_item.all()

    # Construct the list of ordered items with product names and sizes
    ordered_items_list = "<ul>"
    for item in order_items:
        product_name = item.product.name
        product_size = item.size
        if item.size:
            product_name = f"{product_name} ({product_size})"
        ordered_items_list += f"<li><strong>{item.quantity} x {product_name}</strong></li>"
    ordered_items_list += "</ul>"

    order_detail_link = f'{BASE_URL}{order_detail_url}'

    # Replace order_key with order_id in the HTML content
    html_content = """
        <h1>Thank you for your order!</h1>
        <p>Your payment of <strong>€{}</strong> has been received. Your order ID is:<strong>{}</strong>.</p>
        <p>{}</p>
        <p>Your Order Details:</p>
        {}
        <p>Click <a href="{}">here</a> to view your order details.</p>
        <img src="{}" alt="Bakery Logo" width="100" height="50">
    """.format(formatted_amount, order.order_id, marketing_sentence, ordered_items_list, order_detail_link, logo_url)

    # Create an EmailMultiAlternatives instance
    msg = EmailMultiAlternatives(subject, strip_tags(html_content), 'jibinjjohny11@gmail.com', [customer_email])
    msg.attach_alternative(html_content, "text/html")

    # Send the email
    msg.send(fail_silently=False)


class OrderListView(LoginRequiredMixin, View):
    login_url = '/login/'  # Adjust the login URL as needed

    def get(self, request):
        print("Role:", request.user.profile.role)  # Debug print

        if request.user.profile.role == 'manager':
            orders = Order.objects.all().order_by('-created')
            print("Orders:", orders)  # Debug print
            return render(request, 'orders/order_list.html', {'orders': orders})
        else:
            return HttpResponseRedirect(reverse('home'))  # Redirect to home or another page for non-managers


class OrderStatusUpdateView(LoginRequiredMixin, View):
    login_url = '/login/'  # Adjust the login URL as needed

    def post(self, request, order_id):
        if request.user.profile.role == 'manager':
            order = get_object_or_404(Order, id=order_id)
            new_status = request.POST.get('new_status', '')
            new_delivery_option = request.POST.get('new_delivery_option', '')

            if new_status and new_status in dict(Order.STATUS_CHOICES).keys():
                order.status = new_status

            if new_delivery_option and new_delivery_option in dict(Order.DELIVERY_OPTIONS).keys():
                order.delivery_option = new_delivery_option

            order.save()
            return HttpResponseRedirect(reverse('orders:order-list'))
        else:
            return HttpResponseRedirect(reverse('home'))