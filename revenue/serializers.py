from rest_framework import serializers
from decimal import Decimal
from .models import (
    RevenueEntry, RoyaltyDistribution, InvestorRoyalty, 
    RevenueAnalytics, RevenueSource, OTTPlatformIntegration, RevenueWebhook
)


class RevenueSourceSerializer(serializers.ModelSerializer):
    """Serializer for revenue sources"""
    
    class Meta:
        model = RevenueSource
        fields = [
            'id', 'name', 'revenue_type', 'description', 'token_address',
            'platform_fee_percentage', 'creator_fee_percentage', 'investor_fee_percentage',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RevenueEntrySerializer(serializers.ModelSerializer):
    """Serializer for revenue entries"""
    
    source_name = serializers.CharField(source='source.name', read_only=True)
    campaign_title = serializers.CharField(source='campaign.title', read_only=True)
    verified_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = RevenueEntry
        fields = [
            'id', 'campaign', 'campaign_title', 'source', 'source_name',
            'amount', 'currency', 'description', 'revenue_date',
            'verification_document', 'status', 'verified_by', 'verified_by_name',
            'verified_at', 'blockchain_tx_hash', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_verified_by_name(self, obj):
        """Get verifier's full name"""
        if obj.verified_by:
            return f"{obj.verified_by.first_name} {obj.verified_by.last_name}".strip()
        return None


class RoyaltyDistributionSerializer(serializers.ModelSerializer):
    """Serializer for royalty distributions"""
    
    campaign_title = serializers.CharField(source='campaign.title', read_only=True)
    revenue_amount = serializers.DecimalField(source='revenue_entry.amount', max_digits=20, decimal_places=6, read_only=True)
    
    class Meta:
        model = RoyaltyDistribution
        fields = [
            'id', 'campaign', 'campaign_title', 'revenue_entry', 'revenue_amount',
            'distribution_date', 'creator_amount', 'platform_amount',
            'total_investor_amount', 'status', 'blockchain_tx_hash',
            'error_message', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InvestorRoyaltySerializer(serializers.ModelSerializer):
    """Serializer for investor royalties"""
    
    campaign_title = serializers.CharField(source='distribution.campaign.title', read_only=True)
    distribution_date = serializers.DateTimeField(source='distribution.distribution_date', read_only=True)
    
    class Meta:
        model = InvestorRoyalty
        fields = [
            'id', 'distribution', 'campaign_title', 'distribution_date',
            'investor', 'nft_id', 'contribution_amount', 'share_percentage',
            'royalty_amount', 'status', 'claimed_at', 'blockchain_tx_hash',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RevenueAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for revenue analytics"""
    
    campaign_title = serializers.CharField(source='campaign.title', read_only=True)
    
    class Meta:
        model = RevenueAnalytics
        fields = [
            'id', 'campaign', 'campaign_title', 'total_revenue',
            'total_creator_royalties', 'total_platform_fees',
            'total_investor_royalties', 'total_distributions',
            'last_distribution_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OTTPlatformIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for OTT platform integrations"""
    
    class Meta:
        model = OTTPlatformIntegration
        fields = [
            'id', 'name', 'platform_type', 'api_endpoint', 'api_key',
            'webhook_url', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'api_key': {'write_only': True}
        }


class RevenueWebhookSerializer(serializers.ModelSerializer):
    """Serializer for revenue webhooks"""
    
    platform_name = serializers.CharField(source='platform.name', read_only=True)
    campaign_title = serializers.CharField(source='campaign.title', read_only=True)
    
    class Meta:
        model = RevenueWebhook
        fields = [
            'id', 'platform', 'platform_name', 'campaign', 'campaign_title',
            'payload', 'status', 'response_code', 'response_message',
            'processed_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CreateRevenueEntrySerializer(serializers.ModelSerializer):
    """Serializer for creating revenue entries"""
    
    class Meta:
        model = RevenueEntry
        fields = [
            'campaign', 'source', 'amount', 'currency', 'description',
            'revenue_date', 'verification_document'
        ]
    
    def validate_amount(self, value):
        """Validate revenue amount"""
        if value <= 0:
            raise serializers.ValidationError("Revenue amount must be greater than zero")
        return value
    
    def validate_currency(self, value):
        """Validate currency"""
        allowed_currencies = ['USDT', 'USDC', 'DAI', 'LKR', 'USD']
        if value.upper() not in allowed_currencies:
            raise serializers.ValidationError(f"Currency must be one of: {', '.join(allowed_currencies)}")
        return value.upper()


class UpdateRevenueEntryStatusSerializer(serializers.Serializer):
    """Serializer for updating revenue entry status"""
    
    status = serializers.ChoiceField(choices=RevenueEntry.STATUS_CHOICES)
    verification_document = serializers.FileField(required=False)
    
    def validate_status(self, value):
        """Validate status transition"""
        if value not in ['verified', 'processed', 'failed']:
            raise serializers.ValidationError("Invalid status for update")
        return value


class CreateRoyaltyDistributionSerializer(serializers.Serializer):
    """Serializer for creating royalty distributions"""
    
    campaign_id = serializers.IntegerField()
    revenue_entry_id = serializers.IntegerField()
    
    def validate_campaign_id(self, value):
        """Validate campaign exists"""
        from campaigns.models import Campaign
        try:
            Campaign.objects.get(id=value)
        except Campaign.DoesNotExist:
            raise serializers.ValidationError("Campaign not found")
        return value
    
    def validate_revenue_entry_id(self, value):
        """Validate revenue entry exists"""
        try:
            RevenueEntry.objects.get(id=value)
        except RevenueEntry.DoesNotExist:
            raise serializers.ValidationError("Revenue entry not found")
        return value


class ClaimRoyaltySerializer(serializers.Serializer):
    """Serializer for claiming royalties"""
    
    royalty_id = serializers.IntegerField()
    
    def validate_royalty_id(self, value):
        """Validate royalty exists and is claimable"""
        try:
            royalty = InvestorRoyalty.objects.get(id=value)
            if royalty.status != 'claimable':
                raise serializers.ValidationError("Royalty is not claimable")
        except InvestorRoyalty.DoesNotExist:
            raise serializers.ValidationError("Royalty not found")
        return value