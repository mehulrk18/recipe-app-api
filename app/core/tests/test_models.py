from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email(self):
        """Test for creating use with email"""

        email = 'mehulraj@gmail.com'
        password = 'mehulraj'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email of new user is normalized"""
        email = 'mehulraj@GMAIL.COM'
        password = 'mehulraj'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email.lower())

    def test_validate_email_for_new_user(self):
        """Test for validating email address"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'mehulraj')

    def test_create_superuser(self):
        """Test for creating super user"""
        user = get_user_model().objects.create_superuser(
            'mehulraj@gmail.com',
            'mehulraj'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
