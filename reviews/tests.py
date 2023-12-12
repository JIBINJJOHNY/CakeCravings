from django.test import TestCase
from django.contrib.auth.models import User
from products.models import Product
from orders.models import Order
from .models import Review

class ReviewModelTest(TestCase):
    def setUp(self):
        # Create a user, product, and order for testing
        self.user = User.objects.create(username='testuser')
        self.product = Product.objects.create(name='Test Product', price=10.0)
        self.order = Order.objects.create(user=self.user, total_paid=10.0)

    def test_review_creation(self):
        # Create a review and check if it's saved successfully
        review = Review.objects.create(
            user=self.user,
            product=self.product,
            order=self.order,
            rating=5,
            comment='Great product!',
        )

        self.assertEqual(review.user, self.user)
        self.assertEqual(review.product, self.product)
        self.assertEqual(review.order, self.order)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Great product!')

    def test_review_str_method(self):
        # Test the __str__ method of the Review model
        review = Review.objects.create(
            user=self.user,
            product=self.product,
            order=self.order,
            rating=4,
            comment='Nice product!',
        )

        expected_str = f'{self.user.username} - {self.product.name} - 4'
        self.assertEqual(str(review), expected_str)

    def test_review_ordering(self):
        # Test the ordering of reviews by created_at
        review1 = Review.objects.create(user=self.user, product=self.product, rating=3)
        review2 = Review.objects.create(user=self.user, product=self.product, rating=4)

        reviews = Review.objects.all()
        self.assertEqual(reviews[0], review2)
        self.assertEqual(reviews[1], review1)

