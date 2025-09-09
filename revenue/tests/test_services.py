from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, datetime
from unittest.mock import patch, MagicMock
from campaigns.models import Campaign
from revenue.models import (
    RevenueSource, RevenueEntry, RoyaltyDistribution, 
    InvestorRoyalty, RevenueAnalytics
)
from revenue.services import RevenueService, RoyaltyDistributionService, AnalyticsService
from revenue.ott_integration import OTTIntegrationService, BoxOfficeIntegrationService

User = get_user_model()


class RevenueServiceTest(TestCase):
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
        
        self.revenue_service = RevenueService()

    def test_create_revenue_entry(self):
        revenue_entry = self.revenue_service.create_revenue_entry(
            campaign_id=self.campaign.id,
            source_id=self.revenue_source.id,
            amount=Decimal('1000.00'),
            currency='USDT',
            description='Test revenue entry',
            revenue_date=datetime.now()
        )
        
        self.assertEqual(revenue_entry.campaign, self.campaign)
        self.assertEqual(revenue_entry.source, self.revenue_source)
        self.assertEqual(revenue_entry.amount, Decimal('1000.00'))
        self.assertEqual(revenue_entry.currency, 'USDT')
        self.assertEqual(revenue_entry.status, 'pending')

    def test_verify_revenue_entry(self):
        revenue_entry = RevenueEntry.objects.create(
            campaign=self.campaign,
            source=self.revenue_source,
            amount=Decimal('1000.00'),
            currency='USDT',
            description='Test revenue entry',
            revenue_date=date.today(),
            status='pending'
        )
        
        success = self.revenue_service.verify_revenue_entry(
            revenue_entry.id, 
            self.user.id
        )
        
        self.assertTrue(success)
        revenue_entry.refresh_from_db()
        self.assertEqual(revenue_entry.status, 'verified')
        self.assertEqual(revenue_entry.verified_by, self.user)

    def test_get_campaign_revenue_summary(self):
        # Create some revenue entries
        RevenueEntry.objects.create(
            campaign=self.campaign,
            source=self.revenue_source,
            amount=Decimal('1000.00'),
            currency='USDT',
            description='Test revenue entry 1',
            revenue_date=date.today(),
            status='verified'
        )
        
        RevenueEntry.objects.create(
            campaign=self.campaign,
            source=self.revenue_source,
            amount=Decimal('500.00'),
            currency='USDT',
            description='Test revenue entry 2',
            revenue_date=date.today(),
            status='processed'
        )
        
        summary = self.revenue_service.get_campaign_revenue_summary(self.campaign.id)
        
        self.assertEqual(summary['campaign_id'], self.campaign.id)
        self.assertEqual(summary['total_revenue'], Decimal('1500.00'))
        self.assertEqual(len(summary['recent_entries']), 2)


class RoyaltyDistributionServiceTest(TestCase):
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
        
        self.royalty_service = RoyaltyDistributionService()

    @patch('revenue.services.RoyaltyDistributionService._get_royalty_contract')
    def test_process_royalty_distribution(self, mock_contract):
        mock_contract.return_value = None  # Mock contract not available
        
        distribution = self.royalty_service.process_royalty_distribution(self.revenue_entry)
        
        self.assertEqual(distribution.campaign, self.campaign)
        self.assertEqual(distribution.revenue_entry, self.revenue_entry)
        self.assertEqual(distribution.creator_amount, Decimal('300.00'))  # 30% of 1000
        self.assertEqual(distribution.platform_amount, Decimal('50.00'))  # 5% of 1000
        self.assertEqual(distribution.total_investor_amount, Decimal('650.00'))  # 65% of 1000
        self.assertEqual(distribution.status, 'completed')

    def test_claim_investor_royalty(self):
        # Create a royalty distribution
        distribution = RoyaltyDistribution.objects.create(
            campaign=self.campaign,
            revenue_entry=self.revenue_entry,
            distribution_date=datetime.now(),
            creator_amount=Decimal('300.00'),
            platform_amount=Decimal('50.00'),
            total_investor_amount=Decimal('650.00'),
            status='completed'
        )
        
        # Create an investor royalty
        investor_royalty = InvestorRoyalty.objects.create(
            distribution=distribution,
            investor=self.user,
            nft_id=1,
            contribution_amount=Decimal('1000.00'),
            share_percentage=Decimal('10.00'),
            royalty_amount=Decimal('65.00'),
            status='claimable'
        )
        
        with patch('revenue.services.ContractService') as mock_contract_service:
            mock_contract_service.return_value.send_function.return_value = '0x1234567890abcdef'
            
            tx_hash = self.royalty_service.claim_investor_royalty(investor_royalty)
            
            self.assertEqual(tx_hash, '0x1234567890abcdef')


class AnalyticsServiceTest(TestCase):
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
        
        self.analytics_service = AnalyticsService()

    def test_get_revenue_summary(self):
        # Create some revenue entries
        RevenueEntry.objects.create(
            campaign=self.campaign,
            source=self.revenue_source,
            amount=Decimal('1000.00'),
            currency='USDT',
            description='Test revenue entry',
            revenue_date=date.today(),
            status='processed'
        )
        
        # Create a royalty distribution
        revenue_entry = RevenueEntry.objects.create(
            campaign=self.campaign,
            source=self.revenue_source,
            amount=Decimal('1000.00'),
            currency='USDT',
            description='Test revenue entry',
            revenue_date=date.today(),
            status='processed'
        )
        
        RoyaltyDistribution.objects.create(
            campaign=self.campaign,
            revenue_entry=revenue_entry,
            distribution_date=datetime.now(),
            creator_amount=Decimal('300.00'),
            platform_amount=Decimal('50.00'),
            total_investor_amount=Decimal('650.00'),
            status='completed'
        )
        
        summary = self.analytics_service.get_revenue_summary(self.user)
        
        self.assertEqual(summary['total_revenue'], Decimal('2000.00'))
        self.assertEqual(summary['total_creator_royalties'], Decimal('300.00'))
        self.assertEqual(summary['total_platform_fees'], Decimal('50.00'))
        self.assertEqual(summary['total_investor_royalties'], Decimal('650.00'))

    def test_get_investor_portfolio(self):
        # Create a royalty distribution
        revenue_entry = RevenueEntry.objects.create(
            campaign=self.campaign,
            source=self.revenue_source,
            amount=Decimal('1000.00'),
            currency='USDT',
            description='Test revenue entry',
            revenue_date=date.today(),
            status='processed'
        )
        
        distribution = RoyaltyDistribution.objects.create(
            campaign=self.campaign,
            revenue_entry=revenue_entry,
            distribution_date=datetime.now(),
            creator_amount=Decimal('300.00'),
            platform_amount=Decimal('50.00'),
            total_investor_amount=Decimal('650.00'),
            status='completed'
        )
        
        # Create investor royalties
        InvestorRoyalty.objects.create(
            distribution=distribution,
            investor=self.user,
            nft_id=1,
            contribution_amount=Decimal('1000.00'),
            share_percentage=Decimal('10.00'),
            royalty_amount=Decimal('65.00'),
            status='claimable'
        )
        
        portfolio = self.analytics_service.get_investor_portfolio(self.user)
        
        self.assertEqual(portfolio['total_invested'], Decimal('1000.00'))
        self.assertEqual(portfolio['total_royalties_earned'], Decimal('65.00'))
        self.assertEqual(portfolio['total_royalties_claimable'], Decimal('65.00'))
        self.assertEqual(portfolio['roi_percentage'], Decimal('6.50'))


class OTTIntegrationServiceTest(TestCase):
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
        
        self.ott_service = OTTIntegrationService()

    def test_process_webhook(self):
        payload = {
            'campaign_id': self.campaign.id,
            'revenue_data': {
                'amount': 1000.00,
                'currency': 'USDT',
                'period': 'January 2024',
                'date': '2024-01-15'
            }
        }
        
        success = self.ott_service.process_webhook(self.ott_platform.id, payload)
        
        self.assertTrue(success)
        
        # Check if revenue entry was created
        revenue_entries = RevenueEntry.objects.filter(campaign=self.campaign)
        self.assertEqual(revenue_entries.count(), 1)
        
        revenue_entry = revenue_entries.first()
        self.assertEqual(revenue_entry.amount, Decimal('1000.00'))
        self.assertEqual(revenue_entry.currency, 'USDT')
        self.assertEqual(revenue_entry.status, 'verified')


class BoxOfficeIntegrationServiceTest(TestCase):
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
        
        self.box_office_service = BoxOfficeIntegrationService()

    def test_record_box_office_revenue(self):
        revenue_entry = self.box_office_service.record_box_office_revenue(
            campaign_id=self.campaign.id,
            amount=Decimal('5000.00'),
            currency='USDT',
            description='Box office revenue for opening weekend',
            revenue_date=datetime.now()
        )
        
        self.assertEqual(revenue_entry.campaign, self.campaign)
        self.assertEqual(revenue_entry.amount, Decimal('5000.00'))
        self.assertEqual(revenue_entry.currency, 'USDT')
        self.assertEqual(revenue_entry.status, 'pending')

    def test_get_box_office_summary(self):
        # Create some box office revenue entries
        RevenueEntry.objects.create(
            campaign=self.campaign,
            source=self.box_office_service.box_office_source,
            amount=Decimal('1000.00'),
            currency='USDT',
            description='Box office revenue day 1',
            revenue_date=date.today(),
            status='verified'
        )
        
        RevenueEntry.objects.create(
            campaign=self.campaign,
            source=self.box_office_service.box_office_source,
            amount=Decimal('500.00'),
            currency='USDT',
            description='Box office revenue day 2',
            revenue_date=date.today(),
            status='processed'
        )
        
        summary = self.box_office_service.get_box_office_summary(self.campaign.id)
        
        self.assertEqual(summary['campaign_id'], self.campaign.id)
        self.assertEqual(summary['total_revenue'], Decimal('1500.00'))
        self.assertEqual(summary['entry_count'], 2)
