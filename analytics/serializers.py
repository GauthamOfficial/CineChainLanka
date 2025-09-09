from rest_framework import serializers
from decimal import Decimal


class CreatorAnalyticsSerializer(serializers.Serializer):
    """Serializer for creator analytics data"""
    
    total_campaigns = serializers.IntegerField()
    active_campaigns = serializers.IntegerField()
    completed_campaigns = serializers.IntegerField()
    total_funding_raised = serializers.DecimalField(max_digits=20, decimal_places=6)
    total_backers = serializers.IntegerField()
    avg_campaign_performance = serializers.FloatField()
    
    # Campaign metrics
    top_performing_campaigns = serializers.ListField()
    recent_campaigns = serializers.ListField()
    
    # Chart data
    funding_trends = serializers.DictField()
    revenue_forecast = serializers.DictField()


class CampaignMetricsSerializer(serializers.Serializer):
    """Serializer for individual campaign metrics"""
    
    campaign_id = serializers.IntegerField()
    title = serializers.CharField()
    status = serializers.CharField()
    total_funding = serializers.DecimalField(max_digits=20, decimal_places=6)
    funding_goal = serializers.DecimalField(max_digits=20, decimal_places=6)
    backer_count = serializers.IntegerField()
    view_count = serializers.IntegerField()
    like_count = serializers.IntegerField()
    share_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    funding_progress = serializers.FloatField()
    days_remaining = serializers.IntegerField()
    avg_contribution = serializers.DecimalField(max_digits=20, decimal_places=6)
    conversion_rate = serializers.FloatField()


class InvestorPortfolioSerializer(serializers.Serializer):
    """Serializer for investor portfolio data"""
    
    total_invested = serializers.DecimalField(max_digits=20, decimal_places=6)
    total_earned = serializers.DecimalField(max_digits=20, decimal_places=6)
    claimable_royalties = serializers.DecimalField(max_digits=20, decimal_places=6)
    claimed_royalties = serializers.DecimalField(max_digits=20, decimal_places=6)
    overall_roi = serializers.FloatField()
    investment_count = serializers.IntegerField()
    
    # Investment details
    investments = serializers.ListField()
    royalty_trends = serializers.DictField()
    monthly_earnings = serializers.ListField()
    campaign_performance = serializers.ListField()
    best_performing_campaign = serializers.DictField()
    worst_performing_campaign = serializers.DictField()


class InvestmentSerializer(serializers.Serializer):
    """Serializer for individual investment data"""
    
    campaign_id = serializers.IntegerField()
    campaign_title = serializers.CharField()
    nft_id = serializers.IntegerField()
    contribution_amount = serializers.DecimalField(max_digits=20, decimal_places=6)
    share_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    royalty_earned = serializers.DecimalField(max_digits=20, decimal_places=6)
    royalty_claimable = serializers.DecimalField(max_digits=20, decimal_places=6)
    royalty_claimed = serializers.DecimalField(max_digits=20, decimal_places=6)
    status = serializers.CharField()
    investment_date = serializers.DateTimeField()
    last_royalty_date = serializers.DateTimeField(allow_null=True)


class RevenueSummarySerializer(serializers.Serializer):
    """Serializer for revenue summary data"""
    
    total_revenue = serializers.DecimalField(max_digits=20, decimal_places=6)
    period = serializers.DictField()
    revenue_by_source = serializers.ListField()
    revenue_by_campaign = serializers.ListField()
    daily_revenue = serializers.ListField()


class RevenueChartDataSerializer(serializers.Serializer):
    """Serializer for revenue chart data"""
    
    labels = serializers.ListField()
    revenue = serializers.ListField()
    creator_royalties = serializers.ListField()
    investor_royalties = serializers.ListField()
    platform_fees = serializers.ListField()


class SourceBreakdownSerializer(serializers.Serializer):
    """Serializer for revenue source breakdown"""
    
    source = serializers.CharField()
    amount = serializers.DecimalField(max_digits=20, decimal_places=6)
    percentage = serializers.FloatField()
    count = serializers.IntegerField()


class CampaignPerformanceSerializer(serializers.Serializer):
    """Serializer for campaign performance data"""
    
    campaign_id = serializers.IntegerField()
    title = serializers.CharField()
    roi_percentage = serializers.FloatField()
    total_earned = serializers.DecimalField(max_digits=20, decimal_places=6)
    status = serializers.CharField()


class MonthlyEarningsSerializer(serializers.Serializer):
    """Serializer for monthly earnings data"""
    
    month = serializers.CharField()
    earnings = serializers.DecimalField(max_digits=20, decimal_places=6)
    investments = serializers.IntegerField()


class RoyaltyTrendsSerializer(serializers.Serializer):
    """Serializer for royalty trends data"""
    
    labels = serializers.ListField()
    royalty_data = serializers.ListField()
    cumulative_data = serializers.ListField()


class FundingTrendsSerializer(serializers.Serializer):
    """Serializer for funding trends data"""
    
    labels = serializers.ListField()
    funding_data = serializers.ListField()
    backer_data = serializers.ListField()


class RevenueForecastSerializer(serializers.Serializer):
    """Serializer for revenue forecast data"""
    
    next_month = serializers.DecimalField(max_digits=20, decimal_places=6)
    next_quarter = serializers.DecimalField(max_digits=20, decimal_places=6)
    next_year = serializers.DecimalField(max_digits=20, decimal_places=6)