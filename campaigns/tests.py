from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Campaign, CampaignCategory, CampaignReward, CampaignUpdate, CampaignComment
from users.models import User
import json
import tempfile
import os
from datetime import date, timedelta
from decimal import Decimal

User = get_user_model()


class CampaignCategoryModelTest(TestCase):
    """Test cases for CampaignCategory model"""
    
    def setUp(self):
        self.category_data = {
            'name': 'Feature Film',
            'description': 'Full-length feature films',
            'icon': 'film-icon',
            'is_active': True
        }
    
    def test_create_campaign_category(self):
        """Test creating a campaign category"""
        category = CampaignCategory.objects.create(**self.category_data)
        self.assertEqual(category.name, 'Feature Film')
        self.assertEqual(category.description, 'Full-length feature films')
        self.assertEqual(category.icon, 'film-icon')
        self.assertTrue(category.is_active)
    
    def test_campaign_category_str_representation(self):
        """Test campaign category string representation"""
        category = CampaignCategory.objects.create(**self.category_data)
        self.assertEqual(str(category), 'Feature Film')
    
    def test_campaign_category_ordering(self):
        """Test campaign category ordering"""
        category1 = CampaignCategory.objects.create(name='Documentary', description='Documentary films')
        category2 = CampaignCategory.objects.create(name='Short Film', description='Short films')
        
        categories = CampaignCategory.objects.all()
        self.assertEqual(categories[0].name, 'Documentary')
        self.assertEqual(categories[1].name, 'Short Film')
    
    def test_campaign_category_active_filter(self):
        """Test filtering active campaign categories"""
        CampaignCategory.objects.create(**self.category_data)
        CampaignCategory.objects.create(
            name='Inactive Category',
            description='Inactive category',
            is_active=False
        )
        
        active_categories = CampaignCategory.objects.filter(is_active=True)
        self.assertEqual(active_categories.count(), 1)
        self.assertEqual(active_categories.first().name, 'Feature Film')


class CampaignModelTest(TestCase):
    """Test cases for Campaign model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='creatorpass123',
            user_type='creator'
        )
        
        self.category = CampaignCategory.objects.create(
            name='Feature Film',
            description='Full-length feature films'
        )
        
        self.campaign_data = {
            'creator': self.user,
            'title': 'Test Film Campaign',
            'subtitle': 'An amazing test film',
            'description': 'This is a detailed description of the test film campaign',
            'short_description': 'A short description of the test film',
            'category': self.category,
            'funding_goal': Decimal('1000000.00'),
            'funding_deadline': date.today() + timedelta(days=30),
            'campaign_duration': 30,
            'min_investment': Decimal('1000.00'),
            'max_investment': Decimal('100000.00'),
            'equity_offered': Decimal('20.00'),
            'project_type': 'feature_film',
            'genre': 'drama',
            'language': 'Sinhala',
            'target_audience': 'General audience',
            'production_company': 'Test Productions',
            'director': 'Test Director',
            'producer': 'Test Producer',
            'cast': 'Test Cast',
            'crew': 'Test Crew',
            'synopsis': 'A compelling story about...',
            'target_market': 'Sri Lanka',
            'distribution_plan': 'Theatrical and digital distribution',
            'marketing_strategy': 'Social media and traditional marketing',
            'risk_factors': 'Standard production risks',
            'expected_roi': Decimal('25.00'),
            'projected_completion': date.today() + timedelta(days=365),
            'is_featured': False,
            'is_verified': False
        }
    
    def test_create_campaign(self):
        """Test creating a campaign"""
        campaign = Campaign.objects.create(**self.campaign_data)
        self.assertEqual(campaign.title, 'Test Film Campaign')
        self.assertEqual(campaign.creator, self.user)
        self.assertEqual(campaign.category, self.category)
        self.assertEqual(campaign.status, 'draft')
        self.assertEqual(campaign.funding_goal, Decimal('1000000.00'))
    
    def test_campaign_str_representation(self):
        """Test campaign string representation"""
        campaign = Campaign.objects.create(**self.campaign_data)
        expected = f"{campaign.title} by {campaign.creator.username}"
        self.assertEqual(str(campaign), expected)
    
    def test_campaign_status_choices(self):
        """Test campaign status choices"""
        campaign = Campaign.objects.create(**self.campaign_data)
        choices = [choice[0] for choice in Campaign.STATUS_CHOICES]
        self.assertIn(campaign.status, choices)
    
    def test_campaign_defaults(self):
        """Test campaign default values"""
        campaign = Campaign.objects.create(**self.campaign_data)
        self.assertEqual(campaign.status, 'draft')
        self.assertEqual(campaign.current_funding, Decimal('0.00'))
        self.assertEqual(campaign.backer_count, 0)
        self.assertIsNotNone(campaign.created_at)
        self.assertIsNotNone(campaign.updated_at)
    
    def test_campaign_funding_progress(self):
        """Test campaign funding progress calculation"""
        campaign = Campaign.objects.create(**self.campaign_data)
        campaign.current_funding = Decimal('500000.00')
        campaign.save()
        
        progress = campaign.funding_progress
        expected_progress = (500000.00 / 1000000.00) * 100
        self.assertEqual(progress, expected_progress)
    
    def test_campaign_days_remaining(self):
        """Test campaign days remaining calculation"""
        campaign = Campaign.objects.create(**self.campaign_data)
        days_remaining = campaign.days_remaining
        self.assertGreater(days_remaining, 0)
        self.assertLessEqual(days_remaining, 30)
    
    def test_campaign_is_funded(self):
        """Test campaign funding status"""
        campaign = Campaign.objects.create(**self.campaign_data)
        self.assertFalse(campaign.is_funded)
        
        campaign.current_funding = campaign.funding_goal
        campaign.save()
        self.assertTrue(campaign.is_funded)
    
    def test_campaign_is_expired(self):
        """Test campaign expiration status"""
        campaign = Campaign.objects.create(**self.campaign_data)
        self.assertFalse(campaign.is_expired)
        
        # Set deadline to past date
        campaign.funding_deadline = date.today() - timedelta(days=1)
        campaign.save()
        self.assertTrue(campaign.is_expired)


class CampaignRewardModelTest(TestCase):
    """Test cases for CampaignReward model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
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
            creator=self.user,
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
        
        self.reward_data = {
            'campaign': self.campaign,
            'name': 'Early Bird Reward',
            'description': 'Special reward for early backers',
            'minimum_amount': Decimal('5000.00'),
            'reward_type': 'equity',
            'reward_value': Decimal('0.5'),
            'quantity_available': 100,
            'delivery_date': date.today() + timedelta(days=60),
            'is_active': True
        }
    
    def test_create_campaign_reward(self):
        """Test creating a campaign reward"""
        reward = CampaignReward.objects.create(**self.reward_data)
        self.assertEqual(reward.name, 'Early Bird Reward')
        self.assertEqual(reward.campaign, self.campaign)
        self.assertEqual(reward.minimum_amount, Decimal('5000.00'))
        self.assertEqual(reward.reward_type, 'equity')
    
    def test_campaign_reward_str_representation(self):
        """Test campaign reward string representation"""
        reward = CampaignReward.objects.create(**self.reward_data)
        expected = f"{reward.name} - {reward.campaign.title}"
        self.assertEqual(str(reward), expected)
    
    def test_campaign_reward_choices(self):
        """Test campaign reward type choices"""
        reward = CampaignReward.objects.create(**self.reward_data)
        choices = [choice[0] for choice in CampaignReward.REWARD_TYPE_CHOICES]
        self.assertIn(reward.reward_type, choices)
    
    def test_campaign_reward_quantity_management(self):
        """Test campaign reward quantity management"""
        reward = CampaignReward.objects.create(**self.reward_data)
        self.assertEqual(reward.quantity_remaining, 100)
        
        # Simulate some rewards claimed
        reward.quantity_claimed = 25
        reward.save()
        self.assertEqual(reward.quantity_remaining, 75)


class CampaignViewsTest(APITestCase):
    """Test cases for Campaign views"""
    
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
        
        self.category = CampaignCategory.objects.create(
            name='Feature Film',
            description='Full-length feature films'
        )
        
        self.campaign_data = {
            'title': 'Test Film Campaign',
            'subtitle': 'An amazing test film',
            'description': 'This is a detailed description of the test film campaign',
            'short_description': 'A short description of the test film',
            'category': self.category.pk,
            'funding_goal': '1000000.00',
            'funding_deadline': (date.today() + timedelta(days=30)).isoformat(),
            'campaign_duration': 30,
            'min_investment': '1000.00',
            'max_investment': '100000.00',
            'equity_offered': '20.00',
            'project_type': 'feature_film',
            'genre': 'drama',
            'language': 'Sinhala',
            'target_audience': 'General audience',
            'production_company': 'Test Productions',
            'director': 'Test Director',
            'producer': 'Test Producer',
            'cast': 'Test Cast',
            'crew': 'Test Crew',
            'synopsis': 'A compelling story about...',
            'target_market': 'Sri Lanka',
            'distribution_plan': 'Theatrical and digital distribution',
            'marketing_strategy': 'Social media and traditional marketing',
            'risk_factors': 'Standard production risks',
            'expected_roi': '25.00',
            'projected_completion': (date.today() + timedelta(days=365)).isoformat()
        }
        
        self.creator_token = RefreshToken.for_user(self.creator)
        self.investor_token = RefreshToken.for_user(self.investor)
    
    def test_create_campaign(self):
        """Test creating a campaign via API"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.creator_token.access_token}')
        
        response = self.client.post(reverse('campaigns:campaign-create'), self.campaign_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Campaign.objects.filter(title='Test Film Campaign').exists())
    
    def test_campaign_list(self):
        """Test campaign list endpoint"""
        # Create a campaign first
        campaign = Campaign.objects.create(
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
        
        response = self.client.get(reverse('campaigns:campaign-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_campaign_detail(self):
        """Test campaign detail endpoint"""
        # Create a campaign first
        campaign = Campaign.objects.create(
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
        
        response = self.client.get(reverse('campaigns:campaign-detail', kwargs={'pk': campaign.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Film Campaign')
    
    def test_campaign_update(self):
        """Test campaign update endpoint"""
        # Create a campaign first
        campaign = Campaign.objects.create(
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
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.creator_token.access_token}')
        
        update_data = {
            'title': 'Updated Film Campaign',
            'description': 'Updated description'
        }
        
        response = self.client.patch(
            reverse('campaigns:campaign-detail', kwargs={'pk': campaign.pk}),
            update_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify data was updated
        campaign.refresh_from_db()
        self.assertEqual(campaign.title, 'Updated Film Campaign')
        self.assertEqual(campaign.description, 'Updated description')
    
    def test_campaign_deletion(self):
        """Test campaign deletion endpoint"""
        # Create a campaign first
        campaign = Campaign.objects.create(
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
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.creator_token.access_token}')
        
        response = self.client.delete(
            reverse('campaigns:campaign-detail', kwargs={'pk': campaign.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify campaign was deleted
        self.assertFalse(Campaign.objects.filter(pk=campaign.pk).exists())
    
    def test_campaign_submission(self):
        """Test campaign submission workflow"""
        # Create a campaign first
        campaign = Campaign.objects.create(
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
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.creator_token.access_token}')
        
        # Submit campaign for review
        submit_data = {'action': 'submit'}
        response = self.client.post(
            reverse('campaigns:campaign-submit', kwargs={'pk': campaign.pk}),
            submit_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify status changed to pending_review
        campaign.refresh_from_db()
        self.assertEqual(campaign.status, 'pending_review')
    
    def test_campaign_activation(self):
        """Test campaign activation workflow"""
        # Create a campaign first
        campaign = Campaign.objects.create(
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
            status='approved'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.creator_token.access_token}')
        
        # Activate campaign
        activate_data = {'action': 'activate'}
        response = self.client.post(
            reverse('campaigns:campaign-activate', kwargs={'pk': campaign.pk}),
            activate_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify status changed to active
        campaign.refresh_from_db()
        self.assertEqual(campaign.status, 'active')


class CampaignSearchAndFilterTest(APITestCase):
    """Test cases for campaign search and filtering"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='creatorpass123',
            user_type='creator'
        )
        
        self.category1 = CampaignCategory.objects.create(
            name='Feature Film',
            description='Full-length feature films'
        )
        
        self.category2 = CampaignCategory.objects.create(
            name='Documentary',
            description='Documentary films'
        )
        
        # Create multiple campaigns for testing
        self.campaign1 = Campaign.objects.create(
            creator=self.creator,
            title='Action Film Campaign',
            description='An action-packed film',
            short_description='Action film',
            category=self.category1,
            funding_goal=Decimal('1000000.00'),
            funding_deadline=date.today() + timedelta(days=30),
            campaign_duration=30,
            min_investment=Decimal('1000.00'),
            max_investment=Decimal('100000.00'),
            equity_offered=Decimal('20.00'),
            genre='action',
            language='English',
            status='active'
        )
        
        self.campaign2 = Campaign.objects.create(
            creator=self.creator,
            title='Documentary Campaign',
            description='A documentary film',
            short_description='Documentary',
            category=self.category2,
            funding_goal=Decimal('500000.00'),
            funding_deadline=date.today() + timedelta(days=60),
            campaign_duration=60,
            min_investment=Decimal('500.00'),
            max_investment=Decimal('50000.00'),
            equity_offered=Decimal('15.00'),
            genre='documentary',
            language='Sinhala',
            status='active'
        )
    
    def test_campaign_search_by_title(self):
        """Test searching campaigns by title"""
        response = self.client.get(reverse('campaigns:campaign-list'), {'search': 'Action'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Action Film Campaign')
    
    def test_campaign_filter_by_category(self):
        """Test filtering campaigns by category"""
        response = self.client.get(reverse('campaigns:campaign-list'), {'category': self.category1.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['category'], self.category1.pk)
    
    def test_campaign_filter_by_genre(self):
        """Test filtering campaigns by genre"""
        response = self.client.get(reverse('campaigns:campaign-list'), {'genre': 'action'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['genre'], 'action')
    
    def test_campaign_filter_by_language(self):
        """Test filtering campaigns by language"""
        response = self.client.get(reverse('campaigns:campaign-list'), {'language': 'Sinhala'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['language'], 'Sinhala')
    
    def test_campaign_filter_by_status(self):
        """Test filtering campaigns by status"""
        response = self.client.get(reverse('campaigns:campaign-list'), {'status': 'active'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_campaign_filter_by_funding_goal_range(self):
        """Test filtering campaigns by funding goal range"""
        response = self.client.get(
            reverse('campaigns:campaign-list'),
            {'min_goal': '600000', 'max_goal': '1500000'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Action Film Campaign')
    
    def test_campaign_ordering(self):
        """Test campaign ordering"""
        # Test ordering by funding goal (descending)
        response = self.client.get(reverse('campaigns:campaign-list'), {'ordering': '-funding_goal'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['title'], 'Action Film Campaign')
        self.assertEqual(response.data['results'][1]['title'], 'Documentary Campaign')
        
        # Test ordering by creation date (newest first)
        response = self.client.get(reverse('campaigns:campaign-list'), {'ordering': '-created_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CampaignRewardViewsTest(APITestCase):
    """Test cases for CampaignReward views"""
    
    def setUp(self):
        self.client = APIClient()
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
        
        self.creator_token = RefreshToken.for_user(self.creator)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.creator_token.access_token}')
        
        self.reward_data = {
            'campaign': self.campaign.pk,
            'name': 'Early Bird Reward',
            'description': 'Special reward for early backers',
            'minimum_amount': '5000.00',
            'reward_type': 'equity',
            'reward_value': '0.5',
            'quantity_available': 100,
            'delivery_date': (date.today() + timedelta(days=60)).isoformat(),
            'is_active': True
        }
    
    def test_create_campaign_reward(self):
        """Test creating a campaign reward via API"""
        response = self.client.post(reverse('campaigns:reward-create'), self.reward_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CampaignReward.objects.filter(name='Early Bird Reward').exists())
    
    def test_campaign_reward_list(self):
        """Test campaign reward list endpoint"""
        # Create a reward first
        reward = CampaignReward.objects.create(
            campaign=self.campaign,
            name='Early Bird Reward',
            description='Special reward for early backers',
            minimum_amount=Decimal('5000.00'),
            reward_type='equity',
            reward_value=Decimal('0.5'),
            quantity_available=100,
            delivery_date=date.today() + timedelta(days=60),
            is_active=True
        )
        
        response = self.client.get(reverse('campaigns:reward-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_campaign_reward_detail(self):
        """Test campaign reward detail endpoint"""
        # Create a reward first
        reward = CampaignReward.objects.create(
            campaign=self.campaign,
            name='Early Bird Reward',
            description='Special reward for early backers',
            minimum_amount=Decimal('5000.00'),
            reward_type='equity',
            reward_value=Decimal('0.5'),
            quantity_available=100,
            delivery_date=date.today() + timedelta(days=60),
            is_active=True
        )
        
        response = self.client.get(
            reverse('campaigns:reward-detail', kwargs={'pk': reward.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Early Bird Reward')
    
    def test_campaign_reward_update(self):
        """Test campaign reward update endpoint"""
        # Create a reward first
        reward = CampaignReward.objects.create(
            campaign=self.campaign,
            name='Early Bird Reward',
            description='Special reward for early backers',
            minimum_amount=Decimal('5000.00'),
            reward_type='equity',
            reward_value=Decimal('0.5'),
            quantity_available=100,
            delivery_date=date.today() + timedelta(days=60),
            is_active=True
        )
        
        update_data = {
            'name': 'Updated Reward Name',
            'minimum_amount': '7500.00'
        }
        
        response = self.client.patch(
            reverse('campaigns:reward-detail', kwargs={'pk': reward.pk}),
            update_data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify data was updated
        reward.refresh_from_db()
        self.assertEqual(reward.name, 'Updated Reward Name')
        self.assertEqual(reward.minimum_amount, Decimal('7500.00'))


class CampaignIntegrationTest(TestCase):
    """Integration tests for campaign functionality"""
    
    def setUp(self):
        self.client = Client()
        self.creator = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='creatorpass123',
            user_type='creator'
        )
        self.client.force_login(self.creator)
        
        self.category = CampaignCategory.objects.create(
            name='Feature Film',
            description='Full-length feature films'
        )
    
    def test_complete_campaign_workflow(self):
        """Test complete campaign workflow from creation to activation"""
        # Step 1: Create campaign
        campaign_data = {
            'title': 'Test Film Campaign',
            'subtitle': 'An amazing test film',
            'description': 'This is a detailed description of the test film campaign',
            'short_description': 'A short description of the test film',
            'category': self.category.pk,
            'funding_goal': '1000000.00',
            'funding_deadline': (date.today() + timedelta(days=30)).isoformat(),
            'campaign_duration': 30,
            'min_investment': '1000.00',
            'max_investment': '100000.00',
            'equity_offered': '20.00',
            'project_type': 'feature_film',
            'genre': 'drama',
            'language': 'Sinhala'
        }
        
        response = self.client.post(reverse('campaigns:campaign-create'), campaign_data)
        self.assertEqual(response.status_code, 201)
        
        # Step 2: Submit campaign for review
        campaign = Campaign.objects.get(title='Test Film Campaign')
        submit_data = {'action': 'submit'}
        
        response = self.client.post(
            reverse('campaigns:campaign-submit', kwargs={'pk': campaign.pk}),
            submit_data
        )
        self.assertEqual(response.status_code, 200)
        
        # Step 3: Approve campaign (admin action)
        campaign.status = 'approved'
        campaign.save()
        
        # Step 4: Activate campaign
        activate_data = {'action': 'activate'}
        response = self.client.post(
            reverse('campaigns:campaign-activate', kwargs={'pk': campaign.pk}),
            activate_data
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify final status
        campaign.refresh_from_db()
        self.assertEqual(campaign.status, 'active')
    
    def test_campaign_with_rewards_workflow(self):
        """Test campaign creation with rewards"""
        # Create campaign
        campaign_data = {
            'title': 'Test Film Campaign',
            'description': 'Test description',
            'short_description': 'Short description',
            'category': self.category.pk,
            'funding_goal': '1000000.00',
            'funding_deadline': (date.today() + timedelta(days=30)).isoformat(),
            'campaign_duration': 30,
            'min_investment': '1000.00',
            'max_investment': '100000.00',
            'equity_offered': '20.00'
        }
        
        response = self.client.post(reverse('campaigns:campaign-create'), campaign_data)
        self.assertEqual(response.status_code, 201)
        
        # Create reward for the campaign
        campaign = Campaign.objects.get(title='Test Film Campaign')
        reward_data = {
            'campaign': campaign.pk,
            'name': 'Early Bird Reward',
            'description': 'Special reward for early backers',
            'minimum_amount': '5000.00',
            'reward_type': 'equity',
            'reward_value': '0.5',
            'quantity_available': 100,
            'delivery_date': (date.today() + timedelta(days=60)).isoformat(),
            'is_active': True
        }
        
        response = self.client.post(reverse('campaigns:reward-create'), reward_data)
        self.assertEqual(response.status_code, 201)
        
        # Verify reward was created
        self.assertTrue(CampaignReward.objects.filter(name='Early Bird Reward').exists())


class CampaignValidationTest(APITestCase):
    """Test cases for campaign data validation"""
    
    def setUp(self):
        self.client = APIClient()
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
        
        self.creator_token = RefreshToken.for_user(self.creator)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.creator_token.access_token}')
    
    def test_invalid_funding_goal(self):
        """Test invalid funding goal validation"""
        invalid_campaign_data = {
            'title': 'Test Film Campaign',
            'description': 'Test description',
            'short_description': 'Short description',
            'category': self.category.pk,
            'funding_goal': '-1000.00',  # Negative funding goal
            'funding_deadline': (date.today() + timedelta(days=30)).isoformat(),
            'campaign_duration': 30,
            'min_investment': '1000.00',
            'max_investment': '100000.00',
            'equity_offered': '20.00'
        }
        
        response = self.client.post(reverse('campaigns:campaign-create'), invalid_campaign_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_funding_deadline(self):
        """Test invalid funding deadline validation"""
        invalid_campaign_data = {
            'title': 'Test Film Campaign',
            'description': 'Test description',
            'short_description': 'Short description',
            'category': self.category.pk,
            'funding_goal': '1000000.00',
            'funding_deadline': (date.today() - timedelta(days=1)).isoformat(),  # Past date
            'campaign_duration': 30,
            'min_investment': '1000.00',
            'max_investment': '100000.00',
            'equity_offered': '20.00'
        }
        
        response = self.client.post(reverse('campaigns:campaign-create'), invalid_campaign_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_equity_offered(self):
        """Test invalid equity offered validation"""
        invalid_campaign_data = {
            'title': 'Test Film Campaign',
            'description': 'Test description',
            'short_description': 'Short description',
            'category': self.category.pk,
            'funding_goal': '1000000.00',
            'funding_deadline': (date.today() + timedelta(days=30)).isoformat(),
            'campaign_duration': 30,
            'min_investment': '1000.00',
            'max_investment': '100000.00',
            'equity_offered': '150.00'  # More than 100%
        }
        
        response = self.client.post(reverse('campaigns:campaign-create'), invalid_campaign_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_missing_required_fields(self):
        """Test missing required fields validation"""
        incomplete_campaign_data = {
            'title': 'Test Film Campaign',
            # Missing required fields
        }
        
        response = self.client.post(reverse('campaigns:campaign-create'), incomplete_campaign_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
