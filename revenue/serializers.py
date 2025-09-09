from rest_framework import serializers
from .models import (
    RevenueSource, RevenueEntry, RoyaltyDistribution, 
    InvestorRoyalty, RevenueAnalytics, OTTPlatformIntegration, RevenueWebhook
)
from campaigns.serializers import CampaignSerializer
from users.serializers import UserSerializer


class RevenueSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevenueSource
        fields = [
            'id', 'name', 'revenue_type', 'description', 'token_address',
            'platform_fee_percentage', 'creator_fee_percentage', 'investor_fee_percentage',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RevenueEntrySerializer(serializers.ModelSerializer):
    campaign = CampaignSerializer(read_only=True)
    source = RevenueSourceSerializer(read_only=True)
    verified_by = UserSerializer(read_only=True)
    
    class Meta:
        model = RevenueEntry
        fields = [
            'id', 'campaign', 'source', 'amount', 'currency', 'description',
            'revenue_date', 'verification_document', 'status', 'verified_by',
            'verified_at', 'blockchain_tx_hash', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'verified_by', 'verified_at', 'created_at', 'updated_at']


class RevenueEntryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevenueEntry
        fields = [
            'campaign', 'source', 'amount', 'currency', 'description',
            'revenue_date', 'verification_document'
        ]


class InvestorRoyaltySerializer(serializers.ModelSerializer):
    investor = UserSerializer(read_only=True)
    
    class Meta:
        model = InvestorRoyalty
        fields = [
            'id', 'distribution', 'investor', 'nft_id', 'contribution_amount',
            'share_percentage', 'royalty_amount', 'status', 'claimed_at',
            'blockchain_tx_hash', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RoyaltyDistributionSerializer(serializers.ModelSerializer):
    campaign = CampaignSerializer(read_only=True)
    revenue_entry = RevenueEntrySerializer(read_only=True)
    investor_royalties = InvestorRoyaltySerializer(many=True, read_only=True)
    
    class Meta:
        model = RoyaltyDistribution
        fields = [
            'id', 'campaign', 'revenue_entry', 'distribution_date',
            'creator_amount', 'platform_amount', 'total_investor_amount',
            'status', 'blockchain_tx_hash', 'error_message', 'investor_royalties',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RevenueAnalyticsSerializer(serializers.ModelSerializer):
    campaign = CampaignSerializer(read_only=True)
    
    class Meta:
        model = RevenueAnalytics
        fields = [
            'id', 'campaign', 'total_revenue', 'total_creator_royalties',
            'total_platform_fees', 'total_investor_royalties', 'total_distributions',
            'last_distribution_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OTTPlatformIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTTPlatformIntegration
        fields = [
            'id', 'name', 'platform_type', 'api_endpoint', 'webhook_url',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RevenueWebhookSerializer(serializers.ModelSerializer):
    platform = OTTPlatformIntegrationSerializer(read_only=True)
    campaign = CampaignSerializer(read_only=True)
    
    class Meta:
        model = RevenueWebhook
        fields = [
            'id', 'platform', 'campaign', 'payload', 'status', 'response_code',
            'response_message', 'processed_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RevenueSummarySerializer(serializers.Serializer):
    """Serializer for revenue summary data"""
    total_revenue = serializers.DecimalField(max_digits=20, decimal_places=6)
    total_creator_royalties = serializers.DecimalField(max_digits=20, decimal_places=6)
    total_platform_fees = serializers.DecimalField(max_digits=20, decimal_places=6)
    total_investor_royalties = serializers.DecimalField(max_digits=20, decimal_places=6)
    total_distributions = serializers.IntegerField()
    pending_royalties = serializers.DecimalField(max_digits=20, decimal_places=6)
    last_distribution_date = serializers.DateTimeField(allow_null=True)


class InvestorPortfolioSerializer(serializers.Serializer):
    """Serializer for investor portfolio data"""
    total_invested = serializers.DecimalField(max_digits=20, decimal_places=6)
    total_royalties_earned = serializers.DecimalField(max_digits=20, decimal_places=6)
    total_royalties_claimable = serializers.DecimalField(max_digits=20, decimal_places=6)
    total_royalties_claimed = serializers.DecimalField(max_digits=20, decimal_places=6)
    roi_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    active_campaigns = serializers.IntegerField()
    completed_campaigns = serializers.IntegerField()
    total_nfts = serializers.IntegerField()


class RevenueChartDataSerializer(serializers.Serializer):
    """Serializer for revenue chart data"""
    labels = serializers.ListField(child=serializers.CharField())
    revenue_data = serializers.ListField(child=serializers.DecimalField(max_digits=20, decimal_places=6))
    creator_royalties_data = serializers.ListField(child=serializers.DecimalField(max_digits=20, decimal_places=6))
    investor_royalties_data = serializers.ListField(child=serializers.DecimalField(max_digits=20, decimal_places=6))
    platform_fees_data = serializers.ListField(child=serializers.DecimalField(max_digits=20, decimal_places=6))
