from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.view_cart, name='view_cart'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:product_id>/',views.update_cart, name='update_cart'),
    path('update_delivery_cost/',views.update_delivery_cost, name='update_delivery_cost'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
]
