from django.urls import path
from .views import AddOrder, basket_view, order_placed, OrdersView, OrderDetailsView, stripe_webhook

app_name = 'orders'

urlpatterns = [
    path('add_order/', AddOrder.as_view(), name='add_order'),
    path('basket_view/', basket_view, name='basket_view'),
    path('order_placed/', order_placed, name='order_placed'),
    path('user_orders/', OrdersView.as_view(), name='user_orders'),
    path('order_details/<str:order_number>/', OrderDetailsView.as_view(), name='order_details'), 
    path('stripe_webhook/', stripe_webhook, name='stripe_webhook'),
]
