from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import (
    RevenueEntry, RoyaltyDistribution, InvestorRoyalty, 
    RevenueAnalytics, RevenueSource, Campaign
)
from .services import AnalyticsService
from .serializers import (
    RevenueEntrySerializer, RoyaltyDistributionSerializer, 
    InvestorRoyaltySerializer, RevenueAnalyticsSerializer
)

class RevenueEntryViewSet(viewsets.ModelViewSet):
    """ViewSet for revenue entries"""
    queryset = RevenueEntry.objects.all()
    serializer_class = RevenueEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see revenue entries for their own campaigns
        return RevenueEntry.objects.filter(
            campaign__creator=self.request.user
        ).select_related('campaign', 'source')
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get revenue analytics for creator"""
        try:
            analytics_service = AnalyticsService()
            period_days = int(request.query_params.get('period', 30))
            
            analytics_data = analytics_service.get_creator_analytics(
                request.user, period_days
            )
            
            return Response(analytics_data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get analytics: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get revenue summary"""
        try:
            analytics_service = AnalyticsService()
            campaign_id = request.query_params.get('campaign_id')
            period_days = int(request.query_params.get('period', 30))
            
            summary_data = analytics_service.get_revenue_summary(
                campaign_id, period_days
            )
            
            return Response(summary_data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get summary: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RoyaltyDistributionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for royalty distributions"""
    queryset = RoyaltyDistribution.objects.all()
    serializer_class = RoyaltyDistributionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see distributions for their own campaigns
        return RoyaltyDistribution.objects.filter(
            campaign__creator=self.request.user
        ).select_related('campaign', 'revenue_entry')
    
    @action(detail=True, methods=['post'])
    def distribute(self, request, pk=None):
        """Trigger royalty distribution for a campaign"""
        try:
            distribution = self.get_object()
            
            if distribution.status != 'pending':
                return Response(
                    {'error': 'Distribution is not pending'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update status to processing
            distribution.status = 'processing'
            distribution.save()
            
            # Here you would integrate with the blockchain service
            # For now, we'll simulate success
            distribution.status = 'completed'
            distribution.blockchain_tx_hash = f"0x{timezone.now().timestamp():.0f}"
            distribution.save()
            
            return Response({'status': 'Distribution completed'})
            
        except Exception as e:
            return Response(
                {'error': f'Failed to distribute royalties: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InvestorRoyaltyViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for investor royalties"""
    queryset = InvestorRoyalty.objects.all()
    serializer_class = InvestorRoyaltySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own royalties
        return InvestorRoyalty.objects.filter(
            investor=self.request.user
        ).select_related('distribution', 'distribution__campaign')
    
    @action(detail=False, methods=['get'])
    def portfolio(self, request):
        """Get investor portfolio analytics"""
        try:
            analytics_service = AnalyticsService()
            portfolio_data = analytics_service.get_investor_portfolio(request.user)
            
            return Response(portfolio_data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get portfolio: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def claim(self, request, pk=None):
        """Claim investor royalties"""
        try:
            royalty = self.get_object()
            
            if royalty.status != 'claimable':
                return Response(
                    {'error': 'Royalty is not claimable'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Here you would integrate with the blockchain service
            # For now, we'll simulate success
            royalty.status = 'claimed'
            royalty.claimed_at = timezone.now()
            royalty.blockchain_tx_hash = f"0x{timezone.now().timestamp():.0f}"
            royalty.save()
            
            return Response({'status': 'Royalty claimed successfully'})
            
        except Exception as e:
            return Response(
                {'error': f'Failed to claim royalty: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RevenueAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for revenue analytics"""
    queryset = RevenueAnalytics.objects.all()
    serializer_class = RevenueAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see analytics for their own campaigns
        return RevenueAnalytics.objects.filter(
            campaign__creator=self.request.user
        ).select_related('campaign')
    
    @action(detail=False, methods=['get'])
    def creator_analytics(self, request):
        """Get creator analytics data"""
        try:
            analytics_service = AnalyticsService()
            period_days = int(request.query_params.get('period', 30))
            
            analytics_data = analytics_service.get_creator_analytics(
                request.user, period_days
            )
            
            return Response(analytics_data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get creator analytics: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def investor_analytics(self, request):
        """Get investor analytics data"""
        try:
            analytics_service = AnalyticsService()
            portfolio_data = analytics_service.get_investor_portfolio(request.user)
            
            return Response(portfolio_data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get investor analytics: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )