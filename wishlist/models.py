from django.db import models
from django.contrib.auth.models import User
from products.models import Product

class Wishlist(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='wishlist'
    )
    products = models.ManyToManyField(
        Product,
        blank=True,
        related_name='wishlists'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Wishlist'
        verbose_name_plural = 'Wishlists'

    def __str__(self):
        return str(self.user) + '\'s wishlist'

    def add_to_wishlist(self, product):
        if product not in self.products.all():
            self.products.add(product)
            return True
        return False

    def remove_from_wishlist(self, product):
        if product in self.products.all():
            self.products.remove(product)
            return True
        return False

    def remove_all_from_wishlist(self):
        self.products.clear()
        return True

    def get_products(self):
        return self.products.all()
