from rest_framework import serializers


class CreatorAnalyticsSerializer(serializers.Serializer):
    """Serializer for creator analytics data"""
    total_campaigns = serializers.IntegerField()
    active_campaigns = serializers.IntegerField()
    completed_campaigns = serializers.IntegerField()
    total_funding_raised = serializers.FloatField()
    total_backers = serializers.IntegerField()
    avg_campaign_performance = serializers.FloatField()
    top_performing_campaigns = serializers.ListField()
    recent_campaigns = serializers.ListField()
    funding_trends = serializers.DictField()
    revenue_forecast = serializers.DictField()


class InvestorPortfolioSerializer(serializers.Serializer):
    """Serializer for investor portfolio data"""
    total_invested = serializers.DecimalField(max_digits=20, decimal_places=6)
    total_royalties_earned = serializers.DecimalField(max_digits=20, decimal_places=6)
    total_royalties_claimable = serializers.DecimalField(max_digits=20, decimal_places=6)
    total_royalties_claimed = serializers.DecimalField(max_digits=20, decimal_places=6)
    roi_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    active_investments = serializers.IntegerField()
    completed_investments = serializers.IntegerField()
    total_nfts = serializers.IntegerField()
    avg_roi_per_campaign = serializers.DecimalField(max_digits=5, decimal_places=2)
    best_performing_campaign = serializers.DictField()
    worst_performing_campaign = serializers.DictField()
    investments = serializers.ListField()
    royalty_trends = serializers.DictField()
    monthly_earnings = serializers.ListField()
    campaign_performance = serializers.ListField()


class RevenueSummarySerializer(serializers.Serializer):
    """Serializer for revenue summary data"""
    total_revenue = serializers.DecimalField(max_digits=20, decimal_places=6)
    total_creator_royalties = serializers.DecimalField(max_digits=20, decimal_places=6)
    total_platform_fees = serializers.DecimalField(max_digits=20, decimal_places=6)
    total_investor_royalties = serializers.DecimalField(max_digits=20, decimal_places=6)
    total_distributions = serializers.IntegerField()
    pending_royalties = serializers.DecimalField(max_digits=20, decimal_places=6)
    last_distribution_date = serializers.DateTimeField(allow_null=True)


class RevenueChartDataSerializer(serializers.Serializer):
    """Serializer for revenue chart data"""
    labels = serializers.ListField(child=serializers.CharField())
    revenue_data = serializers.ListField(child=serializers.DecimalField(max_digits=20, decimal_places=6))
    creator_royalties_data = serializers.ListField(child=serializers.DecimalField(max_digits=20, decimal_places=6))
    investor_royalties_data = serializers.ListField(child=serializers.DecimalField(max_digits=20, decimal_places=6))
    platform_fees_data = serializers.ListField(child=serializers.DecimalField(max_digits=20, decimal_places=6))
