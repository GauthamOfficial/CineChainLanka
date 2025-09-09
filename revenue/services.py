import logging
from decimal import Decimal
from typing import Dict, List, Optional, Any
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    RevenueEntry, RoyaltyDistribution, InvestorRoyalty, 
    RevenueAnalytics, RevenueSource, Campaign
)
from campaigns.models import Campaign as CampaignModel

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for revenue analytics and reporting"""
    
    def get_creator_analytics(self, creator, period_days: int = 30) -> Dict:
        """Get comprehensive analytics for a creator"""
        try:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=period_days)
            
            # Get creator's campaigns
            campaigns = CampaignModel.objects.filter(creator=creator)
            
            # Get revenue data for the period
            revenue_entries = RevenueEntry.objects.filter(
                campaign__in=campaigns,
                revenue_date__range=[start_date, end_date],
                status__in=['verified', 'processed']
            )
            
            # Calculate metrics
            total_revenue = revenue_entries.aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0')
            
            total_campaigns = campaigns.count()
            active_campaigns = campaigns.filter(status='active').count()
            completed_campaigns = campaigns.filter(status__in=['funded', 'completed']).count()
            
            # Get campaign performance data
            campaign_metrics = []
            for campaign in campaigns:
                campaign_revenue = revenue_entries.filter(campaign=campaign).aggregate(
                    total=Sum('amount')
                )['total'] or Decimal('0')
                
                # Calculate ROI
                roi = Decimal('0')
                if campaign.funding_goal > 0:
                    roi = (campaign_revenue / campaign.funding_goal) * 100
                
                campaign_metrics.append({
                    'id': campaign.id,
                    'title': campaign.title,
                    'total_raised': float(campaign.current_funding),
                    'total_revenue': float(campaign_revenue),
                    'backer_count': campaign.backer_count,
                    'view_count': getattr(campaign, 'view_count', 0),
                    'like_count': getattr(campaign, 'like_count', 0),
                    'share_count': getattr(campaign, 'share_count', 0),
                    'roi': float(roi),
                    'status': campaign.status
                })
            
            # Generate revenue chart data
            revenue_chart = self._generate_revenue_chart_data(revenue_entries, period_days)
            
            # Generate source breakdown
            source_breakdown = self._generate_source_breakdown(revenue_entries)
            
            return {
                'campaigns': campaign_metrics,
                'revenueChart': revenue_chart,
                'sourceBreakdown': source_breakdown,
                'summary': {
                    'total_revenue': float(total_revenue),
                    'total_campaigns': total_campaigns,
                    'active_campaigns': active_campaigns,
                    'completed_campaigns': completed_campaigns,
                    'average_roi': float(sum(c['roi'] for c in campaign_metrics) / max(len(campaign_metrics), 1))
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting creator analytics: {e}")
            return {}
    
    def get_investor_portfolio(self, investor) -> Dict:
        """Get comprehensive portfolio analytics for an investor"""
        try:
            # Get investor's royalty claims
            royalty_claims = InvestorRoyalty.objects.filter(investor=investor)
            
            # Calculate portfolio metrics
            total_invested = royalty_claims.aggregate(
                total=Sum('contribution_amount')
            )['total'] or Decimal('0')
            
            total_earned = royalty_claims.aggregate(
                total=Sum('royalty_amount')
            )['total'] or Decimal('0')
            
            claimable_royalties = royalty_claims.filter(
                status='claimable'
            ).aggregate(
                total=Sum('royalty_amount')
            )['total'] or Decimal('0')
            
            claimed_royalties = royalty_claims.filter(
                status='claimed'
            ).aggregate(
                total=Sum('royalty_amount')
            )['total'] or Decimal('0')
            
            # Calculate overall ROI
            overall_roi = Decimal('0')
            if total_invested > 0:
                overall_roi = (total_earned / total_invested) * 100
            
            # Get investment breakdown by campaign
            investment_breakdown = []
            for claim in royalty_claims:
                distribution = claim.distribution
                campaign = distribution.campaign
                
                investment_roi = Decimal('0')
                if claim.contribution_amount > 0:
                    investment_roi = (claim.royalty_amount / claim.contribution_amount) * 100
                
                investment_breakdown.append({
                    'campaign_id': campaign.id,
                    'campaign_title': campaign.title,
                    'nft_id': claim.nft_id,
                    'contribution_amount': float(claim.contribution_amount),
                    'royalty_earned': float(claim.royalty_amount),
                    'roi_percentage': float(investment_roi),
                    'status': claim.status,
                    'investment_date': claim.created_at.isoformat()
                })
            
            # Generate royalty trends
            royalty_trends = self._generate_royalty_trends(royalty_claims)
            
            return {
                'total_invested': float(total_invested),
                'total_earned': float(total_earned),
                'claimable_royalties': float(claimable_royalties),
                'claimed_royalties': float(claimed_royalties),
                'overall_roi': float(overall_roi),
                'investment_count': royalty_claims.count(),
                'investment_breakdown': investment_breakdown,
                'royalty_trends': royalty_trends
            }
            
        except Exception as e:
            logger.error(f"Error getting investor portfolio: {e}")
            return {}
    
    def get_revenue_summary(self, campaign_id: int = None, period_days: int = 30) -> Dict:
        """Get revenue summary for a campaign or all campaigns"""
        try:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=period_days)
            
            # Filter by campaign if specified
            filter_kwargs = {
                'revenue_date__range': [start_date, end_date],
                'status__in': ['verified', 'processed']
            }
            
            if campaign_id:
                filter_kwargs['campaign_id'] = campaign_id
            
            revenue_entries = RevenueEntry.objects.filter(**filter_kwargs)
            
            # Calculate totals
            total_revenue = revenue_entries.aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0')
            
            # Revenue by source
            revenue_by_source = revenue_entries.values('source__name').annotate(
                total=Sum('amount'),
                count=Count('id')
            ).order_by('-total')
            
            # Revenue by campaign
            revenue_by_campaign = revenue_entries.values(
                'campaign__title', 'campaign__id'
            ).annotate(
                total=Sum('amount'),
                count=Count('id')
            ).order_by('-total')
            
            # Daily revenue trend
            daily_revenue = []
            for i in range(period_days):
                date = start_date + timedelta(days=i)
                day_revenue = revenue_entries.filter(
                    revenue_date=date
                ).aggregate(
                    total=Sum('amount')
                )['total'] or Decimal('0')
                
                daily_revenue.append({
                    'date': date.isoformat(),
                    'revenue': float(day_revenue)
                })
            
            return {
                'total_revenue': float(total_revenue),
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': period_days
                },
                'revenue_by_source': list(revenue_by_source),
                'revenue_by_campaign': list(revenue_by_campaign),
                'daily_revenue': daily_revenue
            }
            
        except Exception as e:
            logger.error(f"Error getting revenue summary: {e}")
            return {}
    
    def _generate_revenue_chart_data(self, revenue_entries, period_days: int) -> Dict:
        """Generate chart data for revenue visualization"""
        try:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=period_days)
            
            # Generate daily data
            labels = []
            revenue_data = []
            creator_royalties = []
            investor_royalties = []
            platform_fees = []
            
            for i in range(period_days):
                date = start_date + timedelta(days=i)
                labels.append(date.strftime('%Y-%m-%d'))
                
                day_entries = revenue_entries.filter(revenue_date=date)
                day_revenue = day_entries.aggregate(
                    total=Sum('amount')
                )['total'] or Decimal('0')
                
                # Calculate distribution (simplified)
                creator_amount = day_revenue * Decimal('0.30')
                platform_amount = day_revenue * Decimal('0.05')
                investor_amount = day_revenue * Decimal('0.65')
                
                revenue_data.append(float(day_revenue))
                creator_royalties.append(float(creator_amount))
                investor_royalties.append(float(investor_amount))
                platform_fees.append(float(platform_amount))
            
            return {
                'labels': labels,
                'revenue': revenue_data,
                'creatorRoyalties': creator_royalties,
                'investorRoyalties': investor_royalties,
                'platformFees': platform_fees
            }
            
        except Exception as e:
            logger.error(f"Error generating revenue chart data: {e}")
            return {'labels': [], 'revenue': [], 'creatorRoyalties': [], 'investorRoyalties': [], 'platformFees': []}
    
    def _generate_source_breakdown(self, revenue_entries) -> List[Dict]:
        """Generate revenue source breakdown data"""
        try:
            source_data = revenue_entries.values('source__name').annotate(
                amount=Sum('amount'),
                count=Count('id')
            ).order_by('-amount')
            
            total_amount = sum(item['amount'] for item in source_data)
            
            breakdown = []
            for item in source_data:
                percentage = 0
                if total_amount > 0:
                    percentage = (item['amount'] / total_amount) * 100
                
                breakdown.append({
                    'source': item['source__name'],
                    'amount': float(item['amount']),
                    'percentage': float(percentage),
                    'count': item['count']
                })
            
            return breakdown
            
        except Exception as e:
            logger.error(f"Error generating source breakdown: {e}")
            return []
    
    def _generate_royalty_trends(self, royalty_claims) -> Dict:
        """Generate royalty trends for investor portfolio"""
        try:
            # Get last 30 days of royalty data
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
            
            labels = []
            royalty_data = []
            cumulative_data = []
            
            cumulative_total = Decimal('0')
            
            for i in range(30):
                date = start_date + timedelta(days=i)
                labels.append(date.strftime('%Y-%m-%d'))
                
                # Get royalties for this date
                day_royalties = royalty_claims.filter(
                    distribution__distribution_date__date=date
                ).aggregate(
                    total=Sum('royalty_amount')
                )['total'] or Decimal('0')
                
                cumulative_total += day_royalties
                
                royalty_data.append(float(day_royalties))
                cumulative_data.append(float(cumulative_total))
            
            return {
                'labels': labels,
                'royalty_data': royalty_data,
                'cumulative_data': cumulative_data
            }
            
        except Exception as e:
            logger.error(f"Error generating royalty trends: {e}")
            return {'labels': [], 'royalty_data': [], 'cumulative_data': []}
    
    def update_campaign_analytics(self, campaign_id: int) -> bool:
        """Update analytics data for a specific campaign"""
        try:
            campaign = CampaignModel.objects.get(id=campaign_id)
            
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
            
            logger.info(f"Analytics updated for campaign {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating campaign analytics: {e}")
            return False