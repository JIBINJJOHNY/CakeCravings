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

class OrdersView(View):
    """View for orders page."""
    
    def get(self, request):
        """Get method for orders page."""
        if request.user.is_authenticated:
            # Check if user is an admin
            if request.user.profile.role.id == 1:
                return render(request, 'profiles/access_denied.html')
            else:
                p = Paginator(Order.objects.all(), 25)
                page = request.GET.get('page')
                orders = p.get_page(page)
                context = {'orders': orders}
                
                # ... (remaining code)

class OrderDetailsView(View):
    """View for order full page."""
    
    def get(self, request, *args, **kwargs):
        """Get method for order details page."""
        if request.user.is_authenticated:
            if request.user.profile.role.id == 1:
                return render(request, 'profiles/access_denied.html')
            else:
                order_id = kwargs['order_id']
                order = get_object_or_404(Order, id=order_id)
                order_items = OrderItem.objects.filter(order=order)
                context = {'order': order, 'order_items': order_items}
                return render(request, 'orders/order_details.html', context)
        else:
            return render(request, 'account/login.html')

class UpdateOrderStatusAJAXView(View):
    """View for updating order status with access only for admin and logistic manager."""
    
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user_role = request.user.profile.role.id
            if user_role == 3 or user_role == 4:
                if request.is_ajax():
                    order_id = request.POST.get('order_id')
                    order = get_object_or_404(Order, id=order_id)
                    order.status = request.POST.get('order_status')
                    order.save()
                    return JsonResponse({'success': True, 'order_status': order.status})
                else:
                    return JsonResponse({'success': False})
            else:
                return render(request, 'profiles/access_denied.html')
        else:
            return render(request, 'account/login.html')

class AddOrderAJAXView(View):
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
    order = Order.objects.get(order_key=data)
    order_id = order.id
    order_obj = Order.objects.get(id=order_id)
    customer = order_obj.user

    # Email content
    subject = 'Cake Cravings - Payment Confirmation'
    order_total_paid = order_obj.total_paid
    order_num = str(order_obj.order_number)

    # Construct link to order details
    link = 'https://cake-cravings-website.com/orders/' + str(customer.username) + '/my_orders/' + order_num + '/'

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
class UserOrdersView(View):
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

class UserOrderDetailsView(View):
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
