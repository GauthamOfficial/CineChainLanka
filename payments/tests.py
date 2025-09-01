from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import PaymentMethod, Transaction, PaymentGateway, Refund
from users.models import User
from campaigns.models import Campaign, CampaignCategory
import json
from decimal import Decimal
from datetime import date, timedelta

User = get_user_model()


class PaymentMethodModelTest(TestCase):
    """Test cases for PaymentMethod model"""
    
    def setUp(self):
        self.payment_method_data = {
            'name': 'LankaQR',
            'payment_type': 'lanka_qr',
            'description': 'Sri Lanka QR code payment system',
            'is_active': True,
            'processing_fee_percentage': Decimal('2.50'),
            'processing_fee_fixed': Decimal('10.00'),
            'minimum_amount': Decimal('100.00'),
            'maximum_amount': Decimal('100000.00'),
            'config_data': {
                'api_key': 'test_key',
                'merchant_id': 'test_merchant'
            }
        }
    
    def test_create_payment_method(self):
        """Test creating a payment method"""
        payment_method = PaymentMethod.objects.create(**self.payment_method_data)
        self.assertEqual(payment_method.name, 'LankaQR')
        self.assertEqual(payment_method.payment_type, 'lanka_qr')
        self.assertEqual(payment_method.processing_fee_percentage, Decimal('2.50'))
        self.assertTrue(payment_method.is_active)
    
    def test_payment_method_str_representation(self):
        """Test payment method string representation"""
        payment_method = PaymentMethod.objects.create(**self.payment_method_data)
        expected = f"LankaQR (LankaQR)"
        self.assertEqual(str(payment_method), expected)
    
    def test_payment_type_choices(self):
        """Test payment type choices"""
        payment_method = PaymentMethod.objects.create(**self.payment_method_data)
        choices = [choice[0] for choice in PaymentMethod.PAYMENT_TYPE_CHOICES]
        self.assertIn(payment_method.payment_type, choices)
    
    def test_fee_calculation(self):
        """Test processing fee calculation"""
        payment_method = PaymentMethod.objects.create(**self.payment_method_data)
        
        # Test with amount 1000.00
        amount = Decimal('1000.00')
        expected_fee = (amount * Decimal('2.50') / 100) + Decimal('10.00')
        calculated_fee = payment_method.calculate_fee(amount)
        
        self.assertEqual(calculated_fee, expected_fee)
    
    def test_amount_validation(self):
        """Test amount validation within limits"""
        payment_method = PaymentMethod.objects.create(**self.payment_method_data)
        
        # Test minimum amount
        self.assertTrue(payment_method.minimum_amount <= Decimal('100.00'))
        
        # Test maximum amount
        self.assertTrue(payment_method.maximum_amount >= Decimal('100000.00'))


class TransactionModelTest(TestCase):
    """Test cases for Transaction model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='investor',
            email='investor@example.com',
            password='investorpass123',
            user_type='investor'
        )
        
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='creatorpass123',
            user_type='creator'
        )
        
        self.category = CampaignCategory.objects.create(
            name='Feature Film',
            description='Full-length feature films'
        )
        
        self.campaign = Campaign.objects.create(
            creator=self.creator,
            title='Test Film Campaign',
            description='Test description',
            short_description='Short description',
            category=self.category,
            funding_goal=Decimal('1000000.00'),
            funding_deadline=date.today() + timedelta(days=30),
            campaign_duration=30,
            min_investment=Decimal('1000.00'),
            max_investment=Decimal('100000.00'),
            equity_offered=Decimal('20.00')
        )
        
        self.payment_method = PaymentMethod.objects.create(
            name='LankaQR',
            payment_type='lanka_qr',
            description='Sri Lanka QR code payment system',
            is_active=True,
            processing_fee_percentage=Decimal('2.50'),
            processing_fee_fixed=Decimal('10.00'),
            minimum_amount=Decimal('100.00'),
            maximum_amount=Decimal('100000.00')
        )
        
        self.transaction_data = {
            'user': self.user,
            'campaign': self.campaign,
            'payment_method': self.payment_method,
            'amount': Decimal('5000.00'),
            'currency': 'LKR',
            'transaction_type': 'investment',
            'status': 'pending',
            'reference_id': 'TXN123456789',
            'gateway_reference': 'GW123456789',
            'description': 'Investment in Test Film Campaign'
        }
    
    def test_create_transaction(self):
        """Test creating a transaction"""
        transaction = Transaction.objects.create(**self.transaction_data)
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.campaign, self.campaign)
        self.assertEqual(transaction.amount, Decimal('5000.00'))
        self.assertEqual(transaction.status, 'pending')
        self.assertEqual(transaction.transaction_type, 'investment')
    
    def test_transaction_str_representation(self):
        """Test transaction string representation"""
        transaction = Transaction.objects.create(**self.transaction_data)
        expected = f"TXN123456789 - {self.user.username} - LKR 5000.00"
        self.assertEqual(str(transaction), expected)
    
    def test_transaction_status_choices(self):
        """Test transaction status choices"""
        transaction = Transaction.objects.create(**self.transaction_data)
        choices = [choice[0] for choice in Transaction.STATUS_CHOICES]
        self.assertIn(transaction.status, choices)
    
    def test_transaction_type_choices(self):
        """Test transaction type choices"""
        transaction = Transaction.objects.create(**self.transaction_data)
        choices = [choice[0] for choice in Transaction.TRANSACTION_TYPE_CHOICES]
        self.assertIn(transaction.transaction_type, choices)
    
    def test_transaction_currency_choices(self):
        """Test transaction currency choices"""
        transaction = Transaction.objects.create(**self.transaction_data)
        choices = [choice[0] for choice in Transaction.CURRENCY_CHOICES]
        self.assertIn(transaction.currency, choices)
    
    def test_transaction_defaults(self):
        """Test transaction default values"""
        transaction = Transaction.objects.create(**self.transaction_data)
        self.assertIsNotNone(transaction.created_at)
        self.assertIsNotNone(transaction.updated_at)
        self.assertIsNone(transaction.processed_at)
        self.assertIsNone(transaction.failed_at)
    
    def test_transaction_status_transitions(self):
        """Test transaction status transitions"""
        transaction = Transaction.objects.create(**self.transaction_data)
        
        # Test pending to processing
        transaction.status = 'processing'
        transaction.save()
        self.assertEqual(transaction.status, 'processing')
        
        # Test processing to completed
        transaction.status = 'completed'
        transaction.processed_at = date.today()
        transaction.save()
        self.assertEqual(transaction.status, 'completed')
        self.assertIsNotNone(transaction.processed_at)
        
        # Test failed status
        transaction.status = 'failed'
        transaction.failed_at = date.today()
        transaction.save()
        self.assertEqual(transaction.status, 'failed')
        self.assertIsNotNone(transaction.failed_at)


class PaymentGatewayModelTest(TestCase):
    """Test cases for PaymentGateway model"""
    
    def setUp(self):
        self.gateway_data = {
            'name': 'Test Payment Gateway',
            'gateway_type': 'lanka_qr',
            'is_active': True,
            'api_key': 'test_api_key',
            'secret_key': 'test_secret_key',
            'merchant_id': 'test_merchant_id',
            'endpoint_url': 'https://test.gateway.com/api',
            'webhook_url': 'https://test.gateway.com/webhook',
            'config_data': {
                'test_mode': True,
                'timeout': 30
            }
        }
    
    def test_create_payment_gateway(self):
        """Test creating a payment gateway"""
        gateway = PaymentGateway.objects.create(**self.gateway_data)
        self.assertEqual(gateway.name, 'Test Payment Gateway')
        self.assertEqual(gateway.gateway_type, 'lanka_qr')
        self.assertTrue(gateway.is_active)
        self.assertEqual(gateway.api_key, 'test_api_key')
    
    def test_payment_gateway_str_representation(self):
        """Test payment gateway string representation"""
        gateway = PaymentGateway.objects.create(**self.gateway_data)
        expected = f"Test Payment Gateway ({gateway.get_gateway_type_display()})"
        self.assertEqual(str(gateway), expected)
    
    def test_gateway_type_choices(self):
        """Test gateway type choices"""
        gateway = PaymentGateway.objects.create(**self.gateway_data)
        choices = [choice[0] for choice in PaymentGateway.GATEWAY_TYPE_CHOICES]
        self.assertIn(gateway.gateway_type, choices)


class RefundModelTest(TestCase):
    """Test cases for Refund model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='investor',
            email='investor@example.com',
            password='investorpass123',
            user_type='investor'
        )
        
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='creatorpass123',
            user_type='creator'
        )
        
        self.category = CampaignCategory.objects.create(
            name='Feature Film',
            description='Full-length feature films'
        )
        
        self.campaign = Campaign.objects.create(
            creator=self.creator,
            title='Test Film Campaign',
            description='Test description',
            short_description='Short description',
            category=self.category,
            funding_goal=Decimal('1000000.00'),
            funding_deadline=date.today() + timedelta(days=30),
            campaign_duration=30,
            min_investment=Decimal('1000.00'),
            max_investment=Decimal('100000.00'),
            equity_offered=Decimal('20.00')
        )
        
        self.payment_method = PaymentMethod.objects.create(
            name='LankaQR',
            payment_type='lanka_qr',
            description='Sri Lanka QR code payment system',
            is_active=True,
            processing_fee_percentage=Decimal('2.50'),
            processing_fee_fixed=Decimal('10.00'),
            minimum_amount=Decimal('100.00'),
            maximum_amount=Decimal('100000.00')
        )
        
        self.transaction = Transaction.objects.create(
            user=self.user,
            campaign=self.campaign,
            payment_method=self.payment_method,
            amount=Decimal('5000.00'),
            currency='LKR',
            transaction_type='investment',
            status='completed',
            reference_id='TXN123456789',
            gateway_reference='GW123456789',
            description='Investment in Test Film Campaign'
        )
        
        self.refund_data = {
            'transaction': self.transaction,
            'amount': Decimal('5000.00'),
            'reason': 'Campaign failed to meet funding goal',
            'refund_type': 'full',
            'status': 'pending',
            'processed_by': self.user
        }
    
    def test_create_refund(self):
        """Test creating a refund"""
        refund = Refund.objects.create(**self.refund_data)
        self.assertEqual(refund.transaction, self.transaction)
        self.assertEqual(refund.amount, Decimal('5000.00'))
        self.assertEqual(refund.reason, 'Campaign failed to meet funding goal')
        self.assertEqual(refund.refund_type, 'full')
        self.assertEqual(refund.status, 'pending')
    
    def test_refund_str_representation(self):
        """Test refund string representation"""
        refund = Refund.objects.create(**self.refund_data)
        expected = f"Refund for TXN123456789 - LKR 5000.00"
        self.assertEqual(str(refund), expected)
    
    def test_refund_status_choices(self):
        """Test refund status choices"""
        refund = Refund.objects.create(**self.refund_data)
        choices = [choice[0] for choice in Refund.STATUS_CHOICES]
        self.assertIn(refund.status, choices)
    
    def test_refund_type_choices(self):
        """Test refund type choices"""
        refund = Refund.objects.create(**self.refund_data)
        choices = [choice[0] for choice in Refund.REFUND_TYPE_CHOICES]
        self.assertIn(refund.refund_type, choices)


class PaymentViewsTest(APITestCase):
    """Test cases for Payment views"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='investor',
            email='investor@example.com',
            password='investorpass123',
            user_type='investor'
        )
        
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='creatorpass123',
            user_type='creator'
        )
        
        self.category = CampaignCategory.objects.create(
            name='Feature Film',
            description='Full-length feature films'
        )
        
        self.campaign = Campaign.objects.create(
            creator=self.creator,
            title='Test Film Campaign',
            description='Test description',
            short_description='Short description',
            category=self.category,
            funding_goal=Decimal('1000000.00'),
            funding_deadline=date.today() + timedelta(days=30),
            campaign_duration=30,
            min_investment=Decimal('1000.00'),
            max_investment=Decimal('100000.00'),
            equity_offered=Decimal('20.00'),
            status='active'
        )
        
        self.payment_method = PaymentMethod.objects.create(
            name='LankaQR',
            payment_type='lanka_qr',
            description='Sri Lanka QR code payment system',
            is_active=True,
            processing_fee_percentage=Decimal('2.50'),
            processing_fee_fixed=Decimal('10.00'),
            minimum_amount=Decimal('100.00'),
            maximum_amount=Decimal('100000.00')
        )
        
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')
        
        self.payment_data = {
            'campaign': self.campaign.pk,
            'payment_method': self.payment_method.pk,
            'amount': '5000.00',
            'currency': 'LKR',
            'description': 'Investment in Test Film Campaign'
        }
    
    def test_initiate_payment(self):
        """Test initiating a payment"""
        response = self.client.post(reverse('payments:initiate-payment'), self.payment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Transaction.objects.filter(user=self.user, campaign=self.campaign).exists())
    
    def test_payment_method_list(self):
        """Test payment method list endpoint"""
        response = self.client.get(reverse('payments:payment-method-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_payment_method_detail(self):
        """Test payment method detail endpoint"""
        response = self.client.get(
            reverse('payments:payment-method-detail', kwargs={'pk': self.payment_method.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'LankaQR')
    
    def test_transaction_list(self):
        """Test transaction list endpoint"""
        # Create a transaction first
        transaction = Transaction.objects.create(
            user=self.user,
            campaign=self.campaign,
            payment_method=self.payment_method,
            amount=Decimal('5000.00'),
            currency='LKR',
            transaction_type='investment',
            status='pending',
            reference_id='TXN123456789',
            gateway_reference='GW123456789',
            description='Investment in Test Film Campaign'
        )
        
        response = self.client.get(reverse('payments:transaction-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_transaction_detail(self):
        """Test transaction detail endpoint"""
        # Create a transaction first
        transaction = Transaction.objects.create(
            user=self.user,
            campaign=self.campaign,
            payment_method=self.payment_method,
            amount=Decimal('5000.00'),
            currency='LKR',
            transaction_type='investment',
            status='pending',
            reference_id='TXN123456789',
            gateway_reference='GW123456789',
            description='Investment in Test Film Campaign'
        )
        
        response = self.client.get(
            reverse('payments:transaction-detail', kwargs={'pk': transaction.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], '5000.00')
    
    def test_payment_webhook(self):
        """Test payment webhook endpoint"""
        # Create a transaction first
        transaction = Transaction.objects.create(
            user=self.user,
            campaign=self.campaign,
            payment_method=self.payment_method,
            amount=Decimal('5000.00'),
            currency='LKR',
            transaction_type='investment',
            status='pending',
            reference_id='TXN123456789',
            gateway_reference='GW123456789',
            description='Investment in Test Film Campaign'
        )
        
        webhook_data = {
            'transaction_id': transaction.reference_id,
            'status': 'completed',
            'gateway_reference': 'GW123456789',
            'amount': '5000.00',
            'currency': 'LKR'
        }
        
        response = self.client.post(reverse('payments:payment-webhook'), webhook_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify transaction status was updated
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, 'completed')


class LocalPaymentIntegrationTest(APITestCase):
    """Test cases for local payment method integrations"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='investor',
            email='investor@example.com',
            password='investorpass123',
            user_type='investor'
        )
        
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='creatorpass123',
            user_type='creator'
        )
        
        self.category = CampaignCategory.objects.create(
            name='Feature Film',
            description='Full-length feature films'
        )
        
        self.campaign = Campaign.objects.create(
            creator=self.creator,
            title='Test Film Campaign',
            description='Test description',
            short_description='Short description',
            category=self.category,
            funding_goal=Decimal('1000000.00'),
            funding_deadline=date.today() + timedelta(days=30),
            campaign_duration=30,
            min_investment=Decimal('1000.00'),
            max_investment=Decimal('100000.00'),
            equity_offered=Decimal('20.00'),
            status='active'
        )
        
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')
    
    def test_lanka_qr_payment_integration(self):
        """Test LankaQR payment integration"""
        # Create LankaQR payment method
        lanka_qr_method = PaymentMethod.objects.create(
            name='LankaQR',
            payment_type='lanka_qr',
            description='Sri Lanka QR code payment system',
            is_active=True,
            processing_fee_percentage=Decimal('2.50'),
            processing_fee_fixed=Decimal('10.00'),
            minimum_amount=Decimal('100.00'),
            maximum_amount=Decimal('100000.00'),
            config_data={
                'merchant_id': 'test_merchant',
                'qr_code_url': 'https://test.qr.lankaqr.lk'
            }
        )
        
        payment_data = {
            'campaign': self.campaign.pk,
            'payment_method': lanka_qr_method.pk,
            'amount': '5000.00',
            'currency': 'LKR',
            'description': 'Investment via LankaQR'
        }
        
        response = self.client.post(reverse('payments:initiate-payment'), payment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify transaction was created
        transaction = Transaction.objects.get(user=self.user, campaign=self.campaign)
        self.assertEqual(transaction.payment_method, lanka_qr_method)
        self.assertEqual(transaction.amount, Decimal('5000.00'))
        self.assertEqual(transaction.status, 'pending')
    
    def test_ez_cash_payment_integration(self):
        """Test eZ Cash payment integration"""
        # Create eZ Cash payment method
        ez_cash_method = PaymentMethod.objects.create(
            name='eZ Cash',
            payment_type='ez_cash',
            description='eZ Cash mobile wallet',
            is_active=True,
            processing_fee_percentage=Decimal('1.50'),
            processing_fee_fixed=Decimal('5.00'),
            minimum_amount=Decimal('50.00'),
            maximum_amount=Decimal('50000.00'),
            config_data={
                'merchant_id': 'test_ez_merchant',
                'api_endpoint': 'https://test.ez.lk/api'
            }
        )
        
        payment_data = {
            'campaign': self.campaign.pk,
            'payment_method': ez_cash_method.pk,
            'amount': '2500.00',
            'currency': 'LKR',
            'description': 'Investment via eZ Cash'
        }
        
        response = self.client.post(reverse('payments:initiate-payment'), payment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify transaction was created
        transaction = Transaction.objects.get(user=self.user, campaign=self.campaign)
        self.assertEqual(transaction.payment_method, ez_cash_method)
        self.assertEqual(transaction.amount, Decimal('2500.00'))
    
    def test_frimi_payment_integration(self):
        """Test FriMi payment integration"""
        # Create FriMi payment method
        frimi_method = PaymentMethod.objects.create(
            name='FriMi',
            payment_type='frimi',
            description='FriMi digital wallet',
            is_active=True,
            processing_fee_percentage=Decimal('1.00'),
            processing_fee_fixed=Decimal('0.00'),
            minimum_amount=Decimal('100.00'),
            maximum_amount=Decimal('100000.00'),
            config_data={
                'merchant_id': 'test_frimi_merchant',
                'api_endpoint': 'https://test.frimi.lk/api'
            }
        )
        
        payment_data = {
            'campaign': self.campaign.pk,
            'payment_method': frimi_method.pk,
            'amount': '3000.00',
            'currency': 'LKR',
            'description': 'Investment via FriMi'
        }
        
        response = self.client.post(reverse('payments:initiate-payment'), payment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify transaction was created
        transaction = Transaction.objects.get(user=self.user, campaign=self.campaign)
        self.assertEqual(transaction.payment_method, frimi_method)
        self.assertEqual(transaction.amount, Decimal('3000.00'))


class PaymentProcessingTest(APITestCase):
    """Test cases for payment processing workflow"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='investor',
            email='investor@example.com',
            password='investorpass123',
            user_type='investor'
        )
        
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='creatorpass123',
            user_type='creator'
        )
        
        self.category = CampaignCategory.objects.create(
            name='Feature Film',
            description='Full-length feature films'
        )
        
        self.campaign = Campaign.objects.create(
            creator=self.creator,
            title='Test Film Campaign',
            description='Test description',
            short_description='Short description',
            category=self.category,
            funding_goal=Decimal('1000000.00'),
            funding_deadline=date.today() + timedelta(days=30),
            campaign_duration=30,
            min_investment=Decimal('1000.00'),
            max_investment=Decimal('100000.00'),
            equity_offered=Decimal('20.00'),
            status='active'
        )
        
        self.payment_method = PaymentMethod.objects.create(
            name='LankaQR',
            payment_type='lanka_qr',
            description='Sri Lanka QR code payment system',
            is_active=True,
            processing_fee_percentage=Decimal('2.50'),
            processing_fee_fixed=Decimal('10.00'),
            minimum_amount=Decimal('100.00'),
            maximum_amount=Decimal('100000.00')
        )
        
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')
    
    def test_payment_processing_workflow(self):
        """Test complete payment processing workflow"""
        # Step 1: Initiate payment
        payment_data = {
            'campaign': self.campaign.pk,
            'payment_method': self.payment_method.pk,
            'amount': '5000.00',
            'currency': 'LKR',
            'description': 'Investment in Test Film Campaign'
        }
        
        response = self.client.post(reverse('payments:initiate-payment'), payment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Step 2: Verify transaction created
        transaction = Transaction.objects.get(user=self.user, campaign=self.campaign)
        self.assertEqual(transaction.status, 'pending')
        self.assertEqual(transaction.amount, Decimal('5000.00'))
        
        # Step 3: Process payment (simulate gateway response)
        transaction.status = 'processing'
        transaction.save()
        
        # Step 4: Complete payment
        transaction.status = 'completed'
        transaction.processed_at = date.today()
        transaction.save()
        
        # Step 5: Update campaign funding
        self.campaign.current_funding += transaction.amount
        self.campaign.backer_count += 1
        self.campaign.save()
        
        # Verify campaign was updated
        self.campaign.refresh_from_db()
        self.assertEqual(self.campaign.current_funding, Decimal('5000.00'))
        self.assertEqual(self.campaign.backer_count, 1)
    
    def test_payment_failure_workflow(self):
        """Test payment failure workflow"""
        # Step 1: Initiate payment
        payment_data = {
            'campaign': self.campaign.pk,
            'payment_method': self.payment_method.pk,
            'amount': '5000.00',
            'currency': 'LKR',
            'description': 'Investment in Test Film Campaign'
        }
        
        response = self.client.post(reverse('payments:initiate-payment'), payment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Step 2: Simulate payment failure
        transaction = Transaction.objects.get(user=self.user, campaign=self.campaign)
        transaction.status = 'failed'
        transaction.failed_at = date.today()
        transaction.failure_reason = 'Insufficient funds'
        transaction.save()
        
        # Verify transaction status
        self.assertEqual(transaction.status, 'failed')
        self.assertIsNotNone(transaction.failed_at)
        self.assertEqual(transaction.failure_reason, 'Insufficient funds')
    
    def test_refund_processing_workflow(self):
        """Test refund processing workflow"""
        # Step 1: Create completed transaction
        transaction = Transaction.objects.create(
            user=self.user,
            campaign=self.campaign,
            payment_method=self.payment_method,
            amount=Decimal('5000.00'),
            currency='LKR',
            transaction_type='investment',
            status='completed',
            reference_id='TXN123456789',
            gateway_reference='GW123456789',
            description='Investment in Test Film Campaign'
        )
        
        # Step 2: Create refund
        refund = Refund.objects.create(
            transaction=transaction,
            amount=Decimal('5000.00'),
            reason='Campaign failed to meet funding goal',
            refund_type='full',
            status='pending',
            processed_by=self.user
        )
        
        # Step 3: Process refund
        refund.status = 'processing'
        refund.save()
        
        # Step 4: Complete refund
        refund.status = 'completed'
        refund.processed_at = date.today()
        refund.save()
        
        # Verify refund status
        self.assertEqual(refund.status, 'completed')
        self.assertIsNotNone(refund.processed_at)


class PaymentValidationTest(APITestCase):
    """Test cases for payment data validation"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='investor',
            email='investor@example.com',
            password='investorpass123',
            user_type='investor'
        )
        
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='creatorpass123',
            user_type='creator'
        )
        
        self.category = CampaignCategory.objects.create(
            name='Feature Film',
            description='Full-length feature films'
        )
        
        self.campaign = Campaign.objects.create(
            creator=self.creator,
            title='Test Film Campaign',
            description='Test description',
            short_description='Short description',
            category=self.category,
            funding_goal=Decimal('1000000.00'),
            funding_deadline=date.today() + timedelta(days=30),
            campaign_duration=30,
            min_investment=Decimal('1000.00'),
            max_investment=Decimal('100000.00'),
            equity_offered=Decimal('20.00'),
            status='active'
        )
        
        self.payment_method = PaymentMethod.objects.create(
            name='LankaQR',
            payment_type='lanka_qr',
            description='Sri Lanka QR code payment system',
            is_active=True,
            processing_fee_percentage=Decimal('2.50'),
            processing_fee_fixed=Decimal('10.00'),
            minimum_amount=Decimal('100.00'),
            maximum_amount=Decimal('100000.00')
        )
        
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')
    
    def test_invalid_amount_validation(self):
        """Test invalid amount validation"""
        # Test amount below minimum
        invalid_payment_data = {
            'campaign': self.campaign.pk,
            'payment_method': self.payment_method.pk,
            'amount': '50.00',  # Below minimum
            'currency': 'LKR',
            'description': 'Investment in Test Film Campaign'
        }
        
        response = self.client.post(reverse('payments:initiate-payment'), invalid_payment_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test amount above maximum
        invalid_payment_data['amount'] = '150000.00'  # Above maximum
        response = self.client.post(reverse('payments:initiate-payment'), invalid_payment_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_campaign_status_validation(self):
        """Test invalid campaign status validation"""
        # Set campaign to non-active status
        self.campaign.status = 'draft'
        self.campaign.save()
        
        payment_data = {
            'campaign': self.campaign.pk,
            'payment_method': self.payment_method.pk,
            'amount': '5000.00',
            'currency': 'LKR',
            'description': 'Investment in Test Film Campaign'
        }
        
        response = self.client.post(reverse('payments:initiate-payment'), payment_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_missing_required_fields_validation(self):
        """Test missing required fields validation"""
        incomplete_payment_data = {
            'campaign': self.campaign.pk,
            # Missing required fields
        }
        
        response = self.client.post(reverse('payments:initiate-payment'), incomplete_payment_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_duplicate_transaction_validation(self):
        """Test duplicate transaction validation"""
        # Create first transaction
        payment_data = {
            'campaign': self.campaign.pk,
            'payment_method': self.payment_method.pk,
            'amount': '5000.00',
            'currency': 'LKR',
            'description': 'Investment in Test Film Campaign'
        }
        
        response = self.client.post(reverse('payments:initiate-payment'), payment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Try to create duplicate transaction
        response = self.client.post(reverse('payments:initiate-payment'), payment_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PaymentIntegrationTest(TestCase):
    """Integration tests for payment functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='investor',
            email='investor@example.com',
            password='investorpass123',
            user_type='investor'
        )
        self.client.force_login(self.user)
        
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='creatorpass123',
            user_type='creator'
        )
        
        self.category = CampaignCategory.objects.create(
            name='Feature Film',
            description='Full-length feature films'
        )
        
        self.campaign = Campaign.objects.create(
            creator=self.creator,
            title='Test Film Campaign',
            description='Test description',
            short_description='Short description',
            category=self.category,
            funding_goal=Decimal('1000000.00'),
            funding_deadline=date.today() + timedelta(days=30),
            campaign_duration=30,
            min_investment=Decimal('1000.00'),
            max_investment=Decimal('100000.00'),
            equity_offered=Decimal('20.00'),
            status='active'
        )
        
        self.payment_method = PaymentMethod.objects.create(
            name='LankaQR',
            payment_type='lanka_qr',
            description='Sri Lanka QR code payment system',
            is_active=True,
            processing_fee_percentage=Decimal('2.50'),
            processing_fee_fixed=Decimal('10.00'),
            minimum_amount=Decimal('100.00'),
            maximum_amount=Decimal('100000.00')
        )
    
    def test_complete_payment_workflow(self):
        """Test complete payment workflow from initiation to completion"""
        # Step 1: Initiate payment
        payment_data = {
            'campaign': self.campaign.pk,
            'payment_method': self.payment_method.pk,
            'amount': '5000.00',
            'currency': 'LKR',
            'description': 'Investment in Test Film Campaign'
        }
        
        response = self.client.post(reverse('payments:initiate-payment'), payment_data)
        self.assertEqual(response.status_code, 201)
        
        # Step 2: Verify transaction created
        transaction = Transaction.objects.get(user=self.user, campaign=self.campaign)
        self.assertEqual(transaction.status, 'pending')
        
        # Step 3: Process payment
        transaction.status = 'processing'
        transaction.save()
        
        # Step 4: Complete payment
        transaction.status = 'completed'
        transaction.processed_at = date.today()
        transaction.save()
        
        # Step 5: Update campaign funding
        self.campaign.current_funding += transaction.amount
        self.campaign.backer_count += 1
        self.campaign.save()
        
        # Verify final state
        self.campaign.refresh_from_db()
        self.assertEqual(self.campaign.current_funding, Decimal('5000.00'))
        self.assertEqual(self.campaign.backer_count, 1)
        
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, 'completed')
    
    def test_payment_with_refund_workflow(self):
        """Test payment workflow with refund"""
        # Step 1: Complete payment
        transaction = Transaction.objects.create(
            user=self.user,
            campaign=self.campaign,
            payment_method=self.payment_method,
            amount=Decimal('5000.00'),
            currency='LKR',
            transaction_type='investment',
            status='completed',
            reference_id='TXN123456789',
            gateway_reference='GW123456789',
            description='Investment in Test Film Campaign'
        )
        
        # Step 2: Create refund
        refund = Refund.objects.create(
            transaction=transaction,
            amount=Decimal('5000.00'),
            reason='Campaign failed to meet funding goal',
            refund_type='full',
            status='pending',
            processed_by=self.user
        )
        
        # Step 3: Process refund
        refund.status = 'processing'
        refund.save()
        
        # Step 4: Complete refund
        refund.status = 'completed'
        refund.processed_at = date.today()
        refund.save()
        
        # Verify refund completion
        self.assertEqual(refund.status, 'completed')
        self.assertIsNotNone(refund.processed_at)
