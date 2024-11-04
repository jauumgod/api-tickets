from django.test import TestCase



from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()  # Use o modelo de usuário que você configurou

class CustomTokenObtainPairViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='spnoroeste',
            password='Organics@123',
            # Adicione outros campos necessários, como email, etc.
        )
        self.url = reverse('token_obtain_pair')  # Substitua pelo nome correto da URL

    def test_login_success(self):
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'testpassword',
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['username'], 'testuser')

    def test_login_invalid_credentials(self):
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'wrongpassword',
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('non_field_errors', response.data)

    def test_login_user_not_found(self):
        response = self.client.post(self.url, {
            'username': 'nonexistentuser',
            'password': 'any_password',
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('non_field_errors', response.data)
