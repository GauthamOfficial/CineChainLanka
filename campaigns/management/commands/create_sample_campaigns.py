from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from campaigns.models import Campaign, CampaignCategory, CampaignReward
from users.models import UserProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample campaigns for development'

    def handle(self, *args, **options):
        # Create categories if they don't exist
        categories_data = [
            {'name': 'Film', 'description': 'Feature films and movies', 'icon': '🎬'},
            {'name': 'Documentary', 'description': 'Documentary films', 'icon': '📹'},
            {'name': 'Web Series', 'description': 'Online series and shows', 'icon': '📺'},
            {'name': 'Short Film', 'description': 'Short films and videos', 'icon': '🎥'},
            {'name': 'Animation', 'description': 'Animated content', 'icon': '🎨'},
            {'name': 'Music Video', 'description': 'Music videos and clips', 'icon': '🎵'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = CampaignCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Get or create a test creator
        creator, created = User.objects.get_or_create(
            username='test_creator',
            defaults={
                'email': 'creator@cinechainlanka.com',
                'first_name': 'Test',
                'last_name': 'Creator',
                'user_type': 'creator',
                'is_active': True
            }
        )
        if created:
            creator.set_password('testpass123')
            creator.save()
            UserProfile.objects.get_or_create(user=creator)
            self.stdout.write(f'Created test creator: {creator.username}')
        else:
            UserProfile.objects.get_or_create(user=creator)
            self.stdout.write(f'Test creator already exists: {creator.username}')

        # Create sample campaigns
        now = timezone.now()
        campaigns_data = [
            {
                'title': 'The Lost Island',
                'subtitle': 'A thrilling adventure film set in Sri Lanka',
                'description': 'Join us on an epic journey through the mysterious jungles of Sri Lanka as we tell the story of a lost civilization and the brave explorers who discover its secrets.',
                'short_description': 'An adventure film exploring Sri Lanka\'s hidden treasures',
                'category': categories['Film'],
                'funding_goal': 5000000,
                'current_funding': 1200000,
                'status': 'active',
                'start_date': now - timedelta(days=30),
                'end_date': now + timedelta(days=60),
                'estimated_completion_date': now + timedelta(days=180)
            },
            {
                'title': 'Voices of the Ocean',
                'subtitle': 'Documentary about marine conservation',
                'description': 'This documentary explores the impact of climate change on Sri Lanka\'s marine ecosystems and the efforts of local communities to protect their coastal heritage.',
                'short_description': 'A documentary about marine conservation in Sri Lanka',
                'category': categories['Documentary'],
                'funding_goal': 2000000,
                'current_funding': 800000,
                'status': 'active',
                'start_date': now - timedelta(days=15),
                'end_date': now + timedelta(days=45),
                'estimated_completion_date': now + timedelta(days=120)
            },
            {
                'title': 'Tech Startup Stories',
                'subtitle': 'Web series about Sri Lankan entrepreneurs',
                'description': 'A web series showcasing the inspiring stories of Sri Lankan tech entrepreneurs who are building innovative solutions for global challenges.',
                'short_description': 'Web series about Sri Lankan tech entrepreneurs',
                'category': categories['Web Series'],
                'funding_goal': 1500000,
                'current_funding': 1500000,
                'status': 'funded',
                'start_date': now - timedelta(days=60),
                'end_date': now - timedelta(days=10),
                'estimated_completion_date': now + timedelta(days=90)
            },
            {
                'title': 'The Last Dance',
                'subtitle': 'Short film about traditional dance',
                'description': 'A beautiful short film capturing the essence of traditional Sri Lankan dance forms and their significance in preserving cultural heritage.',
                'short_description': 'Short film about traditional Sri Lankan dance',
                'category': categories['Short Film'],
                'funding_goal': 500000,
                'current_funding': 300000,
                'status': 'active',
                'start_date': now - timedelta(days=7),
                'end_date': now + timedelta(days=23),
                'estimated_completion_date': now + timedelta(days=60)
            }
        ]

        for campaign_data in campaigns_data:
            campaign, created = Campaign.objects.get_or_create(
                title=campaign_data['title'],
                defaults={
                    **campaign_data,
                    'creator': creator
                }
            )
            
            if created:
                # Create rewards for the campaign
                rewards_data = [
                    {
                        'title': 'Digital Copy',
                        'description': 'Get a digital copy of the final product',
                        'amount': 1000,
                        'max_backers': 100,
                        'estimated_delivery': now.date() + timedelta(days=90)
                    },
                    {
                        'title': 'Special Thanks',
                        'description': 'Your name in the credits + digital copy',
                        'amount': 5000,
                        'max_backers': 50,
                        'estimated_delivery': now.date() + timedelta(days=90)
                    },
                    {
                        'title': 'Behind the Scenes',
                        'description': 'Exclusive behind-the-scenes content + all above',
                        'amount': 10000,
                        'max_backers': 25,
                        'estimated_delivery': now.date() + timedelta(days=90)
                    }
                ]
                
                for reward_data in rewards_data:
                    CampaignReward.objects.create(
                        campaign=campaign,
                        **reward_data
                    )
                
                self.stdout.write(f'Created campaign: {campaign.title}')
            else:
                self.stdout.write(f'Campaign already exists: {campaign.title}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample campaigns!')
        )
