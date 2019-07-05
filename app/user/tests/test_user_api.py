from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUsersApiTest(TestCase):
    """Test users API (Public)."""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_users(self):
        """Test that using valid payload users are created"""
        payload = {
                'email': 'test@gmail.com',
                'password': 'testpass',
                'name': 'Test Name'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test for existance of user"""
        payload = {'email': 'test@gmail.com', 'password': 'testpass'}
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that password should be more than 4 characters"""
        payload = {'email': 'test@gmail.com', 'password': 'tp'}
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
                    email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for a user"""
        payload = {'email': 'test@gmail.com', 'password': 'testpass'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_user_invalid_credentials(self):
        """Test that token is not created if the user credentials
            are invalid"""
        create_user(email='test@gmail.com', password='testpass')
        payload = {'email': 'test@gmail.com', 'password': 'wrong'}

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_no_user(self):
        """Test for token not for no user"""
        payload = {'email': 'test@gmail.com', 'password': 'testpass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_fields(self):
        """Test for token not given if any field is missing"""
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_retrieve_user_unauthorized(self):
        """Test for authentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, 401)  # status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@gmail.com',
            password='testpass',
            name='Test Name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_profile_success(self):
        """Test for successfully retrieving user profile"""
        # No authentication here as Authentication is done in setUp().
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email':  self.user.email,
            'name': self.user.name
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed in the me url"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_profile_update(self):
        """Test for updating  user profile."""
        payload = {'name': 'new name', 'password': 'newtestpass'}
        res = self.client.patch(ME_URL, payload)

        # For updated value from db.
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
