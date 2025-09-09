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
            period_days = int(request.query_params.get('period', 30))
            
            analytics_data = analytics_service.get_creator_analytics(
                request.user, period_days
            )
            
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
            
            serializer = InvestorPortfolioSerializer(portfolio_data)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to get investor portfolio: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
