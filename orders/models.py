from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from shortuuid.django_fields import ShortUUIDField  # Import shortUUIDField

class Order(models.Model):
    PENDING = 'Pending'
    PROCESSING = 'Processing'
    SHIPPED = 'Shipped'
    DELIVERED = 'Delivered'
    READY_FOR_PICKUP = 'Ready For Pickup'

    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered'),
        (READY_FOR_PICKUP, 'Ready For Pickup'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='order_user'
    )
    full_name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=100, blank=True)
    address1 = models.CharField(max_length=250)
    address2 = models.CharField(max_length=250, blank=True)
    city = models.CharField(max_length=100)
    county_region_state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    total_paid = models.DecimalField(max_digits=5, decimal_places=2)
    order_id = ShortUUIDField(
        unique=True,
        max_length=20,  # Adjusted max_length here
        prefix='cc',
        alphabet='abcdefgh12345'
    )
    order_key = models.CharField(max_length=200, blank=True, null=True)
    billing_status = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING
    )

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.order_id)

    def get_order_items(self):
        items = OrderItem.objects.filter(order=self)
        return items


class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='order_item')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return str(self.id)



