from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import KYCRequest, KYCDocument, KYCVerification
import json
import tempfile
import os
from datetime import date, timedelta

User = get_user_model()


class KYCRequestModelTest(TestCase):
    """Test cases for KYCRequest model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.kyc_data = {
            'user': self.user,
            'verification_level': 'basic',
            'legal_name': 'Test User Legal Name',
            'date_of_birth': date(1990, 1, 1),
            'nationality': 'Sri Lankan',
            'residential_address': '123 Test Street, Colombo, Sri Lanka',
            'identity_document_type': 'national_id',
            'identity_document_number': 'ABC123456789',
            'identity_document_expiry': date(2030, 12, 31),
            'address_proof_type': 'utility_bill',
            'address_proof_date': date(2024, 1, 1),
            'employment_status': 'employed',
            'employer_name': 'Test Company Ltd',
            'annual_income': 500000.00,
            'source_of_funds': 'salary',
            'risk_level': 'low'
        }
    
    def test_create_kyc_request(self):
        """Test creating a KYC request"""
        kyc_request = KYCRequest.objects.create(**self.kyc_data)
        self.assertEqual(kyc_request.user, self.user)
        self.assertEqual(kyc_request.status, 'pending')
        self.assertEqual(kyc_request.verification_level, 'basic')
        self.assertEqual(kyc_request.legal_name, 'Test User Legal Name')
    
    def test_kyc_request_str_representation(self):
        """Test KYC request string representation"""
        kyc_request = KYCRequest.objects.create(**self.kyc_data)
        expected = f"KYC Request for {kyc_request.user.username} - {kyc_request.get_status_display()}"
        self.assertEqual(str(kyc_request), expected)
    
    def test_kyc_status_choices(self):
        """Test KYC status choices"""
        kyc_request = KYCRequest.objects.create(**self.kyc_data)
        choices = [choice[0] for choice in KYCRequest.STATUS_CHOICES]
        self.assertIn(kyc_request.status, choices)
    
    def test_verification_level_choices(self):
        """Test verification level choices"""
        kyc_request = KYCRequest.objects.create(**self.kyc_data)
        choices = [choice[0] for choice in KYCRequest.VERIFICATION_LEVEL_CHOICES]
        self.assertIn(kyc_request.verification_level, choices)
    
    def test_kyc_request_defaults(self):
        """Test KYC request default values"""
        kyc_request = KYCRequest.objects.create(**self.kyc_data)
        self.assertEqual(kyc_request.status, 'pending')
        self.assertIsNotNone(kyc_request.created_at)
        self.assertIsNotNone(kyc_request.updated_at)
    
    def test_kyc_request_validation(self):
        """Test KYC request validation"""
        # Test required fields
        incomplete_data = self.kyc_data.copy()
        del incomplete_data['legal_name']
        
        with self.assertRaises(Exception):
            KYCRequest.objects.create(**incomplete_data)


class KYCDocumentModelTest(TestCase):
    """Test cases for KYCDocument model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.kyc_request = KYCRequest.objects.create(
            user=self.user,
            verification_level='basic',
            legal_name='Test User',
            date_of_birth=date(1990, 1, 1),
            nationality='Sri Lankan',
            residential_address='123 Test Street',
            identity_document_type='national_id',
            identity_document_number='ABC123456789',
            address_proof_type='utility_bill',
            address_proof_date=date(2024, 1, 1),
            employment_status='employed',
            employer_name='Test Company',
            annual_income=500000.00,
            source_of_funds='salary',
            risk_level='low'
        )
        
        # Create a temporary file for testing
        self.temp_file = SimpleUploadedFile(
            "test_document.pdf",
            b"file_content",
            content_type="application/pdf"
        )
    
    def test_create_kyc_document(self):
        """Test creating a KYC document"""
        document = KYCDocument.objects.create(
            kyc_request=self.kyc_request,
            document_type='identity_document',
            file=self.temp_file,
            description='Test identity document'
        )
        self.assertEqual(document.kyc_request, self.kyc_request)
        self.assertEqual(document.document_type, 'identity_document')
        self.assertEqual(document.description, 'Test identity document')
    
    def test_kyc_document_str_representation(self):
        """Test KYC document string representation"""
        document = KYCDocument.objects.create(
            kyc_request=self.kyc_request,
            document_type='identity_document',
            file=self.temp_file,
            description='Test identity document'
        )
        expected = f"{document.get_document_type_display()} for {self.kyc_request.user.username}"
        self.assertEqual(str(document), expected)
    
    def test_document_type_choices(self):
        """Test document type choices"""
        document = KYCDocument.objects.create(
            kyc_request=self.kyc_request,
            document_type='identity_document',
            file=self.temp_file
        )
        choices = [choice[0] for choice in KYCDocument.DOCUMENT_TYPE_CHOICES]
        self.assertIn(document.document_type, choices)


class KYCVerificationModelTest(TestCase):
    """Test cases for KYCVerification model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.kyc_request = KYCRequest.objects.create(
            user=self.user,
            verification_level='basic',
            legal_name='Test User',
            date_of_birth=date(1990, 1, 1),
            nationality='Sri Lankan',
            residential_address='123 Test Street',
            identity_document_type='national_id',
            identity_document_number='ABC123456789',
            address_proof_type='utility_bill',
            address_proof_date=date(2024, 1, 1),
            employment_status='employed',
            employer_name='Test Company',
            annual_income=500000.00,
            source_of_funds='salary',
            risk_level='low'
        )
    
    def test_create_kyc_verification(self):
        """Test creating a KYC verification record"""
        verification = KYCVerification.objects.create(
            kyc_request=self.kyc_request,
            verified_by=self.user,
            verification_status='approved',
            verification_notes='All documents verified successfully'
        )
        self.assertEqual(verification.kyc_request, self.kyc_request)
        self.assertEqual(verification.verification_status, 'approved')
        self.assertEqual(verification.verified_by, self.user)
    
    def test_verification_status_choices(self):
        """Test verification status choices"""
        verification = KYCVerification.objects.create(
            kyc_request=self.kyc_request,
            verified_by=self.user,
            verification_status='approved'
        )
        choices = [choice[0] for choice in KYCVerification.VERIFICATION_STATUS_CHOICES]
        self.assertIn(verification.verification_status, choices)


class KYCViewsTest(APITestCase):
    """Test cases for KYC views"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')
        
        self.kyc_data = {
            'verification_level': 'basic',
            'legal_name': 'Test User Legal Name',
            'date_of_birth': '1990-01-01',
            'nationality': 'Sri Lankan',
            'residential_address': '123 Test Street, Colombo, Sri Lanka',
            'identity_document_type': 'national_id',
            'identity_document_number': 'ABC123456789',
            'identity_document_expiry': '2030-12-31',
            'address_proof_type': 'utility_bill',
            'address_proof_date': '2024-01-01',
            'employment_status': 'employed',
            'employer_name': 'Test Company Ltd',
            'annual_income': '500000.00',
            'source_of_funds': 'salary',
            'risk_level': 'low'
        }
    
    def test_create_kyc_request(self):
        """Test creating a KYC request via API"""
        response = self.client.post(reverse('kyc:kyc-request-create'), self.kyc_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(KYCRequest.objects.filter(user=self.user).exists())
    
    def test_kyc_request_retrieval(self):
        """Test retrieving KYC request"""
        # Create KYC request first
        kyc_request = KYCRequest.objects.create(
            user=self.user,
            verification_level='basic',
            legal_name='Test User',
            date_of_birth=date(1990, 1, 1),
            nationality='Sri Lankan',
            residential_address='123 Test Street',
            identity_document_type='national_id',
            identity_document_number='ABC123456789',
            address_proof_type='utility_bill',
            address_proof_date=date(2024, 1, 1),
            employment_status='employed',
            employer_name='Test Company',
            annual_income=500000.00,
            source_of_funds='salary',
            risk_level='low'
        )
        
        response = self.client.get(reverse('kyc:kyc-request-detail', kwargs={'pk': kyc_request.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['legal_name'], 'Test User')
    
    def test_kyc_request_update(self):
        """Test updating KYC request"""
        # Create KYC request first
        kyc_request = KYCRequest.objects.create(
            user=self.user,
            verification_level='basic',
            legal_name='Test User',
            date_of_birth=date(1990, 1, 1),
            nationality='Sri Lankan',
            residential_address='123 Test Street',
            identity_document_type='national_id',
            identity_document_number='ABC123456789',
            address_proof_type='utility_bill',
            address_proof_date=date(2024, 1, 1),
            employment_status='employed',
            employer_name='Test Company',
            annual_income=500000.00,
            source_of_funds='salary',
            risk_level='low'
        )
        
        update_data = {
            'legal_name': 'Updated Legal Name',
            'employer_name': 'Updated Company'
        }
        
        response = self.client.patch(
            reverse('kyc:kyc-request-detail', kwargs={'pk': kyc_request.pk}),
            update_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify data was updated
        kyc_request.refresh_from_db()
        self.assertEqual(kyc_request.legal_name, 'Updated Legal Name')
        self.assertEqual(kyc_request.employer_name, 'Updated Company')
    
    def test_kyc_request_list(self):
        """Test KYC request list endpoint"""
        # Create KYC request first
        KYCRequest.objects.create(
            user=self.user,
            verification_level='basic',
            legal_name='Test User',
            date_of_birth=date(1990, 1, 1),
            nationality='Sri Lankan',
            residential_address='123 Test Street',
            identity_document_type='national_id',
            identity_document_number='ABC123456789',
            address_proof_type='utility_bill',
            address_proof_date=date(2024, 1, 1),
            employment_status='employed',
            employer_name='Test Company',
            annual_income=500000.00,
            source_of_funds='salary',
            risk_level='low'
        )
        
        response = self.client.get(reverse('kyc:kyc-request-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_kyc_request_submission(self):
        """Test KYC request submission workflow"""
        # Create KYC request
        response = self.client.post(reverse('kyc:kyc-request-create'), self.kyc_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Submit KYC request
        kyc_request = KYCRequest.objects.get(user=self.user)
        submit_data = {'action': 'submit'}
        
        response = self.client.post(
            reverse('kyc:kyc-request-submit', kwargs={'pk': kyc_request.pk}),
            submit_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify status changed to submitted
        kyc_request.refresh_from_db()
        self.assertEqual(kyc_request.status, 'submitted')


class KYCDocumentUploadTest(APITestCase):
    """Test cases for KYC document upload"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')
        
        self.kyc_request = KYCRequest.objects.create(
            user=self.user,
            verification_level='basic',
            legal_name='Test User',
            date_of_birth=date(1990, 1, 1),
            nationality='Sri Lankan',
            residential_address='123 Test Street',
            identity_document_type='national_id',
            identity_document_number='ABC123456789',
            address_proof_type='utility_bill',
            address_proof_date=date(2024, 1, 1),
            employment_status='employed',
            employer_name='Test Company',
            annual_income=500000.00,
            source_of_funds='salary',
            risk_level='low'
        )
    
    def test_document_upload(self):
        """Test KYC document upload"""
        # Create test file
        test_file = SimpleUploadedFile(
            "test_document.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        document_data = {
            'kyc_request': self.kyc_request.pk,
            'document_type': 'identity_document',
            'file': test_file,
            'description': 'Test identity document'
        }
        
        response = self.client.post(reverse('kyc:document-upload'), document_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(KYCDocument.objects.filter(kyc_request=self.kyc_request).exists())
    
    def test_document_retrieval(self):
        """Test KYC document retrieval"""
        # Create document first
        test_file = SimpleUploadedFile(
            "test_document.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        document = KYCDocument.objects.create(
            kyc_request=self.kyc_request,
            document_type='identity_document',
            file=test_file,
            description='Test identity document'
        )
        
        response = self.client.get(reverse('kyc:document-detail', kwargs={'pk': document.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['document_type'], 'identity_document')
    
    def test_document_list(self):
        """Test KYC document list endpoint"""
        # Create documents first
        test_file1 = SimpleUploadedFile(
            "test_document1.pdf",
            b"file_content1",
            content_type="application/pdf"
        )
        test_file2 = SimpleUploadedFile(
            "test_document2.pdf",
            b"file_content2",
            content_type="application/pdf"
        )
        
        KYCDocument.objects.create(
            kyc_request=self.kyc_request,
            document_type='identity_document',
            file=test_file1,
            description='Test identity document'
        )
        KYCDocument.objects.create(
            kyc_request=self.kyc_request,
            document_type='address_proof',
            file=test_file2,
            description='Test address proof'
        )
        
        response = self.client.get(reverse('kyc:document-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)


class KYCVerificationWorkflowTest(APITestCase):
    """Test cases for KYC verification workflow"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.kyc_request = KYCRequest.objects.create(
            user=self.user,
            verification_level='basic',
            legal_name='Test User',
            date_of_birth=date(1990, 1, 1),
            nationality='Sri Lankan',
            residential_address='123 Test Street',
            identity_document_type='national_id',
            identity_document_number='ABC123456789',
            address_proof_type='utility_bill',
            address_proof_date=date(2024, 1, 1),
            employment_status='employed',
            employer_name='Test Company',
            annual_income=500000.00,
            source_of_funds='salary',
            risk_level='low',
            status='submitted'
        )
    
    def test_kyc_verification_approval(self):
        """Test KYC verification approval workflow"""
        # Admin user verifies KYC
        admin_token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token.access_token}')
        
        verification_data = {
            'verification_status': 'approved',
            'verification_notes': 'All documents verified successfully'
        }
        
        response = self.client.post(
            reverse('kyc:kyc-verification', kwargs={'pk': self.kyc_request.pk}),
            verification_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify KYC request status changed
        self.kyc_request.refresh_from_db()
        self.assertEqual(self.kyc_request.status, 'approved')
        
        # Verify user KYC status changed
        self.user.refresh_from_db()
        self.assertEqual(self.user.kyc_status, 'verified')
    
    def test_kyc_verification_rejection(self):
        """Test KYC verification rejection workflow"""
        # Admin user rejects KYC
        admin_token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token.access_token}')
        
        verification_data = {
            'verification_status': 'rejected',
            'verification_notes': 'Documents incomplete, please provide additional information'
        }
        
        response = self.client.post(
            reverse('kyc:kyc-verification', kwargs={'pk': self.kyc_request.pk}),
            verification_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify KYC request status changed
        self.kyc_request.refresh_from_db()
        self.assertEqual(self.kyc_request.status, 'rejected')
        
        # Verify user KYC status changed
        self.user.refresh_from_db()
        self.assertEqual(self.user.kyc_status, 'rejected')
    
    def test_kyc_verification_requires_additional_info(self):
        """Test KYC verification requiring additional information"""
        # Admin user requests additional information
        admin_token = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token.access_token}')
        
        verification_data = {
            'verification_status': 'requires_additional_info',
            'verification_notes': 'Please provide additional proof of address'
        }
        
        response = self.client.post(
            reverse('kyc:kyc-verification', kwargs={'pk': self.kyc_request.pk}),
            verification_data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify KYC request status changed
        self.kyc_request.refresh_from_db()
        self.assertEqual(self.kyc_request.status, 'requires_additional_info')


class KYCIntegrationTest(TestCase):
    """Integration tests for KYC functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
    
    def test_complete_kyc_workflow(self):
        """Test complete KYC workflow from creation to verification"""
        # Step 1: Create KYC request
        kyc_data = {
            'verification_level': 'basic',
            'legal_name': 'Test User Legal Name',
            'date_of_birth': '1990-01-01',
            'nationality': 'Sri Lankan',
            'residential_address': '123 Test Street, Colombo, Sri Lanka',
            'identity_document_type': 'national_id',
            'identity_document_number': 'ABC123456789',
            'identity_document_expiry': '2030-12-31',
            'address_proof_type': 'utility_bill',
            'address_proof_date': '2024-01-01',
            'employment_status': 'employed',
            'employer_name': 'Test Company Ltd',
            'annual_income': '500000.00',
            'source_of_funds': 'salary',
            'risk_level': 'low'
        }
        
        response = self.client.post(reverse('kyc:kyc-request-create'), kyc_data)
        self.assertEqual(response.status_code, 201)
        
        # Step 2: Submit KYC request
        kyc_request = KYCRequest.objects.get(user=self.user)
        submit_data = {'action': 'submit'}
        
        response = self.client.post(
            reverse('kyc:kyc-request-submit', kwargs={'pk': kyc_request.pk}),
            submit_data
        )
        self.assertEqual(response.status_code, 200)
        
        # Step 3: Verify KYC request (admin action)
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.client.force_login(admin_user)
        
        verification_data = {
            'verification_status': 'approved',
            'verification_notes': 'All documents verified successfully'
        }
        
        response = self.client.post(
            reverse('kyc:kyc-verification', kwargs={'pk': kyc_request.pk}),
            verification_data
        )
        self.assertEqual(response.status_code, 201)
        
        # Verify final status
        kyc_request.refresh_from_db()
        self.assertEqual(kyc_request.status, 'approved')
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.kyc_status, 'verified')


class KYCValidationTest(APITestCase):
    """Test cases for KYC data validation"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')
    
    def test_invalid_date_format(self):
        """Test invalid date format validation"""
        invalid_kyc_data = {
            'verification_level': 'basic',
            'legal_name': 'Test User',
            'date_of_birth': 'invalid-date',
            'nationality': 'Sri Lankan',
            'residential_address': '123 Test Street',
            'identity_document_type': 'national_id',
            'identity_document_number': 'ABC123456789',
            'address_proof_type': 'utility_bill',
            'address_proof_date': 'invalid-date',
            'employment_status': 'employed',
            'employer_name': 'Test Company',
            'annual_income': '500000.00',
            'source_of_funds': 'salary',
            'risk_level': 'low'
        }
        
        response = self.client.post(reverse('kyc:kyc-request-create'), invalid_kyc_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_missing_required_fields(self):
        """Test missing required fields validation"""
        incomplete_kyc_data = {
            'verification_level': 'basic',
            'legal_name': 'Test User',
            # Missing required fields
        }
        
        response = self.client.post(reverse('kyc:kyc-request-create'), incomplete_kyc_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_annual_income(self):
        """Test invalid annual income validation"""
        invalid_kyc_data = {
            'verification_level': 'basic',
            'legal_name': 'Test User',
            'date_of_birth': '1990-01-01',
            'nationality': 'Sri Lankan',
            'residential_address': '123 Test Street',
            'identity_document_type': 'national_id',
            'identity_document_number': 'ABC123456789',
            'address_proof_type': 'utility_bill',
            'address_proof_date': '2024-01-01',
            'employment_status': 'employed',
            'employer_name': 'Test Company',
            'annual_income': '-1000.00',  # Negative income
            'source_of_funds': 'salary',
            'risk_level': 'low'
        }
        
        response = self.client.post(reverse('kyc:kyc-request-create'), invalid_kyc_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
