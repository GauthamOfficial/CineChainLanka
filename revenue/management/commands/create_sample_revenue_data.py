from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
import random
from revenue.models import RevenueSource, RevenueEntry, Campaign
from campaigns.models import Campaign as CampaignModel


class Command(BaseCommand):
    help = 'Create sample revenue data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--campaign-id',
            type=int,
            help='Specific campaign ID to create revenue data for',
        )
        parser.add_argument(
            '--amount',
            type=int,
            default=10,
            help='Number of revenue entries to create',
        )

    def handle(self, *args, **options):
        campaign_id = options.get('campaign_id')
        amount = options.get('amount', 10)

        if campaign_id:
            campaigns = CampaignModel.objects.filter(id=campaign_id)
        else:
            campaigns = CampaignModel.objects.filter(status__in=['funded', 'completed'])

        if not campaigns.exists():
            self.stdout.write(
                self.style.ERROR('No suitable campaigns found. Create some funded campaigns first.')
            )
            return

        # Get revenue sources
        revenue_sources = RevenueSource.objects.filter(is_active=True)
        if not revenue_sources.exists():
            self.stdout.write(
                self.style.ERROR('No revenue sources found. Run setup_revenue_sources first.')
            )
            return

        # Create sample revenue entries
        created_count = 0
        for campaign in campaigns:
            for i in range(amount):
                # Random revenue source
                source = random.choice(revenue_sources)
                
                # Random amount between 100 and 10000 USDT
                amount_value = Decimal(str(random.uniform(100, 10000)))
                
                # Random date within last 90 days
                days_ago = random.randint(1, 90)
                revenue_date = timezone.now().date() - timedelta(days=days_ago)
                
                # Create revenue entry
                revenue_entry = RevenueEntry.objects.create(
                    campaign=campaign,
                    source=source,
                    amount=amount_value,
                    currency='USDT',
                    description=f'Sample {source.name} revenue - Entry {i+1}',
                    revenue_date=revenue_date,
                    status='verified'  # Mark as verified for testing
                )
                
                created_count += 1
                self.stdout.write(f'Created revenue entry: {revenue_entry.id} for campaign {campaign.title}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample revenue entries')
        )
