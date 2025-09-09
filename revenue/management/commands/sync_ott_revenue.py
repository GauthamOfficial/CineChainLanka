from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from revenue.models import OTTPlatformIntegration, RevenueEntry, RevenueSource
from revenue.ott_integration import OTTIntegrationService
from campaigns.models import Campaign
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync revenue data from OTT platforms'

    def add_arguments(self, parser):
        parser.add_argument(
            '--platform',
            type=str,
            help='Specific platform to sync (netflix, amazon_prime, disney_plus)',
        )
        parser.add_argument(
            '--campaign-id',
            type=int,
            help='Specific campaign to sync',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to sync (default: 30)',
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Run in test mode (no actual data changes)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting OTT revenue sync...')
        )

        try:
            ott_service = OTTIntegrationService()
            
            # Get platforms to sync
            platforms_query = OTTPlatformIntegration.objects.filter(is_active=True)
            if options['platform']:
                platforms_query = platforms_query.filter(name=options['platform'])
            
            if not platforms_query.exists():
                self.stdout.write(
                    self.style.WARNING('No active OTT platforms found')
                )
                return
            
            # Get campaigns to sync
            campaigns_query = Campaign.objects.filter(status__in=['funded', 'completed'])
            if options['campaign_id']:
                campaigns_query = campaigns_query.filter(id=options['campaign_id'])
            
            if not campaigns_query.exists():
                self.stdout.write(
                    self.style.WARNING('No campaigns found to sync')
                )
                return
            
            synced_count = 0
            
            for platform in platforms_query:
                self.stdout.write(f'Syncing {platform.name}...')
                
                for campaign in campaigns_query:
                    try:
                        if options['test']:
                            # Test mode - just show what would be synced
                            self.stdout.write(
                                f'  - Would sync campaign {campaign.id} ({campaign.title})'
                            )
                            continue
                        
                        # Sync revenue data
                        success = ott_service.sync_revenue_data(
                            platform.name, 
                            campaign.id
                        )
                        
                        if success:
                            synced_count += 1
                            self.stdout.write(
                                f'  - Synced campaign {campaign.id} ({campaign.title})'
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'  - Failed to sync campaign {campaign.id} ({campaign.title})'
                                )
                            )
                            
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'  - Error syncing campaign {campaign.id}: {e}'
                            )
                        )
                        logger.error(f'Error syncing campaign {campaign.id}: {e}')
            
            if options['test']:
                self.stdout.write(
                    self.style.SUCCESS('Test mode completed - no data was synced')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Synced {synced_count} campaigns')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during OTT revenue sync: {e}')
            )
            logger.error(f'Error during OTT revenue sync: {e}')

    def create_test_revenue_data(self, platform_name, campaign_id):
        """Create test revenue data for development"""
        try:
            # Get or create revenue source
            source, created = RevenueSource.objects.get_or_create(
                name=platform_name,
                revenue_type='ott_platform',
                defaults={
                    'description': f'{platform_name} streaming revenue',
                    'platform_fee_percentage': Decimal('5.00'),
                    'creator_fee_percentage': Decimal('30.00'),
                    'investor_fee_percentage': Decimal('65.00'),
                }
            )
            
            # Create test revenue entries
            campaign = Campaign.objects.get(id=campaign_id)
            
            # Create entries for the last 30 days
            for i in range(30):
                date = timezone.now().date() - timedelta(days=i)
                amount = Decimal('100.00') + (Decimal(str(i)) * Decimal('10.00'))
                
                RevenueEntry.objects.create(
                    campaign=campaign,
                    source=source,
                    amount=amount,
                    currency='USDT',
                    description=f'{platform_name} test revenue - Day {i+1}',
                    revenue_date=date,
                    status='verified'
                )
            
            self.stdout.write(f'  - Created test revenue data for {platform_name}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating test data: {e}')
            )
            logger.error(f'Error creating test data: {e}')
