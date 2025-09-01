from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from campaigns.models import CampaignCategory, Campaign
from payments.models import PaymentMethod
from kyc.models import KYCRequest

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create sample users
        self.create_sample_users()
        
        # Create sample campaign categories
        self.create_sample_categories()
        
        # Create sample payment methods
        self.create_sample_payment_methods()
        
        # Create sample campaigns
        self.create_sample_campaigns()
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))

    def create_sample_users(self):
        """Create sample users for testing"""
        if User.objects.filter(username='creator1').exists():
            self.stdout.write('Sample users already exist, skipping...')
            return
        
        # Create a creator user
        creator1 = User.objects.create_user(
            username='creator1',
            email='creator1@example.com',
            password='testpass123',
            first_name='John',
            last_name='Director',
            user_type='creator',
            phone_number='+94712345678',
            bio='A passionate filmmaker with 10+ years of experience',
            city='Colombo',
            country='Sri Lanka',
            creator_verified=True,
            creator_category='Film Director'
        )
        
        # Create an investor user
        investor1 = User.objects.create_user(
            username='investor1',
            email='investor1@example.com',
            password='testpass123',
            first_name='Sarah',
            last_name='Investor',
            user_type='investor',
            phone_number='+94787654321',
            bio='Interested in supporting creative projects',
            city='Kandy',
            country='Sri Lanka',
            investment_limit=100000.00
        )
        
        # Create an admin user
        admin_user = User.objects.create_user(
            username='admin_user',
            email='admin@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            user_type='admin',
            is_staff=True,
            is_superuser=False
        )
        
        self.stdout.write(f'Created users: {creator1.username}, {investor1.username}, {admin_user.username}')

    def create_sample_categories(self):
        """Create sample campaign categories"""
        if CampaignCategory.objects.exists():
            self.stdout.write('Sample categories already exist, skipping...')
            return
        
        categories = [
            {
                'name': 'Feature Film',
                'description': 'Full-length feature films and movies',
                'icon': 'film'
            },
            {
                'name': 'Documentary',
                'description': 'Documentary films and educational content',
                'icon': 'documentary'
            },
            {
                'name': 'Short Film',
                'description': 'Short films and experimental content',
                'icon': 'short-film'
            },
            {
                'name': 'Web Series',
                'description': 'Digital series and online content',
                'icon': 'web-series'
            },
            {
                'name': 'Animation',
                'description': 'Animated films and content',
                'icon': 'animation'
            }
        ]
        
        for cat_data in categories:
            category = CampaignCategory.objects.create(**cat_data)
            self.stdout.write(f'Created category: {category.name}')

    def create_sample_payment_methods(self):
        """Create sample payment methods"""
        if PaymentMethod.objects.exists():
            self.stdout.write('Sample payment methods already exist, skipping...')
            return
        
        payment_methods = [
            {
                'name': 'LankaQR',
                'payment_type': 'lanka_qr',
                'description': 'Sri Lanka\'s national QR payment system',
                'processing_fee_percentage': 0.50,
                'processing_fee_fixed': 0.00,
                'minimum_amount': 10.00,
                'maximum_amount': 100000.00
            },
            {
                'name': 'eZ Cash',
                'payment_type': 'ez_cash',
                'description': 'Mobile money transfer service',
                'processing_fee_percentage': 1.00,
                'processing_fee_fixed': 5.00,
                'minimum_amount': 50.00,
                'maximum_amount': 50000.00
            },
            {
                'name': 'FriMi',
                'payment_type': 'frimi',
                'description': 'Digital wallet and payment service',
                'processing_fee_percentage': 0.75,
                'processing_fee_fixed': 3.00,
                'minimum_amount': 25.00,
                'maximum_amount': 75000.00
            },
            {
                'name': 'Bank Transfer',
                'payment_type': 'bank_transfer',
                'description': 'Direct bank transfer',
                'processing_fee_percentage': 0.00,
                'processing_fee_fixed': 0.00,
                'minimum_amount': 100.00,
                'maximum_amount': 1000000.00
            }
        ]
        
        for pm_data in payment_methods:
            payment_method = PaymentMethod.objects.create(**pm_data)
            self.stdout.write(f'Created payment method: {payment_method.name}')

    def create_sample_campaigns(self):
        """Create sample campaigns"""
        if Campaign.objects.exists():
            self.stdout.write('Sample campaigns already exist, skipping...')
            return
        
        creator = User.objects.get(username='creator1')
        category = CampaignCategory.objects.get(name='Feature Film')
        
        # Create a sample campaign
        campaign = Campaign.objects.create(
            creator=creator,
            title='The Lost Kingdom - A Sri Lankan Epic',
            subtitle='A historical drama set in ancient Sri Lanka',
            description='''This is a feature-length historical drama that tells the story of a forgotten kingdom in ancient Sri Lanka. 
            The film will showcase the rich cultural heritage, stunning landscapes, and compelling narrative that will captivate audiences worldwide.
            
            Our team consists of experienced filmmakers, historians, and local talent who are passionate about bringing this story to life.
            We have secured locations, assembled a talented cast, and are ready to begin production once funding is secured.
            
            The film will be shot in 4K resolution with professional cinematography, original music score, and post-production effects
            that will ensure a cinematic experience worthy of international film festivals.''',
            short_description='A historical drama set in ancient Sri Lanka, showcasing rich cultural heritage and stunning landscapes.',
            category=category,
            funding_goal=5000000.00,
            start_date=timezone.now() + timedelta(days=7),
            end_date=timezone.now() + timedelta(days=60),
            estimated_completion_date=timezone.now().date() + timedelta(days=365),
            status='pending_review',
            tags=['historical', 'drama', 'sri-lanka', 'epic', 'culture'],
            risks_and_challenges='''Production challenges include securing historical locations, coordinating with local authorities,
            and managing a large cast and crew. Weather conditions during outdoor shoots may also pose challenges.
            We have contingency plans and experienced production managers to handle these challenges effectively.''',
            team_members=[
                {
                    'name': 'John Director',
                    'role': 'Director',
                    'experience': '10+ years in film direction'
                },
                {
                    'name': 'Jane Producer',
                    'role': 'Producer',
                    'experience': '15+ years in film production'
                },
                {
                    'name': 'Mike Cinematographer',
                    'role': 'Director of Photography',
                    'experience': '12+ years in cinematography'
                }
            ]
        )
        
        self.stdout.write(f'Created campaign: {campaign.title}')
        
        # Create KYC request for the creator
        kyc_request = KYCRequest.objects.create(
            user=creator,
            verification_level='enhanced',
            status='approved',
            legal_name='John Director',
            date_of_birth=timezone.now().date() - timedelta(days=35*365),
            nationality='Sri Lankan',
            residential_address='123 Cinema Street, Colombo 03, Sri Lanka',
            identity_document_type='national_id',
            identity_document_number='123456789V',
            address_proof_type='utility_bill',
            address_proof_date=timezone.now().date() - timedelta(days=30),
            source_of_funds='employment',
            employment_status='self_employed',
            employer_name='Independent Filmmaker',
            reviewed_by=User.objects.get(username='admin'),
            reviewed_at=timezone.now()
        )
        
        self.stdout.write(f'Created KYC request for {creator.username}')
        
        # Update creator KYC status
        creator.kyc_status = 'verified'
        creator.kyc_verified_at = timezone.now()
        creator.save()
        
        self.stdout.write(f'Updated KYC status for {creator.username}')

