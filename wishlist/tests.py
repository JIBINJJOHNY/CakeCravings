from django.test import TestCase
from django.contrib.auth.models import User
from products.models import Product
from .models import Wishlist


class WishlistModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.product1 = Product.objects.create(name='Test Product 1', description='Test Description 1', category=your_category_instance, price=50.0, availability='in_stock')
        self.product2 = Product.objects.create(name='Test Product 2', description='Test Description 2', category=your_category_instance, price=60.0, availability='in_stock')
        self.wishlist = Wishlist.objects.create(user=self.user)

    def test_wishlist_creation(self):
        self.assertEqual(str(self.wishlist), f"{self.user}'s wishlist")
        self.assertEqual(self.wishlist.get_products().count(), 0)

    def test_add_to_wishlist(self):
        self.assertTrue(self.wishlist.add_to_wishlist(self.product1))
        self.assertEqual(self.wishlist.get_products().count(), 1)
        # Adding the same product again should return False
        self.assertFalse(self.wishlist.add_to_wishlist(self.product1))  
    def test_remove_from_wishlist(self):
        self.wishlist.add_to_wishlist(self.product1)
        self.assertTrue(self.wishlist.remove_from_wishlist(self.product1))
        self.assertEqual(self.wishlist.get_products().count(), 0)
        # Removing a non-existent product should return False
        self.assertFalse(self.wishlist.remove_from_wishlist(self.product1))  

    def test_remove_all_from_wishlist(self):
        self.wishlist.add_to_wishlist(self.product1)
        self.wishlist.add_to_wishlist(self.product2)
        self.assertTrue(self.wishlist.remove_all_from_wishlist())
        self.assertEqual(self.wishlist.get_products().count(), 0)
