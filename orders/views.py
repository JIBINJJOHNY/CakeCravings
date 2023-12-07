from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import Paginator
from django.db.models import Q
from products.models import Product
from reviews.models import Review
from .models import Order, OrderItem
from cart.contexts import cart_contents
from .forms import OrderForm, OrderItemForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
class AddOrder(View):
    """View for adding order AJAX."""
    
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.is_ajax():
                # Use your own logic to calculate total based on products in the cart
                cart = cart_contents(request)
                promo_price = bag['promo_price']
                if promo_price and promo_price != 0:
                    total_final = promo_price
                else:
                    total_final = cart['total']
                
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
                
                # Use your own logic to get products from the cart
                cart_items = cart['cart_items']
                
                if Order.objects.filter(order_key=order_key).exists():
                    pass
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
                        total_paid=str(total_final),
                    )
                    
                    for item in cart_items:
                        # Assuming 'product_id' is a key in your bag item
                        product_id = item['product_id']
                        product = get_object_or_404(Product, id=product_id)
                        
                        OrderItem.objects.create(
                            order=order,
                            quantity=item['quantity'],
                        )
                
                return JsonResponse({'success': True})
            
            return JsonResponse({'success': False})
        else:
            return render(request, 'account/login.html')

def payment_confirmation(data):
    # Update billing status
    Order.objects.filter(order_key=data).update(billing_status=True)

    # Get order details
    order = get_object_or_404(Order, order_key=data)
    customer = order.user

    # Email content
    subject = 'Cake Cravings - Payment Confirmation'
    order_total_paid = order.total_paid
    order_num = str(order.order_number)

    # Construct link to order details
    link = reverse('orders:order-details', args=[str(order.id)])

    # Email configuration
    subject, from_email, to = 'Cake Cravings - Payment Confirmation', 'your-email@yourdomain.com', str(customer.email)
    text_content = ''
    html_content = f'<h1>Payment Confirmation - Cake Cravings</h2>' \
        f'<p>Your payment of ${order_total_paid} has been confirmed.</p>' \
        f'<p>You can view your order details by clicking on your order information link below:</p>' \
        f'<strong>Order ID: </strong>' \
        f'<a href={link}>{order_num}</a><br>' \
        f'<p>Thank you for shopping with Cake Cravings!</p>' \
        f'<em>Cake Cravings Shop</em>'

    # Send email
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)
class UserOrders(View):
    """View for user orders page."""
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
            p = Paginator(Order.objects.filter(user=user).filter(billing_status=True), 15)
            page = request.GET.get('page')
            orders = p.get_page(page)
            return render(request, 'orders/user_orders.html', {'orders': orders})
        else:
            return render(request, 'account/login.html')

class UserOrderDetails(View):
    """View for user order details page."""
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            order = get_object_or_404(Order, order_number=kwargs['order_number'])
            order_items = OrderItem.objects.filter(order=order)
            
            # ... (remaining code)
            
            context = {'order': order, 'order_items': order_items, 'products_in_reviews': products_in_reviews}
            if order.user == request.user:
                return render(request, 'orders/user_order_details.html', context)
            else:
                return render(request, 'profiles/access_denied.html')
        else:
            return render(request, 'account/login.html')


@login_required
def BasketView(request):
    """View for payment page."""
    my_profile = get_object_or_404(Profile, user=request.user)
    cart = cart_contents(request)

    total_final = cart['total']  # Assuming 'total' is the key in your cart context
    total_sum = str(total_final)
    total = total_sum.replace('.', '')
    total = int(total)

    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe.api_key = settings.STRIPE_SECRET_KEY

    intent = stripe.PaymentIntent.create(
        amount=total,
        currency='usd',
        metadata={'userid': request.user.id}
    )

    # Check if the user has addresses
    if request.user.addresses.count() == 0:
        pass
    else:
        # Check if there is a primary address
        if request.user.addresses.filter(is_primary=True).exists():
            primary_address = Address.objects.get(user=request.user, is_primary=True)
            context = {
                'my_profile': my_profile,
                'primary_address': primary_address,
                'total_sum': total_sum,
                'client_secret': intent.client_secret,
                'stripe_public_key': stripe_public_key,
            }
            return render(request, 'payment/payment.html', context)

    context = {
        'my_profile': my_profile,
        'total_sum': total_sum,
        'client_secret': intent.client_secret,
        'stripe_public_key': stripe_public_key,
    }
    return render(request, 'payment/payment.html', context)


def order_placed(request):
    """View for order placed page."""
    cart = cart_contents(request)
    bag_items = cart['cart_items']

    for item in bag_items:
        sold_product_inventory = item['product'].inventory  # Assuming you have a 'Product' model with an 'inventory' field
        sold_quantity = item['quantity']

        # Update inventory
        sold_product_inventory.units_sold += sold_quantity
        sold_product_inventory.units -= sold_quantity
        sold_product_inventory.save()

    # Clear the bag
    request.session['cake_cravings_cart'] = {}

    return render(request, 'payment/order_placed.html')

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

class StripeWebhookView(View):
    @staticmethod
    @csrf_exempt
    def post(request, *args, **kwargs):
        payload = request.body
        event = None
        try:
            event = stripe.Event.construct_from(
                json.loads(payload), stripe.api_key
            )
        except ValueError as e:
            return JsonResponse({'error': 'Invalid payload'}, status=400)

        # Handle the event as needed
        if event.type == 'payment_intent.succeeded':
            payment_confirmation(event.data.object.client_secret)
            # You can add more event handling logic here for other event types

        return JsonResponse({'message': 'Webhook received successfully'}, status=200)