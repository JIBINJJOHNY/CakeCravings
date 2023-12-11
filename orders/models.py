from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.db.models import Sum
from django.conf import settings
from shortuuid.django_fields import ShortUUIDField


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
        max_length=20,
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
    order_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f"Order ID: {self.order_id}, Order Number: {self.order_key}, Order Total: ${self.order_total}"


    def get_order_items(self):
        items = OrderItem.objects.filter(order=self)
        return items
    def update_total(self):
        """
        Update order total, delivery cost, and grand total.
        """
        # Calculate the order total using aggregate
        order_total_aggregate = self.order_item.aggregate(Sum('product__price'))['product__price__sum']

        # Use 0 if the order_total_aggregate is None
        self.order_total = order_total_aggregate if order_total_aggregate is not None else 0

        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = self.order_total * settings.STANDARD_DELIVERY_PERCENTAGE / 100
        else:
            self.delivery_cost = 0

        self.grand_total = self.order_total + self.delivery_cost
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='order_item')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=5, choices=Product.SIZE_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}" + (f" ({self.size})" if self.size else "")

    def get_total(self):
            return self.quantity * self.product.price

