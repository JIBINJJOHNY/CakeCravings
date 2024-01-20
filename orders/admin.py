# admin.py
from django.contrib import admin
from .models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin for the Order model."""
    list_display = (
        'user',
        'full_name',
        'order_key',
        'total_paid',
        'billing_status',
        'status',
        'order_total',    
        'delivery_cost',  
        'grand_total',    
    )
    list_filter = (
        'billing_status',
        'status',
    )
    search_fields = (
        'user__username',
        'full_name',
        'email',
        'phone',
        'address1',
        'address2',
        'country',
        'state',
        'city',
        'zip_code',
        'order_key',
        'total_paid',
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin for the OrderItem model."""
    list_display = (
        'order',
        'product',
        'quantity',
        'size',
    )
    list_filter = (
        'order',
        'product',
        'size',
    )
    search_fields = (
        'order__order_key',  #  search by order key
        'product__name',    #search by product name
        'quantity',
    )