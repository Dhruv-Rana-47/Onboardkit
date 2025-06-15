# accounts/tests.py
from django.test import TestCase
from django.urls import reverse
from .models import User

class AuthenticationTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='testpass123',
            role='ADMIN'
        )
        
    def test_admin_dashboard_access(self):
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin Dashboard")