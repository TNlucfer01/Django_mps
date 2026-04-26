from django.test import TestCase
from django.contrib.auth.models import User
from products.models import Product, Category
from reviews.models import Review

class ReviewSignalTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Test Phone",
            price=100.00,
            category=self.category
        )
        self.user = User.objects.create_user(username="testuser", password="password")

    def test_rating_updated_on_review_save(self):
        # Create an approved review
        Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment="Great!",
            is_approved=True
        )
        
        # Refresh product from DB
        self.product.refresh_from_db()
        self.assertEqual(self.product.review_count, 1)
        self.assertEqual(float(self.product.average_rating), 5.0)

    def test_rating_updated_on_review_delete(self):
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment="Great!",
            is_approved=True
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.review_count, 1)

        review.delete()
        self.product.refresh_from_db()
        self.assertEqual(self.product.review_count, 0)
        self.assertEqual(float(self.product.average_rating), 0.0)
