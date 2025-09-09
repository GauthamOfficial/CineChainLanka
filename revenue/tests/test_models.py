from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, datetime
from campaigns.models import Campaign
from revenue.models import (
    RevenueSource, RevenueEntry, RoyaltyDistribution, 
    InvestorRoyalty, RevenueAnalytics, OTTPlatformIntegration, RevenueWebhook
)

User = get_user_model()


class RevenueSourceModelTest(TestCase):
    def setUp(self):
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

    def test_revenue_source_creation(self):
        self.assertEqual(self.revenue_source.name, 'Test Source')
        self.assertEqual(self.revenue_source.revenue_type, 'box_office')
        self.assertEqual(self.revenue_source.platform_fee_percentage, Decimal('5.00'))
        self.assertTrue(self.revenue_source.is_active)

    def test_revenue_source_str(self):
        expected = 'Test Source (Box Office)'
        self.assertEqual(str(self.revenue_source), expected)


class RevenueEntryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
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

    def test_revenue_entry_creation(self):
        self.assertEqual(self.revenue_entry.campaign, self.campaign)
        self.assertEqual(self.revenue_entry.source, self.revenue_source)
        self.assertEqual(self.revenue_entry.amount, Decimal('1000.00'))
        self.assertEqual(self.revenue_entry.currency, 'USDT')
        self.assertEqual(self.revenue_entry.status, 'pending')

    def test_revenue_entry_str(self):
        expected = 'Test Campaign - 1000.00 USDT (Pending)'
        self.assertEqual(str(self.revenue_entry), expected)


class RoyaltyDistributionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
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

    def test_royalty_distribution_creation(self):
        self.assertEqual(self.royalty_distribution.campaign, self.campaign)
        self.assertEqual(self.royalty_distribution.revenue_entry, self.revenue_entry)
        self.assertEqual(self.royalty_distribution.creator_amount, Decimal('300.00'))
        self.assertEqual(self.royalty_distribution.platform_amount, Decimal('50.00'))
        self.assertEqual(self.royalty_distribution.total_investor_amount, Decimal('650.00'))
        self.assertEqual(self.royalty_distribution.status, 'completed')

    def test_royalty_distribution_str(self):
        expected = f'Distribution for Test Campaign - {self.royalty_distribution.distribution_date}'
        self.assertEqual(str(self.royalty_distribution), expected)


class InvestorRoyaltyModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
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

    def test_investor_royalty_creation(self):
        self.assertEqual(self.investor_royalty.distribution, self.royalty_distribution)
        self.assertEqual(self.investor_royalty.investor, self.user)
        self.assertEqual(self.investor_royalty.nft_id, 1)
        self.assertEqual(self.investor_royalty.contribution_amount, Decimal('1000.00'))
        self.assertEqual(self.investor_royalty.share_percentage, Decimal('10.00'))
        self.assertEqual(self.investor_royalty.royalty_amount, Decimal('65.00'))
        self.assertEqual(self.investor_royalty.status, 'claimable')

    def test_investor_royalty_str(self):
        expected = 'testuser - 65.00 USDT'
        self.assertEqual(str(self.investor_royalty), expected)


class RevenueAnalyticsModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
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

    def test_revenue_analytics_creation(self):
        self.assertEqual(self.revenue_analytics.campaign, self.campaign)
        self.assertEqual(self.revenue_analytics.total_revenue, Decimal('5000.00'))
        self.assertEqual(self.revenue_analytics.total_creator_royalties, Decimal('1500.00'))
        self.assertEqual(self.revenue_analytics.total_platform_fees, Decimal('250.00'))
        self.assertEqual(self.revenue_analytics.total_investor_royalties, Decimal('3250.00'))
        self.assertEqual(self.revenue_analytics.total_distributions, 5)

    def test_revenue_analytics_str(self):
        expected = 'Analytics for Test Campaign'
        self.assertEqual(str(self.revenue_analytics), expected)


class OTTPlatformIntegrationModelTest(TestCase):
    def setUp(self):
        self.ott_platform = OTTPlatformIntegration.objects.create(
            name='Test OTT Platform',
            platform_type='netflix',
            api_endpoint='https://api.test.com/revenue',
            webhook_url='https://webhook.test.com/endpoint',
            is_active=True
        )

    def test_ott_platform_creation(self):
        self.assertEqual(self.ott_platform.name, 'Test OTT Platform')
        self.assertEqual(self.ott_platform.platform_type, 'netflix')
        self.assertEqual(self.ott_platform.api_endpoint, 'https://api.test.com/revenue')
        self.assertEqual(self.ott_platform.webhook_url, 'https://webhook.test.com/endpoint')
        self.assertTrue(self.ott_platform.is_active)

    def test_ott_platform_str(self):
        expected = 'Test OTT Platform (Netflix)'
        self.assertEqual(str(self.ott_platform), expected)


class RevenueWebhookModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.campaign = Campaign.objects.create(
            title='Test Campaign',
            description='Test campaign description',
            creator=self.user,
            funding_goal=Decimal('10000.00'),
            start_date=date.today(),
            end_date=date.today()
        )
        
        self.ott_platform = OTTPlatformIntegration.objects.create(
            name='Test OTT Platform',
            platform_type='netflix',
            api_endpoint='https://api.test.com/revenue',
            webhook_url='https://webhook.test.com/endpoint',
            is_active=True
        )
        
        self.revenue_webhook = RevenueWebhook.objects.create(
            platform=self.ott_platform,
            campaign=self.campaign,
            payload={'test': 'data'},
            status='pending'
        )

    def test_revenue_webhook_creation(self):
        self.assertEqual(self.revenue_webhook.platform, self.ott_platform)
        self.assertEqual(self.revenue_webhook.campaign, self.campaign)
        self.assertEqual(self.revenue_webhook.payload, {'test': 'data'})
        self.assertEqual(self.revenue_webhook.status, 'pending')

    def test_revenue_webhook_str(self):
        expected = 'Webhook for Test Campaign - Pending'
        self.assertEqual(str(self.revenue_webhook), expected)
