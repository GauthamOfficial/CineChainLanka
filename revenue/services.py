import logging
from decimal import Decimal
from typing import Dict, List, Optional, Any
from django.db.models import Sum, Count, Q, F, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    RevenueSource, RevenueEntry, RoyaltyDistribution, 
    InvestorRoyalty, RevenueAnalytics, Campaign
)
from blockchain.services import Web3Service, ContractService
from blockchain.models import BlockchainNetwork, SmartContract
from campaigns.models import Campaign

logger = logging.getLogger(__name__)


class RevenueService:
    """Service for revenue management"""
    
    def __init__(self):
        self.revenue_sources = RevenueSource.objects.filter(is_active=True)
    
    def create_revenue_entry(
        self,
        campaign_id: int,
        source_id: int,
        amount: Decimal,
        currency: str,
        description: str,
        revenue_date: datetime,
        verification_document=None
    ) -> RevenueEntry:
        """Create a new revenue entry"""
        try:
            campaign = Campaign.objects.get(id=campaign_id)
            source = RevenueSource.objects.get(id=source_id)
            
            revenue_entry = RevenueEntry.objects.create(
                campaign=campaign,
                source=source,
                amount=amount,
                currency=currency,
                description=description,
                revenue_date=revenue_date,
                verification_document=verification_document
            )
            
            logger.info(f"Revenue entry created: {revenue_entry.id}")
            return revenue_entry
            
        except Exception as e:
            logger.error(f"Error creating revenue entry: {e}")
            raise
    
    def verify_revenue_entry(self, revenue_entry_id: int, verified_by_id: int) -> bool:
        """Verify a revenue entry"""
        try:
            revenue_entry = RevenueEntry.objects.get(id=revenue_entry_id)
            revenue_entry.status = 'verified'
            revenue_entry.verified_by_id = verified_by_id
            revenue_entry.verified_at = timezone.now()
            revenue_entry.save()
            
            logger.info(f"Revenue entry verified: {revenue_entry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying revenue entry: {e}")
            return False
    
    def get_campaign_revenue_summary(self, campaign_id: int) -> Dict:
        """Get revenue summary for a campaign"""
        try:
            campaign = Campaign.objects.get(id=campaign_id)
            
            # Get total revenue
            total_revenue = RevenueEntry.objects.filter(
                campaign=campaign,
                status__in=['verified', 'processed']
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            # Get revenue by source
            revenue_by_source = RevenueEntry.objects.filter(
                campaign=campaign,
                status__in=['verified', 'processed']
            ).values('source__name').annotate(
                total=Sum('amount'),
                count=Count('id')
            )
            
            # Get recent revenue entries
            recent_entries = RevenueEntry.objects.filter(
                campaign=campaign
            ).order_by('-revenue_date')[:10]
            
            return {
                'campaign_id': campaign_id,
                'campaign_title': campaign.title,
                'total_revenue': total_revenue,
                'revenue_by_source': list(revenue_by_source),
                'recent_entries': [
                    {
                        'id': entry.id,
                        'amount': entry.amount,
                        'currency': entry.currency,
                        'source': entry.source.name,
                        'revenue_date': entry.revenue_date,
                        'status': entry.status
                    }
                    for entry in recent_entries
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting campaign revenue summary: {e}")
            return {}
    
    def get_revenue_trends(self, campaign_id: int, days: int = 30) -> Dict:
        """Get revenue trends for a campaign"""
        try:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)
            
            # Get daily revenue data
            daily_revenue = RevenueEntry.objects.filter(
                campaign_id=campaign_id,
                revenue_date__range=[start_date, end_date],
                status__in=['verified', 'processed']
            ).extra(
                select={'day': 'date(revenue_date)'}
            ).values('day').annotate(
                total=Sum('amount'),
                count=Count('id')
            ).order_by('day')
            
            # Get source breakdown
            source_breakdown = RevenueEntry.objects.filter(
                campaign_id=campaign_id,
                revenue_date__range=[start_date, end_date],
                status__in=['verified', 'processed']
            ).values('source__name').annotate(
                total=Sum('amount'),
                percentage=F('total') * 100.0 / Sum('amount')
            )
            
            return {
                'daily_revenue': list(daily_revenue),
                'source_breakdown': list(source_breakdown),
                'period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'days': days
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting revenue trends: {e}")
            return {}


class RoyaltyDistributionService:
    """Service for royalty distribution management"""
    
    def __init__(self):
        self.royalty_contract = self._get_royalty_contract()
    
    def _get_royalty_contract(self) -> Optional[SmartContract]:
        """Get the royalty distribution contract"""
        try:
            return SmartContract.objects.filter(
                name='RoyaltyDistribution',
                is_active=True
            ).first()
        except Exception as e:
            logger.error(f"Error getting royalty contract: {e}")
            return None
    
    def process_royalty_distribution(self, revenue_entry: RevenueEntry) -> RoyaltyDistribution:
        """Process royalty distribution for a revenue entry"""
        try:
            campaign = revenue_entry.campaign
            source = revenue_entry.source
            
            # Calculate distribution amounts
            platform_amount = revenue_entry.amount * (source.platform_fee_percentage / 100)
            creator_amount = revenue_entry.amount * (source.creator_fee_percentage / 100)
            investor_amount = revenue_entry.amount * (source.investor_fee_percentage / 100)
            
            # Create distribution record
            distribution = RoyaltyDistribution.objects.create(
                campaign=campaign,
                revenue_entry=revenue_entry,
                distribution_date=timezone.now(),
                creator_amount=creator_amount,
                platform_amount=platform_amount,
                total_investor_amount=investor_amount,
                status='processing'
            )
            
            # Process investor distributions
            self._process_investor_distributions(distribution, campaign, investor_amount)
            
            # Update revenue entry status
            revenue_entry.status = 'processed'
            revenue_entry.save()
            
            # Update distribution status
            distribution.status = 'completed'
            distribution.save()
            
            # Update analytics
            self._update_revenue_analytics(campaign)
            
            logger.info(f"Royalty distribution processed: {distribution.id}")
            return distribution
            
        except Exception as e:
            logger.error(f"Error processing royalty distribution: {e}")
            if 'distribution' in locals():
                distribution.status = 'failed'
                distribution.error_message = str(e)
                distribution.save()
            raise
    
    def _process_investor_distributions(
        self, 
        distribution: RoyaltyDistribution, 
        campaign: Campaign, 
        total_investor_amount: Decimal
    ) -> None:
        """Process individual investor distributions"""
        try:
            # Get all NFTs for this campaign (this would need to be implemented)
            # For now, we'll create a placeholder
            nft_contributions = self._get_campaign_nft_contributions(campaign)
            
            if not nft_contributions:
                logger.warning(f"No NFT contributions found for campaign {campaign.id}")
                return
            
            total_contributions = sum(contrib['amount'] for contrib in nft_contributions)
            
            for nft_contrib in nft_contributions:
                if total_contributions > 0:
                    share_percentage = (nft_contrib['amount'] / total_contributions) * 100
                    royalty_amount = total_investor_amount * (share_percentage / 100)
                    
                    InvestorRoyalty.objects.create(
                        distribution=distribution,
                        investor_id=nft_contrib['investor_id'],
                        nft_id=nft_contrib['nft_id'],
                        contribution_amount=nft_contrib['amount'],
                        share_percentage=share_percentage,
                        royalty_amount=royalty_amount,
                        status='claimable'
                    )
            
        except Exception as e:
            logger.error(f"Error processing investor distributions: {e}")
            raise
    
    def _get_campaign_nft_contributions(self, campaign: Campaign) -> List[Dict]:
        """Get NFT contributions for a campaign"""
        # This would need to be implemented to get actual NFT data
        # For now, returning empty list
        return []
    
    def claim_investor_royalty(self, royalty: InvestorRoyalty) -> str:
        """Claim investor royalty on blockchain"""
        try:
            if not self.royalty_contract:
                raise Exception("Royalty contract not available")
            
            # Get network and Web3 service
            network = self.royalty_contract.network
            web3_service = Web3Service(network)
            contract_service = ContractService(self.royalty_contract, web3_service)
            
            # Call claim function on smart contract
            tx_hash = contract_service.send_function(
                'claimInvestorRoyalty',
                royalty.distribution.id,
                royalty.nft_id
            )
            
            logger.info(f"Investor royalty claimed: {royalty.id}, TX: {tx_hash}")
            return tx_hash
            
        except Exception as e:
            logger.error(f"Error claiming investor royalty: {e}")
            raise
    
    def _update_revenue_analytics(self, campaign: Campaign) -> None:
        """Update revenue analytics for a campaign"""
        try:
            analytics, created = RevenueAnalytics.objects.get_or_create(campaign=campaign)
            
            # Calculate totals
            total_revenue = RevenueEntry.objects.filter(
                campaign=campaign,
                status='processed'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            total_creator_royalties = RoyaltyDistribution.objects.filter(
                campaign=campaign,
                status='completed'
            ).aggregate(total=Sum('creator_amount'))['total'] or Decimal('0')
            
            total_platform_fees = RoyaltyDistribution.objects.filter(
                campaign=campaign,
                status='completed'
            ).aggregate(total=Sum('platform_amount'))['total'] or Decimal('0')
            
            total_investor_royalties = RoyaltyDistribution.objects.filter(
                campaign=campaign,
                status='completed'
            ).aggregate(total=Sum('total_investor_amount'))['total'] or Decimal('0')
            
            total_distributions = RoyaltyDistribution.objects.filter(
                campaign=campaign,
                status='completed'
            ).count()
            
            last_distribution = RoyaltyDistribution.objects.filter(
                campaign=campaign,
                status='completed'
            ).order_by('-distribution_date').first()
            
            # Update analytics
            analytics.total_revenue = total_revenue
            analytics.total_creator_royalties = total_creator_royalties
            analytics.total_platform_fees = total_platform_fees
            analytics.total_investor_royalties = total_investor_royalties
            analytics.total_distributions = total_distributions
            analytics.last_distribution_date = last_distribution.distribution_date if last_distribution else None
            analytics.save()
            
        except Exception as e:
            logger.error(f"Error updating revenue analytics: {e}")


class AnalyticsService:
    """Service for revenue analytics"""
    
    def get_revenue_summary(self, user) -> Dict:
        """Get revenue summary for user's campaigns"""
        try:
            # Get campaigns where user is creator or backer
            from payments.models import Transaction
            backer_campaign_ids = Transaction.objects.filter(
                user=user,
                campaign__isnull=False
            ).values_list('campaign_id', flat=True)
            
            campaigns = Campaign.objects.filter(
                Q(creator=user) | Q(id__in=backer_campaign_ids)
            ).distinct()
            
            # Calculate totals
            total_revenue = RevenueEntry.objects.filter(
                campaign__in=campaigns,
                status='processed'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            total_creator_royalties = RoyaltyDistribution.objects.filter(
                campaign__in=campaigns,
                campaign__creator=user,
                status='completed'
            ).aggregate(total=Sum('creator_amount'))['total'] or Decimal('0')
            
            total_platform_fees = RoyaltyDistribution.objects.filter(
                campaign__in=campaigns,
                status='completed'
            ).aggregate(total=Sum('platform_amount'))['total'] or Decimal('0')
            
            total_investor_royalties = RoyaltyDistribution.objects.filter(
                campaign__in=campaigns,
                status='completed'
            ).aggregate(total=Sum('total_investor_amount'))['total'] or Decimal('0')
            
            total_distributions = RoyaltyDistribution.objects.filter(
                campaign__in=campaigns,
                status='completed'
            ).count()
            
            # Get pending royalties for investor
            pending_royalties = InvestorRoyalty.objects.filter(
                investor=user,
                status='claimable'
            ).aggregate(total=Sum('royalty_amount'))['total'] or Decimal('0')
            
            last_distribution = RoyaltyDistribution.objects.filter(
                campaign__in=campaigns,
                status='completed'
            ).order_by('-distribution_date').first()
            
            return {
                'total_revenue': total_revenue,
                'total_creator_royalties': total_creator_royalties,
                'total_platform_fees': total_platform_fees,
                'total_investor_royalties': total_investor_royalties,
                'total_distributions': total_distributions,
                'pending_royalties': pending_royalties,
                'last_distribution_date': last_distribution.distribution_date if last_distribution else None
            }
            
        except Exception as e:
            logger.error(f"Error getting revenue summary: {e}")
            return {}
    
    def get_revenue_chart_data(self, user, days: int = 30) -> Dict:
        """Get revenue chart data"""
        try:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)
            
            from payments.models import Transaction
            backer_campaign_ids = Transaction.objects.filter(
                user=user,
                campaign__isnull=False
            ).values_list('campaign_id', flat=True)
            
            campaigns = Campaign.objects.filter(
                Q(creator=user) | Q(id__in=backer_campaign_ids)
            ).distinct()
            
            # Get daily revenue data
            daily_data = RevenueEntry.objects.filter(
                campaign__in=campaigns,
                revenue_date__range=[start_date, end_date],
                status='processed'
            ).extra(
                select={'day': 'date(revenue_date)'}
            ).values('day').annotate(
                revenue=Sum('amount'),
                creator_royalties=Sum('amount') * F('source__creator_fee_percentage') / 100,
                investor_royalties=Sum('amount') * F('source__investor_fee_percentage') / 100,
                platform_fees=Sum('amount') * F('source__platform_fee_percentage') / 100
            ).order_by('day')
            
            # Format data for charts
            labels = []
            revenue_data = []
            creator_royalties_data = []
            investor_royalties_data = []
            platform_fees_data = []
            
            for item in daily_data:
                labels.append(item['day'].strftime('%Y-%m-%d'))
                revenue_data.append(float(item['revenue'] or 0))
                creator_royalties_data.append(float(item['creator_royalties'] or 0))
                investor_royalties_data.append(float(item['investor_royalties'] or 0))
                platform_fees_data.append(float(item['platform_fees'] or 0))
            
            return {
                'labels': labels,
                'revenue_data': revenue_data,
                'creator_royalties_data': creator_royalties_data,
                'investor_royalties_data': investor_royalties_data,
                'platform_fees_data': platform_fees_data
            }
            
        except Exception as e:
            logger.error(f"Error getting chart data: {e}")
            return {}
    
    def get_investor_portfolio(self, user) -> Dict:
        """Get investor portfolio summary"""
        try:
            # Get user's NFT contributions
            user_royalties = InvestorRoyalty.objects.filter(investor=user)
            
            # Calculate totals
            total_invested = user_royalties.aggregate(
                total=Sum('contribution_amount')
            )['total'] or Decimal('0')
            
            total_royalties_earned = user_royalties.aggregate(
                total=Sum('royalty_amount')
            )['total'] or Decimal('0')
            
            total_royalties_claimable = user_royalties.filter(
                status='claimable'
            ).aggregate(total=Sum('royalty_amount'))['total'] or Decimal('0')
            
            total_royalties_claimed = user_royalties.filter(
                status='claimed'
            ).aggregate(total=Sum('royalty_amount'))['total'] or Decimal('0')
            
            # Calculate ROI
            roi_percentage = 0
            if total_invested > 0:
                roi_percentage = (total_royalties_earned / total_invested) * 100
            
            # Get campaign counts
            active_campaigns = Campaign.objects.filter(
                backers=user,
                status='active'
            ).count()
            
            completed_campaigns = Campaign.objects.filter(
                backers=user,
                status__in=['funded', 'completed']
            ).count()
            
            total_nfts = user_royalties.values('nft_id').distinct().count()
            
            return {
                'total_invested': total_invested,
                'total_royalties_earned': total_royalties_earned,
                'total_royalties_claimable': total_royalties_claimable,
                'total_royalties_claimed': total_royalties_claimed,
                'roi_percentage': roi_percentage,
                'active_campaigns': active_campaigns,
                'completed_campaigns': completed_campaigns,
                'total_nfts': total_nfts
            }
            
        except Exception as e:
            logger.error(f"Error getting investor portfolio: {e}")
            return {}
    
    def get_claimable_royalties(self, user) -> Decimal:
        """Get total claimable royalties for user"""
        try:
            return InvestorRoyalty.objects.filter(
                investor=user,
                status='claimable'
            ).aggregate(total=Sum('royalty_amount'))['total'] or Decimal('0')
        except Exception as e:
            logger.error(f"Error getting claimable royalties: {e}")
            return Decimal('0')
