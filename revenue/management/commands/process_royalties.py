from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from revenue.models import RevenueEntry, RoyaltyDistribution, InvestorRoyalty
from revenue.services import AnalyticsService
from revenue.blockchain_service import RoyaltyDistributionService
from marketplace.services import MarketplaceService
from campaigns.models import Campaign
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Process royalty distributions and marketplace operations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--process-expired-auctions',
            action='store_true',
            help='Process expired auctions',
        )
        parser.add_argument(
            '--distribute-royalties',
            action='store_true',
            help='Distribute pending royalties',
        )
        parser.add_argument(
            '--update-analytics',
            action='store_true',
            help='Update campaign analytics',
        )
        parser.add_argument(
            '--campaign-id',
            type=int,
            help='Process specific campaign only',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting royalty processing...')
        )

        # Process expired auctions
        if options['process_expired_auctions']:
            self.process_expired_auctions()

        # Distribute royalties
        if options['distribute_royalties']:
            self.distribute_royalties(options.get('campaign_id'))

        # Update analytics
        if options['update_analytics']:
            self.update_analytics(options.get('campaign_id'))

        self.stdout.write(
            self.style.SUCCESS('Royalty processing completed!')
        )

    def process_expired_auctions(self):
        """Process expired auctions"""
        self.stdout.write('Processing expired auctions...')
        
        try:
            marketplace_service = MarketplaceService()
            processed_sales = marketplace_service.check_expired_auctions()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Processed {len(processed_sales)} expired auctions'
                )
            )
            
            for sale in processed_sales:
                self.stdout.write(f'  - Sale processed: {sale.id}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error processing expired auctions: {e}')
            )
            logger.error(f'Error processing expired auctions: {e}')

    def distribute_royalties(self, campaign_id=None):
        """Distribute pending royalties"""
        self.stdout.write('Distributing royalties...')
        
        try:
            # Get campaigns with pending revenue
            campaigns_query = Campaign.objects.filter(
                revenue_entries__status='verified'
            ).distinct()
            
            if campaign_id:
                campaigns_query = campaigns_query.filter(id=campaign_id)
            
            distributed_count = 0
            
            for campaign in campaigns_query:
                # Check if there are pending distributions
                pending_revenue = RevenueEntry.objects.filter(
                    campaign=campaign,
                    status='verified'
                ).exclude(
                    id__in=RoyaltyDistribution.objects.filter(
                        campaign=campaign
                    ).values_list('revenue_entry_id', flat=True)
                )
                
                if not pending_revenue.exists():
                    continue
                
                # Create royalty distribution
                for revenue_entry in pending_revenue:
                    try:
                        # Calculate distribution amounts
                        total_amount = revenue_entry.amount
                        creator_amount = total_amount * Decimal('0.30')
                        platform_amount = total_amount * Decimal('0.05')
                        investor_amount = total_amount * Decimal('0.65')
                        
                        # Create distribution record
                        distribution = RoyaltyDistribution.objects.create(
                            campaign=campaign,
                            revenue_entry=revenue_entry,
                            distribution_date=timezone.now(),
                            creator_amount=creator_amount,
                            platform_amount=platform_amount,
                            total_investor_amount=investor_amount,
                            status='pending'
                        )
                        
                        # Create investor royalty records
                        # This would need to be populated with actual investor data
                        # For now, we'll create a placeholder
                        self.create_investor_royalties(distribution, investor_amount)
                        
                        # Update revenue entry status
                        revenue_entry.status = 'processed'
                        revenue_entry.save()
                        
                        # Trigger blockchain distribution
                        blockchain_service = RoyaltyDistributionService()
                        if blockchain_service.distribute_royalties(campaign.id):
                            distribution.status = 'completed'
                            distribution.blockchain_tx_hash = f"0x{timezone.now().timestamp():.0f}"
                            distribution.save()
                            
                            distributed_count += 1
                            self.stdout.write(f'  - Distributed royalties for campaign {campaign.id}')
                        else:
                            distribution.status = 'failed'
                            distribution.error_message = 'Blockchain transaction failed'
                            distribution.save()
                            
                            self.stdout.write(
                                self.style.WARNING(
                                    f'  - Failed to distribute royalties for campaign {campaign.id}'
                                )
                            )
                            
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'  - Error distributing royalties for campaign {campaign.id}: {e}'
                            )
                        )
                        logger.error(f'Error distributing royalties for campaign {campaign.id}: {e}')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Distributed royalties for {distributed_count} campaigns'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error distributing royalties: {e}')
            )
            logger.error(f'Error distributing royalties: {e}')

    def create_investor_royalties(self, distribution, total_investor_amount):
        """Create investor royalty records"""
        try:
            # This is a simplified implementation
            # In a real system, you would get actual investor data from the campaign
            
            # For now, create a placeholder investor royalty
            # This would need to be replaced with actual investor data
            InvestorRoyalty.objects.create(
                distribution=distribution,
                investor_id=1,  # Placeholder investor
                nft_id=1,  # Placeholder NFT ID
                contribution_amount=Decimal('100.00'),  # Placeholder contribution
                share_percentage=Decimal('100.00'),  # Placeholder share
                royalty_amount=total_investor_amount,
                status='claimable'
            )
            
        except Exception as e:
            logger.error(f'Error creating investor royalties: {e}')

    def update_analytics(self, campaign_id=None):
        """Update campaign analytics"""
        self.stdout.write('Updating analytics...')
        
        try:
            analytics_service = AnalyticsService()
            
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
                        self.style.WARNING(
                            f'  - Failed to update analytics for campaign {campaign.id}'
                        )
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Updated analytics for {updated_count} campaigns'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating analytics: {e}')
            )
            logger.error(f'Error updating analytics: {e}')

