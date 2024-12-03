from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

class UserLoginTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email_address='testuser@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )

    def test_user_login_success(self):
        url = reverse('login')  # Adjust URL name as per your URL configuration
        data = {
            'username': 'testuser',
            'password': 'password123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        user = authenticate(username='testuser', password='password123')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')

    def test_user_login_failure(self):
        url = reverse('login')  # Adjust URL name as per your URL configuration
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')
