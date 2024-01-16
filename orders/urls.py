from django.urls import path
from .views import AddOrder, basket_view, OrderConfirmation, OrdersView, OrderDetailsView, stripe_webhook, ErrorView


app_name = 'orders'

urlpatterns = [
    path('add_order/', AddOrder.as_view(), name='add_order'),
    path('basket_view/', basket_view, name='basket_view'),
    path('error/', ErrorView.as_view(), name='error'),
    path('order_confirmation/', OrderConfirmation.as_view(), name='order_confirmation'),
    path('user_orders/', OrdersView.as_view(), name='user_orders'),
    path('order_details/<str:order_number>/', OrderDetailsView.as_view(), name='order_details'), 
    path('stripe_webhook/', stripe_webhook, name='stripe_webhook'),


]
