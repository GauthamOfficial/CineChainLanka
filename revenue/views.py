from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import (
    RevenueSource, RevenueEntry, RoyaltyDistribution, 
    InvestorRoyalty, RevenueAnalytics, OTTPlatformIntegration, RevenueWebhook
)
from .serializers import (
    RevenueSourceSerializer, RevenueEntrySerializer, RevenueEntryCreateSerializer,
    RoyaltyDistributionSerializer, InvestorRoyaltySerializer, RevenueAnalyticsSerializer,
    OTTPlatformIntegrationSerializer, RevenueWebhookSerializer, RevenueSummarySerializer,
    InvestorPortfolioSerializer, RevenueChartDataSerializer
)
from .services import RevenueService, RoyaltyDistributionService, AnalyticsService
from campaigns.models import Campaign
from users.models import User


class RevenueSourceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing revenue sources"""
    queryset = RevenueSource.objects.all()
    serializer_class = RevenueSourceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return RevenueSource.objects.all()
        return RevenueSource.objects.filter(is_active=True)


class RevenueEntryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing revenue entries"""
    queryset = RevenueEntry.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RevenueEntryCreateSerializer
        return RevenueEntrySerializer
    
    def get_queryset(self):
        queryset = RevenueEntry.objects.select_related('campaign', 'source', 'verified_by')
        
        # Filter by campaign if provided
        campaign_id = self.request.query_params.get('campaign_id')
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(revenue_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(revenue_date__lte=end_date)
        
        # Non-staff users can only see their own campaign revenues
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(campaign__creator=self.request.user) | 
                Q(campaign__backers=self.request.user)
            )
        
        return queryset.order_by('-revenue_date')
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a revenue entry"""
        revenue_entry = self.get_object()
        
        if not request.user.is_staff:
            return Response(
                {'error': 'Only staff can verify revenue entries'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if revenue_entry.status != 'pending':
            return Response(
                {'error': 'Revenue entry is not pending verification'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        revenue_entry.status = 'verified'
        revenue_entry.verified_by = request.user
        revenue_entry.verified_at = timezone.now()
        revenue_entry.save()
        
        return Response({'message': 'Revenue entry verified successfully'})
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Process a verified revenue entry for royalty distribution"""
        revenue_entry = self.get_object()
        
        if not request.user.is_staff:
            return Response(
                {'error': 'Only staff can process revenue entries'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if revenue_entry.status != 'verified':
            return Response(
                {'error': 'Revenue entry must be verified before processing'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Use the royalty distribution service
            distribution_service = RoyaltyDistributionService()
            distribution = distribution_service.process_royalty_distribution(revenue_entry)
            
            return Response({
                'message': 'Royalty distribution processed successfully',
                'distribution_id': distribution.id
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to process royalty distribution: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RoyaltyDistributionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing royalty distributions"""
    queryset = RoyaltyDistribution.objects.all()
    serializer_class = RoyaltyDistributionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = RoyaltyDistribution.objects.select_related(
            'campaign', 'revenue_entry'
        ).prefetch_related('investor_royalties__investor')
        
        # Filter by campaign if provided
        campaign_id = self.request.query_params.get('campaign_id')
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Non-staff users can only see distributions for their campaigns
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(campaign__creator=self.request.user) | 
                Q(campaign__backers=self.request.user)
            )
        
        return queryset.order_by('-distribution_date')


class InvestorRoyaltyViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for investor royalty management"""
    queryset = InvestorRoyalty.objects.all()
    serializer_class = InvestorRoyaltySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own royalties
        return InvestorRoyalty.objects.filter(
            investor=self.request.user
        ).select_related('distribution__campaign').order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def claim(self, request, pk=None):
        """Claim investor royalty"""
        royalty = self.get_object()
        
        if royalty.investor != request.user:
            return Response(
                {'error': 'You can only claim your own royalties'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if royalty.status != 'claimable':
            return Response(
                {'error': 'Royalty is not available for claiming'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Use the royalty distribution service to claim
            distribution_service = RoyaltyDistributionService()
            tx_hash = distribution_service.claim_investor_royalty(royalty)
            
            royalty.status = 'claimed'
            royalty.claimed_at = timezone.now()
            royalty.blockchain_tx_hash = tx_hash
            royalty.save()
            
            return Response({
                'message': 'Royalty claimed successfully',
                'transaction_hash': tx_hash
            })
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
        # Non-staff users can only see analytics for their campaigns
        if not self.request.user.is_staff:
            return RevenueAnalytics.objects.filter(
                Q(campaign__creator=self.request.user) | 
                Q(campaign__backers=self.request.user)
            )
        return RevenueAnalytics.objects.all()
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get revenue summary for user's campaigns"""
        try:
            analytics_service = AnalyticsService()
            summary_data = analytics_service.get_revenue_summary(request.user)
            
            serializer = RevenueSummarySerializer(summary_data)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Failed to get revenue summary: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def chart_data(self, request):
        """Get revenue chart data"""
        try:
            analytics_service = AnalyticsService()
            chart_data = analytics_service.get_revenue_chart_data(request.user)
            
            serializer = RevenueChartDataSerializer(chart_data)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Failed to get chart data: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InvestorPortfolioViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for investor portfolio analytics"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def portfolio(self, request):
        """Get investor portfolio summary"""
        try:
            analytics_service = AnalyticsService()
            portfolio_data = analytics_service.get_investor_portfolio(request.user)
            
            serializer = InvestorPortfolioSerializer(portfolio_data)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Failed to get portfolio data: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def claimable_royalties(self, request):
        """Get claimable royalties for investor"""
        try:
            analytics_service = AnalyticsService()
            claimable_amount = analytics_service.get_claimable_royalties(request.user)
            
            return Response({
                'claimable_royalties': claimable_amount
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to get claimable royalties: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OTTPlatformIntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for OTT platform integrations"""
    queryset = OTTPlatformIntegration.objects.all()
    serializer_class = OTTPlatformIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return OTTPlatformIntegration.objects.all()
        return OTTPlatformIntegration.objects.filter(is_active=True)


class RevenueWebhookViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for revenue webhooks"""
    queryset = RevenueWebhook.objects.all()
    serializer_class = RevenueWebhookSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return RevenueWebhook.objects.all()
        return RevenueWebhook.objects.filter(
            campaign__creator=self.request.user
        ).order_by('-created_at')
