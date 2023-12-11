from django.test import TestCase
from django.utils import timezone
from .models import Category, Tag, Discount, Product, ProductImage

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category', is_active=True)

    def test_category_creation(self):
        category = Category.objects.create(name='Test Category', is_active=True)
        self.assertEqual(category.name, 'Test Category')
        self.assertTrue(category.is_active)
        self.assertIsNotNone(category.slug)

class TagModelTest(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(name='Test Tag', is_active=True)

    def test_tag_creation(self):
        tag = Tag.objects.create(name='Test Tag', is_active=True)
        self.assertEqual(tag.name, 'Test Tag')
        self.assertTrue(tag.is_active)
        self.assertIsNotNone(tag.slug)

class DiscountModelTest(TestCase):
    def setUp(self):
        self.discount = Discount.objects.create(
            percentage=10,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=1),
            is_active=True
        )
        def test_discount_validity(self):
            self.assertTrue(self.discount.is_valid())

        def test_discount_invalidity(self):
            invalid_discount = Discount.objects.create(
                percentage=10,
                start_date=timezone.now().date() + timezone.timedelta(days=2),
                end_date=timezone.now().date() + timezone.timedelta(days=3),
                is_active=True
            )
            self.assertFalse(invalid_discount.is_valid())
class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category', is_active=True)
        self.tag = Tag.objects.create(name='Test Tag', is_active=True)
        self.discount = Discount.objects.create(percentage=10, start_date=timezone.now().date(), end_date=timezone.now().date() + timezone.timedelta(days=1), is_active=True)

    def test_product_creation(self):
        product = Product.objects.create(name='Test Product', description='Test Description', category=self.category, price=50.0, discount_price=self.discount, availability='in_stock')
        product.tags.add(self.tag)

        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.description, 'Test Description')
        self.assertEqual(product.category, self.category)
        self.assertEqual(product.price, 45.0)  # Discounted price
        self.assertTrue(product.is_active)
        self.assertIsNotNone(product.slug)
        self.assertTrue(product.discount_price.is_valid())
        self.assertEqual(product.availability, 'in_stock')

class ProductImageModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category', is_active=True)
        self.product = Product.objects.create(name='Test Product', description='Test Description', category=self.category, price=50.0, availability='in_stock')
        self.product_image = ProductImage.objects.create(product=self.product, alt_text='Test Alt Text', default_image=True, is_active=True)

    def test_product_image_creation(self):
        self.assertEqual(self.product_image.product, self.product)
        self.assertEqual(self.product_image.alt_text, 'Test Alt Text')
        self.assertTrue(self.product_image.default_image)
        self.assertTrue(self.product_image.is_active)
        self.assertIsNotNone(self.product_image.image_url)
