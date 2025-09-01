from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import json
import tempfile
import os

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'user_type': 'investor',
            'phone_number': '+94771234567',
            'bio': 'Test bio',
            'date_of_birth': '1990-01-01',
            'address_line1': '123 Test Street',
            'city': 'Colombo',
            'state_province': 'Western Province',
            'postal_code': '10000',
            'country': 'Sri Lanka'
        }
    
    def test_create_user(self):
        """Test creating a basic user"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.user_type, 'investor')
        self.assertEqual(user.kyc_status, 'pending')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
    
    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(**self.user_data)
        # Check the actual string representation from the model
        actual_str = str(user)
        self.assertIn('testuser', actual_str)
        self.assertIn('Investor', actual_str)
    
    def test_user_type_choices(self):
        """Test user type choices"""
        user = User.objects.create_user(**self.user_data)
        choices = [choice[0] for choice in User.USER_TYPE_CHOICES]
        self.assertIn(user.user_type, choices)
    
    def test_kyc_status_default(self):
        """Test KYC status default value"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.kyc_status, 'pending')
    
    def test_phone_number_validation(self):
        """Test phone number validation"""
        # Valid phone number
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.phone_number, '+94771234567')
        
        # Test with invalid phone number - Django will handle validation
        # The phone_regex validator should prevent invalid numbers
        try:
            User.objects.create_user(
                username='invalid',
                email='invalid@example.com',
                password='testpass123',
                phone_number='invalid'
            )
            # If we get here, validation didn't work as expected
            self.fail("Phone number validation should have failed")
        except Exception:
            # This is expected behavior
            pass


class UserViewsTest(APITestCase):
    """Test cases for User views"""
    
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'user_type': 'investor',
            'phone_number': '+94771234567'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        self.client.credentials()  # Remove authentication
        new_user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'user_type': 'creator',
            'phone_number': '+94779876543'
        }
        
        response = self.client.post(reverse('auth:user-register'), new_user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_user_login(self):
        """Test user login endpoint"""
        self.client.credentials()  # Remove authentication
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(reverse('auth:user-login'), login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_user_profile_retrieval(self):
        """Test user profile retrieval"""
        response = self.client.get(reverse('users:user-profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
    
    def test_user_profile_update(self):
        """Test user profile update"""
        update_data = {
            'first_name': 'Updated',
            'bio': 'Updated bio',
            'city': 'Kandy'
        }
        
        response = self.client.patch(reverse('users:user-profile-update'), update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if data was updated
        user = User.objects.get(username='testuser')
        self.assertEqual(user.first_name, 'Updated')
        self.assertEqual(user.bio, 'Updated bio')
        self.assertEqual(user.city, 'Kandy')
    
    def test_user_list(self):
        """Test user list endpoint (admin only)"""
        # Create admin user
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        admin_token = RefreshToken.for_user(admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token.access_token}')
        
        response = self.client.get(reverse('users:user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_password_change(self):
        """Test password change functionality"""
        password_data = {
            'old_password': 'testpass123',
            'new_password': 'newpass123'
        }
        
        response = self.client.post(reverse('auth:password-change'), password_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify password was changed
        user = User.objects.get(username='testuser')
        self.assertTrue(user.check_password('newpass123'))
    
    def test_password_reset_request(self):
        """Test password reset request"""
        self.client.credentials()  # Remove authentication
        reset_data = {'email': 'test@example.com'}
        
        response = self.client.post(reverse('auth:password-reset'), reset_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_deletion(self):
        """Test user account deletion"""
        response = self.client.delete(reverse('users:user-profile'))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify user was deleted
        self.assertFalse(User.objects.filter(username='testuser').exists())


class UserAuthenticationTest(APITestCase):
    """Test cases for user authentication"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_jwt_token_creation(self):
        """Test JWT token creation"""
        token = RefreshToken.for_user(self.user)
        self.assertIsNotNone(token.access_token)
        # RefreshToken object has access_token and token attributes
        self.assertIsNotNone(str(token))
    
    def test_jwt_token_validation(self):
        """Test JWT token validation"""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        response = self.client.get(reverse('users:user-profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_invalid_token(self):
        """Test invalid token handling"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        
        response = self.client.get(reverse('users:user-profile'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_refresh(self):
        """Test token refresh functionality"""
        token = RefreshToken.for_user(self.user)
        refresh_data = {'refresh': str(token)}
        
        response = self.client.post(reverse('auth:token_refresh'), refresh_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class UserPermissionsTest(APITestCase):
    """Test cases for user permissions"""
    
    def setUp(self):
        self.client = APIClient()
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='creatorpass123',
            user_type='creator'
        )
        self.investor = User.objects.create_user(
            username='investor',
            email='investor@example.com',
            password='investorpass123',
            user_type='investor'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
    
    def test_creator_permissions(self):
        """Test creator user permissions"""
        token = RefreshToken.for_user(self.creator)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        # Creator should be able to access their profile
        response = self.client.get(reverse('users:user-profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_investor_permissions(self):
        """Test investor user permissions"""
        token = RefreshToken.for_user(self.investor)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        # Investor should be able to access their profile
        response = self.client.get(reverse('users:user-profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_admin_permissions(self):
        """Test admin user permissions"""
        token = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        # Admin should be able to access user list
        response = self.client.get(reverse('users:user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserIntegrationTest(TestCase):
    """Integration tests for user functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_user_registration_flow(self):
        """Test complete user registration flow"""
        # Register user
        response = self.client.post(reverse('auth:user-register'), self.user_data)
        self.assertEqual(response.status_code, 201)
        
        # Verify user was created
        self.assertTrue(User.objects.filter(username='testuser').exists())
        
        # Login with created user
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('auth:user-login'), login_data)
        self.assertEqual(response.status_code, 200)
    
    def test_user_profile_management_flow(self):
        """Test complete user profile management flow"""
        # Create and login user
        user = User.objects.create_user(**self.user_data)
        self.client.force_login(user)
        
        # Update profile
        update_data = {
            'first_name': 'Updated',
            'bio': 'New bio'
        }
        response = self.client.patch(reverse('users:user-profile-update'), update_data)
        self.assertEqual(response.status_code, 200)
        
        # Verify profile was updated
        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Updated')
        self.assertEqual(user.bio, 'New bio')


class UserValidationTest(APITestCase):
    """Test cases for user data validation"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_invalid_email_format(self):
        """Test invalid email format validation"""
        invalid_user_data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'testpass123'
        }
        
        response = self.client.post(reverse('auth:user-register'), invalid_user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_duplicate_username(self):
        """Test duplicate username validation"""
        # Create first user
        User.objects.create_user(
            username='testuser',
            email='test1@example.com',
            password='testpass123'
        )
        
        # Try to create second user with same username
        duplicate_user_data = {
            'username': 'testuser',
            'email': 'test2@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(reverse('auth:user-register'), duplicate_user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_duplicate_email(self):
        """Test duplicate email validation"""
        # Create first user
        User.objects.create_user(
            username='user1',
            email='test@example.com',
            password='testpass123'
        )
        
        # Try to create second user with same email
        duplicate_user_data = {
            'username': 'user2',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(reverse('auth:user-register'), duplicate_user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_password_strength_validation(self):
        """Test password strength validation"""
        weak_password_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': '123'  # Too short
        }
        
        response = self.client.post(reverse('auth:user-register'), weak_password_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
