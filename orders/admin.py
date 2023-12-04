# admin.py
from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # Number of empty forms to display for adding related OrderItem objects

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'full_name', 'email', 'created', 'status']
    inlines = [OrderItemInline]

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'size']

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
