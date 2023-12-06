from django.urls import path
from .views import OrdersView, OrderDetailsView, UpdateOrderStatusAJAXView, AddOrderAJAXView, UserOrdersView, UserOrderDetailsView

app_name = 'orders'

urlpatterns = [
    path('', OrdersView.as_view(), name='orders'),
    path('order_details/<int:order_id>/', OrderDetailsView.as_view(), name='order_details'),
    path('update_order_status/', UpdateOrderStatusAJAXView.as_view(), name='update_order_status_ajax'),
    path('add_order_ajax/', AddOrderAJAXView.as_view(), name='add_order_ajax'),
    path('user_orders/', UserOrdersView.as_view(), name='user_orders'),
    path('user_order_details/<str:order_number>/', UserOrderDetailsView.as_view(), name='user_order_details'),
]
