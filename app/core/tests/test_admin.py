from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTest(TestCase):
    """docstring for AdminSiteTest."""

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='mehulraj@gmail.com',
            password='mehulraj'
        )

        # Keep the user Logged in
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='testuser@gmail.com',
            password='testuser',
            name='test user name'
        )

    def test_user_list(self):
        """Test for the listing of users on user page."""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.email)
        self.assertContains(res, self.user.name)

    def test_user_change_page(self):
        """Test that user edit page is working"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user(self):
        """Test that user create page works."""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
