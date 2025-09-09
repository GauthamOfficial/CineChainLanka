from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Q, F, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from campaigns.models import Campaign
from revenue.models import RevenueEntry, RoyaltyDistribution, InvestorRoyalty
from revenue.services import AnalyticsService
from .serializers import (
    CreatorAnalyticsSerializer, InvestorPortfolioSerializer, 
    RevenueSummarySerializer, RevenueChartDataSerializer
)


class CreatorAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for creator analytics"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def creator_analytics(self, request):
        """Get creator analytics data"""
        try:
            analytics_service = AnalyticsService()
            
            # Get user's campaigns
            campaigns = Campaign.objects.filter(creator=request.user)
            
            # Calculate campaign metrics
            campaign_metrics = []
            for campaign in campaigns:
                # Get funding data
                total_funding = campaign.funding_goal
                current_funding = campaign.current_funding
                funding_progress = (current_funding / total_funding * 100) if total_funding > 0 else 0
                
                # Get engagement data (mock data for now)
                view_count = 100 + (campaign.id * 10)  # Mock data
                like_count = 20 + (campaign.id * 5)    # Mock data
                share_count = 5 + (campaign.id * 2)    # Mock data
                
                # Calculate conversion rate (mock)
                conversion_rate = min(15.0 + (campaign.id * 2), 25.0)
                
                # Calculate average contribution
                avg_contribution = current_funding / max(campaign.backer_count, 1)
                
                campaign_metrics.append({
                    'campaign_id': campaign.id,
                    'title': campaign.title,
                    'status': campaign.status,
                    'total_funding': float(current_funding),
                    'funding_goal': float(total_funding),
                    'backer_count': campaign.backer_count,
                    'view_count': view_count,
                    'like_count': like_count,
                    'share_count': share_count,
                    'created_at': campaign.created_at.isoformat(),
                    'end_date': campaign.end_date.isoformat(),
                    'funding_progress': float(funding_progress),
                    'days_remaining': max(0, (campaign.end_date.date() - timezone.now().date()).days),
                    'avg_contribution': float(avg_contribution),
                    'conversion_rate': conversion_rate
                })
            
            # Calculate summary data
            total_campaigns = campaigns.count()
            active_campaigns = campaigns.filter(status='active').count()
            completed_campaigns = campaigns.filter(status__in=['funded', 'completed']).count()
            from decimal import Decimal
            total_funding_raised = float(sum(c.current_funding for c in campaigns))
            total_backers = sum(c.backer_count for c in campaigns)
            avg_campaign_performance = float(sum(c['funding_progress'] for c in campaign_metrics) / max(len(campaign_metrics), 1))
            
            # Get top performing campaigns
            top_performing = sorted(campaign_metrics, key=lambda x: x['funding_progress'], reverse=True)[:5]
            
            # Get recent campaigns
            recent_campaigns = sorted(campaign_metrics, key=lambda x: x['created_at'], reverse=True)[:10]
            
            # Generate funding trends (mock data)
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
            funding_trends = {
                'labels': [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)],
                'funding_data': [1000 + (i * 100) for i in range(30)],
                'backer_data': [10 + (i * 2) for i in range(30)]
            }
            
            # Revenue forecast (mock data)
            revenue_forecast = {
                'next_month': 5000.0,
                'next_quarter': 15000.0,
                'next_year': 60000.0
            }
            
            analytics_data = {
                'total_campaigns': total_campaigns,
                'active_campaigns': active_campaigns,
                'completed_campaigns': completed_campaigns,
                'total_funding_raised': total_funding_raised,
                'total_backers': total_backers,
                'avg_campaign_performance': avg_campaign_performance,
                'top_performing_campaigns': top_performing,
                'recent_campaigns': recent_campaigns,
                'funding_trends': funding_trends,
                'revenue_forecast': revenue_forecast
            }
            
            serializer = CreatorAnalyticsSerializer(analytics_data)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get creator analytics: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InvestorAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for investor analytics"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def portfolio(self, request):
        """Get investor portfolio data"""
        try:
            analytics_service = AnalyticsService()
            portfolio_data = analytics_service.get_investor_portfolio(request.user)
            
            # Get user's investments
            user_royalties = InvestorRoyalty.objects.filter(investor=request.user)
            
            # Get investment details
            investments = []
            for royalty in user_royalties:
                distribution = royalty.distribution
                campaign = distribution.campaign
                
                # Calculate ROI for this investment
                roi_percentage = 0
                if royalty.contribution_amount > 0:
                    roi_percentage = (royalty.royalty_amount / royalty.contribution_amount) * 100
                
                investments.append({
                    'campaign_id': campaign.id,
                    'campaign_title': campaign.title,
                    'nft_id': royalty.nft_id,
                    'contribution_amount': float(royalty.contribution_amount),
                    'share_percentage': float(royalty.share_percentage),
                    'royalty_earned': float(royalty.royalty_amount),
                    'royalty_claimable': float(royalty.royalty_amount) if royalty.status == 'claimable' else 0,
                    'royalty_claimed': float(royalty.royalty_amount) if royalty.status == 'claimed' else 0,
                    'status': royalty.status,
                    'investment_date': royalty.created_at.isoformat(),
                    'last_royalty_date': distribution.distribution_date.isoformat() if distribution.distribution_date else None
                })
            
            # Generate royalty trends (mock data)
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
            royalty_trends = {
                'labels': [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)],
                'royalty_data': [50 + (i * 10) for i in range(30)],
                'cumulative_data': [sum(50 + (j * 10) for j in range(i+1)) for i in range(30)]
            }
            
            # Monthly earnings (mock data)
            monthly_earnings = [
                {'month': 'January 2024', 'earnings': 1500.0, 'investments': 3},
                {'month': 'February 2024', 'earnings': 2200.0, 'investments': 2},
                {'month': 'March 2024', 'earnings': 1800.0, 'investments': 4},
            ]
            
            # Campaign performance
            campaign_performance = []
            for investment in investments:
                campaign_performance.append({
                    'campaign_id': investment['campaign_id'],
                    'title': investment['campaign_title'],
                    'roi_percentage': investment['royalty_earned'] / max(investment['contribution_amount'], 1) * 100,
                    'total_earned': investment['royalty_earned'],
                    'status': investment['status']
                })
            
            # Get best and worst performing campaigns
            if campaign_performance:
                best_campaign = max(campaign_performance, key=lambda x: x['roi_percentage'])
                worst_campaign = min(campaign_performance, key=lambda x: x['roi_percentage'])
            else:
                best_campaign = {'campaign_id': 0, 'title': 'No investments', 'roi_percentage': 0}
                worst_campaign = {'campaign_id': 0, 'title': 'No investments', 'roi_percentage': 0}
            
            portfolio_data.update({
                'investments': investments,
                'royalty_trends': royalty_trends,
                'monthly_earnings': monthly_earnings,
                'campaign_performance': campaign_performance,
                'best_performing_campaign': best_campaign,
                'worst_performing_campaign': worst_campaign
            })
            
            serializer = InvestorPortfolioSerializer(portfolio_data)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get investor portfolio: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
