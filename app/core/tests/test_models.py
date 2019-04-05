from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def sample_user(email="prueba@admin.com", password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTest(TestCase):

    def test_create_user_with_email_successful(self):
        """Testing the user creation with email"""
        email = "test@admin.com"
        password = 'Testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password, password)

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'admin@TEST.com'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_create_user_invalid_email(self):
        """Test creating user with no email raises error"""
        """If this clause raises an error, the test will be OK"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, '')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        email = 'test@admin.com'
        password = 'Test123'

        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)
