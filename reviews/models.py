from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from orders.models import Order

class Review(models.Model):
    """Review model."""
    STAR_CHOICES = (
        ('1', '1'),  
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        blank=True,
        null=True,
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='reviews',
        null=True,
        blank=True,
    )
    rating = models.IntegerField(
        choices=STAR_CHOICES,
        default=1,  
    )
    comment = models.TextField(
        max_length=1000,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return string representation of the model."""
        return f'{self.user.username} - {self.product.name} - {self.rating}'

    class Meta:
        """Meta class."""
        ordering = ['-created_at']
        unique_together = ('user', 'product')
