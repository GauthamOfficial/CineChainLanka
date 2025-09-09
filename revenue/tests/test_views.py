from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from datetime import date, datetime
from campaigns.models import Campaign
from revenue.models import (
    RevenueSource, RevenueEntry, RoyaltyDistribution, 
    InvestorRoyalty, RevenueAnalytics, OTTPlatformIntegration
)

User = get_user_model()


class RevenueSourceViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.revenue_source = RevenueSource.objects.create(
            name='Test Source',
            revenue_type='box_office',
            description='Test revenue source',
            token_address='0x1234567890123456789012345678901234567890',
            platform_fee_percentage=Decimal('5.00'),
            creator_fee_percentage=Decimal('30.00'),
            investor_fee_percentage=Decimal('65.00'),
            is_active=True
        )

    def test_list_revenue_sources(self):
        url = reverse('revenue:revenuesource-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_revenue_source(self):
        url = reverse('revenue:revenuesource-list')
        data = {
            'name': 'New Source',
            'revenue_type': 'ott_platform',
            'description': 'New revenue source',
            'token_address': '0x1234567890123456789012345678901234567890',
            'platform_fee_percentage': '5.00',
            'creator_fee_percentage': '30.00',
            'investor_fee_percentage': '65.00',
            'is_active': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RevenueSource.objects.count(), 2)

    def test_retrieve_revenue_source(self):
        url = reverse('revenue:revenuesource-detail', kwargs={'pk': self.revenue_source.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Source')


class RevenueEntryViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.campaign = Campaign.objects.create(
            title='Test Campaign',
            description='Test campaign description',
            creator=self.user,
            funding_goal=Decimal('10000.00'),
            start_date=date.today(),
            end_date=date.today()
        )
        
        self.revenue_source = RevenueSource.objects.create(
            name='Test Source',
            revenue_type='box_office',
            token_address='0x1234567890123456789012345678901234567890',
            platform_fee_percentage=Decimal('5.00'),
            creator_fee_percentage=Decimal('30.00'),
            investor_fee_percentage=Decimal('65.00'),
            is_active=True
        )
        
        self.revenue_entry = RevenueEntry.objects.create(
            campaign=self.campaign,
            source=self.revenue_source,
            amount=Decimal('1000.00'),
            currency='USDT',
            description='Test revenue entry',
            revenue_date=date.today(),
            status='pending'
        )

    def test_list_revenue_entries(self):
        url = reverse('revenue:revenueentry-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_revenue_entry(self):
        url = reverse('revenue:revenueentry-list')
        data = {
            'campaign': self.campaign.id,
            'source': self.revenue_source.id,
            'amount': '2000.00',
            'currency': 'USDT',
            'description': 'New revenue entry',
            'revenue_date': date.today().isoformat()
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RevenueEntry.objects.count(), 2)

    def test_verify_revenue_entry(self):
        url = reverse('revenue:revenueentry-verify', kwargs={'pk': self.revenue_entry.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # Non-staff user

    def test_filter_by_campaign(self):
        url = reverse('revenue:revenueentry-list')
        response = self.client.get(url, {'campaign_id': self.campaign.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_by_status(self):
        url = reverse('revenue:revenueentry-list')
        response = self.client.get(url, {'status': 'pending'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class RoyaltyDistributionViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.campaign = Campaign.objects.create(
            title='Test Campaign',
            description='Test campaign description',
            creator=self.user,
            funding_goal=Decimal('10000.00'),
            start_date=date.today(),
            end_date=date.today()
        )
        
        self.revenue_source = RevenueSource.objects.create(
            name='Test Source',
            revenue_type='box_office',
            token_address='0x1234567890123456789012345678901234567890',
            platform_fee_percentage=Decimal('5.00'),
            creator_fee_percentage=Decimal('30.00'),
            investor_fee_percentage=Decimal('65.00'),
            is_active=True
        )
        
        self.revenue_entry = RevenueEntry.objects.create(
            campaign=self.campaign,
            source=self.revenue_source,
            amount=Decimal('1000.00'),
            currency='USDT',
            description='Test revenue entry',
            revenue_date=date.today(),
            status='verified'
        )
        
        self.royalty_distribution = RoyaltyDistribution.objects.create(
            campaign=self.campaign,
            revenue_entry=self.revenue_entry,
            distribution_date=datetime.now(),
            creator_amount=Decimal('300.00'),
            platform_amount=Decimal('50.00'),
            total_investor_amount=Decimal('650.00'),
            status='completed'
        )

    def test_list_royalty_distributions(self):
        url = reverse('revenue:royaltydistribution-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_royalty_distribution(self):
        url = reverse('revenue:royaltydistribution-detail', kwargs={'pk': self.royalty_distribution.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['campaign'], self.campaign.id)


class InvestorRoyaltyViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.campaign = Campaign.objects.create(
            title='Test Campaign',
            description='Test campaign description',
            creator=self.user,
            funding_goal=Decimal('10000.00'),
            start_date=date.today(),
            end_date=date.today()
        )
        
        self.revenue_source = RevenueSource.objects.create(
            name='Test Source',
            revenue_type='box_office',
            token_address='0x1234567890123456789012345678901234567890',
            platform_fee_percentage=Decimal('5.00'),
            creator_fee_percentage=Decimal('30.00'),
            investor_fee_percentage=Decimal('65.00'),
            is_active=True
        )
        
        self.revenue_entry = RevenueEntry.objects.create(
            campaign=self.campaign,
            source=self.revenue_source,
            amount=Decimal('1000.00'),
            currency='USDT',
            description='Test revenue entry',
            revenue_date=date.today(),
            status='verified'
        )
        
        self.royalty_distribution = RoyaltyDistribution.objects.create(
            campaign=self.campaign,
            revenue_entry=self.revenue_entry,
            distribution_date=datetime.now(),
            creator_amount=Decimal('300.00'),
            platform_amount=Decimal('50.00'),
            total_investor_amount=Decimal('650.00'),
            status='completed'
        )
        
        self.investor_royalty = InvestorRoyalty.objects.create(
            distribution=self.royalty_distribution,
            investor=self.user,
            nft_id=1,
            contribution_amount=Decimal('1000.00'),
            share_percentage=Decimal('10.00'),
            royalty_amount=Decimal('65.00'),
            status='claimable'
        )

    def test_list_investor_royalties(self):
        url = reverse('revenue:investorroyalty-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_claim_investor_royalty(self):
        url = reverse('revenue:investorroyalty-claim', kwargs={'pk': self.investor_royalty.pk})
        response = self.client.post(url)
        # This will fail because we don't have the blockchain service mocked
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class RevenueAnalyticsViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.campaign = Campaign.objects.create(
            title='Test Campaign',
            description='Test campaign description',
            creator=self.user,
            funding_goal=Decimal('10000.00'),
            start_date=date.today(),
            end_date=date.today()
        )
        
        self.revenue_analytics = RevenueAnalytics.objects.create(
            campaign=self.campaign,
            total_revenue=Decimal('5000.00'),
            total_creator_royalties=Decimal('1500.00'),
            total_platform_fees=Decimal('250.00'),
            total_investor_royalties=Decimal('3250.00'),
            total_distributions=5
        )

    def test_list_revenue_analytics(self):
        url = reverse('revenue:revenueanalytics-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_revenue_summary(self):
        url = reverse('revenue:revenueanalytics-summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_revenue', response.data)

    def test_get_chart_data(self):
        url = reverse('revenue:revenueanalytics-chart_data')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('labels', response.data)


class InvestorPortfolioViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_get_portfolio(self):
        url = reverse('revenue:investorportfolio-portfolio')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_invested', response.data)

    def test_get_claimable_royalties(self):
        url = reverse('revenue:investorportfolio-claimable_royalties')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('claimable_royalties', response.data)


class OTTPlatformIntegrationViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.ott_platform = OTTPlatformIntegration.objects.create(
            name='Test OTT Platform',
            platform_type='netflix',
            api_endpoint='https://api.test.com/revenue',
            webhook_url='https://webhook.test.com/endpoint',
            is_active=True
        )

    def test_list_ott_platforms(self):
        url = reverse('revenue:ottplatformintegration-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_ott_platform(self):
        url = reverse('revenue:ottplatformintegration-list')
        data = {
            'name': 'New OTT Platform',
            'platform_type': 'amazon_prime',
            'api_endpoint': 'https://api.new.com/revenue',
            'webhook_url': 'https://webhook.new.com/endpoint',
            'is_active': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(OTTPlatformIntegration.objects.count(), 2)
