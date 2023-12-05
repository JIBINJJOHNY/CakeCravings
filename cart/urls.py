from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.view_cart, name='view_cart'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('update_delivery_option/', views.update_delivery_option, name='update_delivery_option'),
    path('update_quantity_in_cart/', views.update_quantity_in_cart, name='update_quantity_in_cart'),
    path('remove_item_from_cart/',views.remove_item_from_cart, name='remove_item_from_cart'),
    path('update_delivery_cost/',views.update_delivery_cost, name='update_delivery_cost'),
]
