import logging
from decimal import Decimal
from typing import Dict, List, Optional, Any
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    RevenueEntry, RoyaltyDistribution, InvestorRoyalty, 
    RevenueAnalytics, RevenueSource, Campaign, OTTPlatformIntegration
)
from django.db.models import Sum, Count
from .blockchain_service import RoyaltyDistributionService
from .ott_integration import OTTIntegrationService
from campaigns.models import Campaign as CampaignModel

logger = logging.getLogger(__name__)


class RevenueTrackingService:
    """Comprehensive revenue tracking and distribution service"""
    
    def __init__(self):
        self.royalty_service = RoyaltyDistributionService()
        self.ott_service = OTTIntegrationService()
    
    def track_revenue(self, campaign_id: int, amount: Decimal, source: str, 
                     description: str, currency: str = 'USDT') -> bool:
        """Track new revenue for a campaign"""
        try:
            with transaction.atomic():
                # Get campaign
                campaign = CampaignModel.objects.get(id=campaign_id)
                
                # Get or create revenue source
                revenue_source, created = RevenueSource.objects.get_or_create(
                    name=source,
                    revenue_type='other',
                    defaults={
                        'description': f'Revenue from {source}',
                        'platform_fee_percentage': Decimal('5.00'),
                        'creator_fee_percentage': Decimal('30.00'),
                        'investor_fee_percentage': Decimal('65.00'),
                    }
                )
                
                # Create revenue entry
                revenue_entry = RevenueEntry.objects.create(
                    campaign=campaign,
                    source=revenue_source,
                    amount=amount,
                    currency=currency,
                    description=description,
                    revenue_date=timezone.now().date(),
                    status='verified'
                )
                
                # Update analytics
                self._update_campaign_analytics(campaign)
                
                # Trigger royalty distribution
                self._trigger_royalty_distribution(campaign, revenue_entry)
                
                logger.info(f"Revenue tracked: {amount} {currency} for campaign {campaign_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error tracking revenue: {e}")
            return False
    
    def process_ott_revenue(self, platform_name: str, campaign_id: int, 
                           revenue_data: List[Dict]) -> bool:
        """Process revenue from OTT platform"""
        try:
            with transaction.atomic():
                campaign = CampaignModel.objects.get(id=campaign_id)
                
                # Get or create OTT revenue source
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
                
                total_revenue = Decimal('0')
                
                # Create revenue entries
                for entry_data in revenue_data:
                    amount = Decimal(str(entry_data.get('amount', 0)))
                    total_revenue += amount
                    
                    RevenueEntry.objects.create(
                        campaign=campaign,
                        source=source,
                        amount=amount,
                        currency=entry_data.get('currency', 'USDT'),
                        description=f"{platform_name} revenue - {entry_data.get('title', 'Unknown')}",
                        revenue_date=datetime.fromisoformat(
                            entry_data.get('date', timezone.now().isoformat())
                        ).date(),
                        status='verified'
                    )
                
                # Update analytics
                self._update_campaign_analytics(campaign)
                
                # Trigger royalty distribution
                self._trigger_royalty_distribution(campaign, None)
                
                logger.info(f"OTT revenue processed: {total_revenue} USDT for campaign {campaign_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error processing OTT revenue: {e}")
            return False
    
    def process_marketplace_revenue(self, sale_id: int) -> bool:
        """Process revenue from NFT marketplace sale"""
        try:
            from marketplace.models import NFTSale
            
            with transaction.atomic():
                sale = NFTSale.objects.get(id=sale_id)
                campaign = sale.listing.campaign
                
                # Create revenue entries for platform fee and creator royalty
                platform_source, _ = RevenueSource.objects.get_or_create(
                    name='Marketplace Platform Fee',
                    revenue_type='marketplace',
                    defaults={
                        'description': 'Platform fee from NFT marketplace',
                        'platform_fee_percentage': Decimal('0.00'),
                        'creator_fee_percentage': Decimal('0.00'),
                        'investor_fee_percentage': Decimal('0.00'),
                    }
                )
                
                creator_source, _ = RevenueSource.objects.get_or_create(
                    name='NFT Creator Royalty',
                    revenue_type='marketplace',
                    defaults={
                        'description': 'Creator royalty from NFT sales',
                        'platform_fee_percentage': Decimal('0.00'),
                        'creator_fee_percentage': Decimal('0.00'),
                        'investor_fee_percentage': Decimal('0.00'),
                    }
                )
                
                # Create platform fee entry
                RevenueEntry.objects.create(
                    campaign=campaign,
                    source=platform_source,
                    amount=sale.platform_fee,
                    currency=sale.currency,
                    description=f"Platform fee from NFT sale #{sale.listing.nft_id}",
                    revenue_date=timezone.now().date(),
                    status='verified'
                )
                
                # Create creator royalty entry
                RevenueEntry.objects.create(
                    campaign=campaign,
                    source=creator_source,
                    amount=sale.creator_royalty,
                    currency=sale.currency,
                    description=f"Creator royalty from NFT sale #{sale.listing.nft_id}",
                    revenue_date=timezone.now().date(),
                    status='verified'
                )
                
                # Update analytics
                self._update_campaign_analytics(campaign)
                
                # Trigger royalty distribution
                self._trigger_royalty_distribution(campaign, None)
                
                logger.info(f"Marketplace revenue processed for sale {sale_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error processing marketplace revenue: {e}")
            return False
    
    def distribute_royalties(self, campaign_id: int) -> bool:
        """Distribute royalties for a campaign"""
        try:
            with transaction.atomic():
                campaign = CampaignModel.objects.get(id=campaign_id)
                
                # Get pending revenue entries
                pending_revenue = RevenueEntry.objects.filter(
                    campaign=campaign,
                    status='verified'
                ).exclude(
                    id__in=RoyaltyDistribution.objects.filter(
                        campaign=campaign
                    ).values_list('revenue_entry_id', flat=True)
                )
                
                if not pending_revenue.exists():
                    logger.info(f"No pending revenue for campaign {campaign_id}")
                    return True
                
                total_revenue = sum(entry.amount for entry in pending_revenue)
                
                # Calculate distribution amounts
                creator_amount = total_revenue * Decimal('0.30')
                platform_amount = total_revenue * Decimal('0.05')
                investor_amount = total_revenue * Decimal('0.65')
                
                # Create distribution record
                distribution = RoyaltyDistribution.objects.create(
                    campaign=campaign,
                    revenue_entry=pending_revenue.first(),  # Use first entry as reference
                    distribution_date=timezone.now(),
                    creator_amount=creator_amount,
                    platform_amount=platform_amount,
                    total_investor_amount=investor_amount,
                    status='pending'
                )
                
                # Create investor royalty records
                self._create_investor_royalties(distribution, investor_amount)
                
                # Update revenue entries status
                pending_revenue.update(status='processed')
                
                # Trigger blockchain distribution
                if self.royalty_service.distribute_royalties(campaign_id):
                    distribution.status = 'completed'
                    distribution.blockchain_tx_hash = f"0x{timezone.now().timestamp():.0f}"
                    distribution.save()
                    
                    logger.info(f"Royalties distributed for campaign {campaign_id}")
                    return True
                else:
                    distribution.status = 'failed'
                    distribution.error_message = 'Blockchain transaction failed'
                    distribution.save()
                    
                    logger.error(f"Failed to distribute royalties for campaign {campaign_id}")
                    return False
                
        except Exception as e:
            logger.error(f"Error distributing royalties: {e}")
            return False
    
    def get_revenue_summary(self, campaign_id: int = None, 
                           start_date: datetime = None, 
                           end_date: datetime = None) -> Dict:
        """Get comprehensive revenue summary"""
        try:
            # Set default date range
            if not end_date:
                end_date = timezone.now()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Build query
            query = RevenueEntry.objects.filter(
                revenue_date__range=[start_date.date(), end_date.date()],
                status__in=['verified', 'processed']
            )
            
            if campaign_id:
                query = query.filter(campaign_id=campaign_id)
            
            # Calculate totals
            total_revenue = query.aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0')
            
            # Revenue by source
            revenue_by_source = query.values('source__name').annotate(
                total=Sum('amount'),
                count=Count('id')
            ).order_by('-total')
            
            # Revenue by campaign
            revenue_by_campaign = query.values(
                'campaign__title', 'campaign__id'
            ).annotate(
                total=Sum('amount'),
                count=Count('id')
            ).order_by('-total')
            
            # Daily revenue trend
            daily_revenue = []
            current_date = start_date.date()
            while current_date <= end_date.date():
                day_revenue = query.filter(
                    revenue_date=current_date
                ).aggregate(
                    total=Sum('amount')
                )['total'] or Decimal('0')
                
                daily_revenue.append({
                    'date': current_date.isoformat(),
                    'revenue': float(day_revenue)
                })
                
                current_date += timedelta(days=1)
            
            # Distribution summary
            distributions = RoyaltyDistribution.objects.filter(
                campaign_id=campaign_id
            ) if campaign_id else RoyaltyDistribution.objects.all()
            
            total_distributed = distributions.aggregate(
                total=Sum('creator_amount') + Sum('platform_amount') + Sum('total_investor_amount')
            )['total'] or Decimal('0')
            
            return {
                'total_revenue': float(total_revenue),
                'total_distributed': float(total_distributed),
                'pending_distribution': float(total_revenue - total_distributed),
                'revenue_by_source': list(revenue_by_source),
                'revenue_by_campaign': list(revenue_by_campaign),
                'daily_revenue': daily_revenue,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting revenue summary: {e}")
            return {}
    
    def _update_campaign_analytics(self, campaign: CampaignModel) -> None:
        """Update campaign analytics"""
        try:
            # Get or create analytics record
            analytics, created = RevenueAnalytics.objects.get_or_create(
                campaign=campaign,
                defaults={
                    'total_revenue': Decimal('0'),
                    'total_creator_royalties': Decimal('0'),
                    'total_platform_fees': Decimal('0'),
                    'total_investor_royalties': Decimal('0'),
                    'total_distributions': 0
                }
            )
            
            # Calculate current totals
            revenue_entries = RevenueEntry.objects.filter(
                campaign=campaign,
                status__in=['verified', 'processed']
            )
            
            total_revenue = revenue_entries.aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0')
            
            # Calculate distributions
            distributions = RoyaltyDistribution.objects.filter(campaign=campaign)
            
            total_creator_royalties = distributions.aggregate(
                total=Sum('creator_amount')
            )['total'] or Decimal('0')
            
            total_platform_fees = distributions.aggregate(
                total=Sum('platform_amount')
            )['total'] or Decimal('0')
            
            total_investor_royalties = distributions.aggregate(
                total=Sum('total_investor_amount')
            )['total'] or Decimal('0')
            
            # Update analytics
            analytics.total_revenue = total_revenue
            analytics.total_creator_royalties = total_creator_royalties
            analytics.total_platform_fees = total_platform_fees
            analytics.total_investor_royalties = total_investor_royalties
            analytics.total_distributions = distributions.count()
            
            if distributions.exists():
                analytics.last_distribution_date = distributions.order_by(
                    '-distribution_date'
                ).first().distribution_date
            
            analytics.save()
            
        except Exception as e:
            logger.error(f"Error updating campaign analytics: {e}")
    
    def _trigger_royalty_distribution(self, campaign: CampaignModel, 
                                    revenue_entry: Optional[RevenueEntry]) -> None:
        """Trigger royalty distribution for a campaign"""
        try:
            # Check if there's enough revenue to distribute
            total_revenue = RevenueEntry.objects.filter(
                campaign=campaign,
                status='verified'
            ).aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0')
            
            if total_revenue < Decimal('10.00'):  # Minimum distribution threshold
                logger.info(f"Revenue too low for distribution: {total_revenue}")
                return
            
            # Trigger distribution
            self.distribute_royalties(campaign.id)
            
        except Exception as e:
            logger.error(f"Error triggering royalty distribution: {e}")
    
    def _create_investor_royalties(self, distribution: RoyaltyDistribution, 
                                 total_investor_amount: Decimal) -> None:
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
            logger.error(f"Error creating investor royalties: {e}")
    
    def sync_all_ott_revenue(self) -> Dict[str, int]:
        """Sync revenue from all OTT platforms"""
        try:
            results = {}
            
            # Get active OTT platforms
            platforms = OTTPlatformIntegration.objects.filter(is_active=True)
            
            for platform in platforms:
                try:
                    # Get campaigns for this platform
                    campaigns = CampaignModel.objects.filter(
                        status__in=['funded', 'completed']
                    )
                    
                    synced_count = 0
                    for campaign in campaigns:
                        if self.ott_service.sync_revenue_data(platform.name, campaign.id):
                            synced_count += 1
                    
                    results[platform.name] = synced_count
                    
                except Exception as e:
                    logger.error(f"Error syncing {platform.name}: {e}")
                    results[platform.name] = 0
            
            return results
            
        except Exception as e:
            logger.error(f"Error syncing OTT revenue: {e}")
            return {}
    
    def process_pending_distributions(self) -> int:
        """Process all pending royalty distributions"""
        try:
            processed_count = 0
            
            # Get campaigns with pending distributions
            campaigns = CampaignModel.objects.filter(
                revenue_entries__status='verified'
            ).distinct()
            
            for campaign in campaigns:
                if self.distribute_royalties(campaign.id):
                    processed_count += 1
            
            return processed_count
            
        except Exception as e:
            logger.error(f"Error processing pending distributions: {e}")
            return 0
