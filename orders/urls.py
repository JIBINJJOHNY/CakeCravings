from django.urls import path
from .views import (
    AddOrder,
    UserOrders,
    UserOrderDetails,
    BasketView,
    order_placed,
    StripeWebhookView,
)

app_name = 'orders'  
urlpatterns = [
    path('add_order/', AddOrder.as_view(), name='add_order'),
    path('user_orders/', UserOrders.as_view(), name='user_orders'),
    path('user_order_details/<str:order_number>/', UserOrderDetails.as_view(), name='user_order_details'),
    path('basket/', BasketView, name='basket'),
    path('order_placed/', order_placed, name='order_placed'),
    path('stripe_webhook/', StripeWebhookView.as_view(), name='stripe_webhook'),

]
