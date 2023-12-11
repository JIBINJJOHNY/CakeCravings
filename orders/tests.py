from django.test import TestCase
from django.contrib.auth.models import User
from products.models import Product
from .models import Order, OrderItem
from decimal import Decimal
from django.utils import timezone

class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.product = Product.objects.create(name='Test Product', description='Test Description', category=your_category_instance, price=50.0, availability='in_stock')
        self.order = Order.objects.create(
            user=self.user,
            full_name='John Doe',
            email='john@example.com',
            phone='123456789',
            address1='Test Address 1',
            city='Test City',
            county_region_state='Test County',
            country='Test Country',
            zip_code='12345',
            total_paid=50.0,
            order_key='test_order_key',
            billing_status=False,
            status=Order.PENDING,
            order_total=50.0,
            delivery_cost=0.0,
            grand_total=50.0
        )
        self.order_item = OrderItem.objects.create(order=self.order, product=self.product, quantity=2, size='M')

    def test_order_creation(self):
        self.assertEqual(str(self.order), f"Order ID: {self.order.order_id}, Order Number: {self.order.order_key}, Order Total: ${self.order.order_total}")
        self.assertEqual(self.order.get_order_items().count(), 1)
        self.assertEqual(self.order.total_paid, 50.0)

    def test_update_total(self):
        self.order_item.quantity = 3
        self.order_item.save()
        self.order.update_total()
        self.assertEqual(self.order.order_total, 150.0)
        self.assertEqual(self.order.delivery_cost, 0.0)
        self.assertEqual(self.order.grand_total, 150.0)

class OrderItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.product = Product.objects.create(name='Test Product', description='Test Description', category=your_category_instance, price=50.0, availability='in_stock')
        self.order = Order.objects.create(
            user=self.user,
            full_name='Jibin johny',
            email='jibin@example.com',
            phone='123456789',
            address1='Test Address 1',
            city='Test City',
            county_region_state='Test County',
            country='Test Country',
            zip_code='12345',
            total_paid=50.0,
            order_key='test_order_key',
            billing_status=False,
            status=Order.PENDING,
            order_total=50.0,
            delivery_cost=0.0,
            grand_total=50.0
        )
        self.order_item = OrderItem.objects.create(order=self.order, product=self.product, quantity=2, size='M')

    def test_order_item_creation(self):
        self.assertEqual(str(self.order_item), "2 x Test Product (M)")
        self.assertEqual(self.order_item.get_total(), 100.0)
