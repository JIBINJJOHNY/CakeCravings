from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.db.models import Sum
from django.conf import settings
from shortuuid.django_fields import ShortUUIDField
from decimal import Decimal
from django.db.models import Sum, F, ExpressionWrapper, DecimalField

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
    GERMAN_STATES_CHOICES = (
        ('BW', 'Baden-Württemberg'),
        ('BY', 'Bavaria (Bayern)'),
        ('BE', 'Berlin'),
        ('BB', 'Brandenburg'),
        ('HB', 'Bremen'),
        ('HH', 'Hamburg'),
        ('HE', 'Hesse (Hessen)'),
        ('NI', 'Lower Saxony (Niedersachsen)'),
        ('MV', 'Mecklenburg-Western Pomerania (Mecklenburg-Vorpommern)'),
        ('NW', 'North Rhine-Westphalia (Nordrhein-Westfalen)'),
        ('RP', 'Rhineland-Palatinate (Rheinland-Pfalz)'),
        ('SL', 'Saarland'),
        ('SN', 'Saxony (Sachsen)'),
        ('ST', 'Saxony-Anhalt (Sachsen-Anhalt)'),
        ('SH', 'Schleswig-Holstein'),
        ('TH', 'Thuringia (Thüringen)'),
    )

    DELIVERY_OPTIONS = (
        ('online', 'Online Delivery'),
        ('pickup', 'Pickup'),
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
    state = models.CharField(
        max_length=100,
        choices=GERMAN_STATES_CHOICES,
        blank=True, 
        null=True,
    )
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    total_paid = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    order_id = ShortUUIDField(
        unique=True,
        max_length=30,
        prefix='cc',
        alphabet='abcdefgh12345'
    )
    order_key = models.CharField(max_length=200, blank=True, null=True)
    billing_status = models.BooleanField(default=False)
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default=PENDING
    )
    delivery_option = models.CharField(
        max_length=10,
        choices=DELIVERY_OPTIONS,
        default='online',
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
        # Calculate the order total by iterating through related OrderItem objects
        order_items = self.order_item.all()
        order_total = 0  # Initialize order_total

        for item in order_items:
            item_total = item.get_total()

            # If the item has a size, consider it for the order total calculation
            if item.size and item.size != 'None':
                order_total += item_total

        # Use 0 if the order total is None
        self.order_total = order_total if order_total is not None else Decimal('0.00')

        # Calculate the delivery cost separately
        if self.order_total < settings.FREE_DELIVERY_THRESHOLD and self.delivery_option == 'online':
            self.delivery_cost = self.order_total * (settings.STANDARD_DELIVERY_PERCENTAGE / Decimal('100.0'))
        else:
            self.delivery_cost = Decimal('0.00')

        # Calculate the grand total by adding order total and delivery cost
        self.grand_total = self.order_total + self.delivery_cost
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='order_item')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=5, choices=Product.SIZE_CHOICES, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Specify a default value

    def __str__(self):
        return f"{self.quantity} x {self.product.name}" + (f" ({self.size})" if self.size else "")

    def get_total(self):
        return self.quantity * self.price  # Use the price field for the calculation