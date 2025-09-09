from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from revenue.tracking_service import RevenueTrackingService
from marketplace.services import MarketplaceService
from revenue.services import AnalyticsService
from campaigns.models import Campaign
from revenue.models import RevenueEntry, RoyaltyDistribution
from marketplace.models import NFTListing
from django.db.models import Sum
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run all Phase 3 operations: marketplace, analytics, and revenue tracking'

    def add_arguments(self, parser):
        parser.add_argument(
            '--process-marketplace',
            action='store_true',
            help='Process marketplace operations (expired auctions)',
        )
        parser.add_argument(
            '--sync-ott',
            action='store_true',
            help='Sync revenue from OTT platforms',
        )
        parser.add_argument(
            '--distribute-royalties',
            action='store_true',
            help='Distribute pending royalties',
        )
        parser.add_argument(
            '--update-analytics',
            action='store_true',
            help='Update all campaign analytics',
        )
        parser.add_argument(
            '--run-all',
            action='store_true',
            help='Run all operations',
        )
        parser.add_argument(
            '--campaign-id',
            type=int,
            help='Process specific campaign only',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting Phase 3 operations...')
        )

        tracking_service = RevenueTrackingService()
        marketplace_service = MarketplaceService()
        analytics_service = AnalyticsService()

        # Process marketplace operations
        if options['process_marketplace'] or options['run_all']:
            self.process_marketplace_operations(marketplace_service)

        # Sync OTT revenue
        if options['sync_ott'] or options['run_all']:
            self.sync_ott_revenue(tracking_service)

        # Distribute royalties
        if options['distribute_royalties'] or options['run_all']:
            self.distribute_royalties(tracking_service, options.get('campaign_id'))

        # Update analytics
        if options['update_analytics'] or options['run_all']:
            self.update_analytics(analytics_service, options.get('campaign_id'))

        self.stdout.write(
            self.style.SUCCESS('Phase 3 operations completed!')
        )

    def process_marketplace_operations(self, marketplace_service):
        """Process marketplace operations"""
        self.stdout.write('Processing marketplace operations...')
        
        try:
            # Process expired auctions
            processed_sales = marketplace_service.check_expired_auctions()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Processed {len(processed_sales)} expired auctions'
                )
            )
            
            # Get marketplace stats
            stats = marketplace_service.get_marketplace_stats()
            self.stdout.write(f'  - Total listings: {stats.get("total_listings", 0)}')
            self.stdout.write(f'  - Active listings: {stats.get("active_listings", 0)}')
            self.stdout.write(f'  - Sold listings: {stats.get("sold_listings", 0)}')
            self.stdout.write(f'  - Total volume: ${stats.get("total_volume", 0):,.2f}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error processing marketplace operations: {e}')
            )
            logger.error(f'Error processing marketplace operations: {e}')

    def sync_ott_revenue(self, tracking_service):
        """Sync revenue from OTT platforms"""
        self.stdout.write('Syncing OTT revenue...')
        
        try:
            results = tracking_service.sync_all_ott_revenue()
            
            total_synced = 0
            for platform, count in results.items():
                self.stdout.write(f'  - {platform}: {count} campaigns synced')
                total_synced += count
            
            self.stdout.write(
                self.style.SUCCESS(f'Total OTT revenue synced: {total_synced} campaigns')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error syncing OTT revenue: {e}')
            )
            logger.error(f'Error syncing OTT revenue: {e}')

    def distribute_royalties(self, tracking_service, campaign_id=None):
        """Distribute pending royalties"""
        self.stdout.write('Distributing royalties...')
        
        try:
            if campaign_id:
                # Process specific campaign
                success = tracking_service.distribute_royalties(campaign_id)
                if success:
                    self.stdout.write(
                        self.style.SUCCESS(f'Royalties distributed for campaign {campaign_id}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Failed to distribute royalties for campaign {campaign_id}')
                    )
            else:
                # Process all pending distributions
                processed_count = tracking_service.process_pending_distributions()
                self.stdout.write(
                    self.style.SUCCESS(f'Distributed royalties for {processed_count} campaigns')
                )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error distributing royalties: {e}')
            )
            logger.error(f'Error distributing royalties: {e}')

    def update_analytics(self, analytics_service, campaign_id=None):
        """Update campaign analytics"""
        self.stdout.write('Updating analytics...')
        
        try:
            from campaigns.models import Campaign
            
            # Get campaigns to update
            campaigns_query = Campaign.objects.all()
            if campaign_id:
                campaigns_query = campaigns_query.filter(id=campaign_id)
            
            updated_count = 0
            for campaign in campaigns_query:
                if analytics_service.update_campaign_analytics(campaign.id):
                    updated_count += 1
                    self.stdout.write(f'  - Updated analytics for campaign {campaign.id}')
                else:
                    self.stdout.write(
                        self.style.WARNING(f'  - Failed to update analytics for campaign {campaign.id}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f'Updated analytics for {updated_count} campaigns')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating analytics: {e}')
            )
            logger.error(f'Error updating analytics: {e}')

    def get_system_status(self):
        """Get overall system status"""
        try:
            from campaigns.models import Campaign
            from revenue.models import RevenueEntry, RoyaltyDistribution
            from marketplace.models import NFTListing
            
            # Campaign stats
            total_campaigns = Campaign.objects.count()
            active_campaigns = Campaign.objects.filter(status='active').count()
            funded_campaigns = Campaign.objects.filter(status='funded').count()
            
            # Revenue stats
            total_revenue = RevenueEntry.objects.aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0')
            
            pending_distributions = RoyaltyDistribution.objects.filter(
                status='pending'
            ).count()
            
            # Marketplace stats
            total_listings = NFTListing.objects.count()
            active_listings = NFTListing.objects.filter(status='active').count()
            
            self.stdout.write('\n=== System Status ===')
            self.stdout.write(f'Campaigns: {total_campaigns} total, {active_campaigns} active, {funded_campaigns} funded')
            self.stdout.write(f'Revenue: ${total_revenue:,.2f} total, {pending_distributions} pending distributions')
            self.stdout.write(f'Marketplace: {total_listings} total listings, {active_listings} active')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error getting system status: {e}')
            )
            logger.error(f'Error getting system status: {e}')
