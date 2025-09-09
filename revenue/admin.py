from django.contrib import admin
from .models import (
    RevenueSource, RevenueEntry, RoyaltyDistribution, 
    InvestorRoyalty, RevenueAnalytics, OTTPlatformIntegration, RevenueWebhook
)


@admin.register(RevenueSource)
class RevenueSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'revenue_type', 'platform_fee_percentage', 'creator_fee_percentage', 'investor_fee_percentage', 'is_active']
    list_filter = ['revenue_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RevenueEntry)
class RevenueEntryAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'source', 'amount', 'currency', 'revenue_date', 'status', 'verified_by']
    list_filter = ['status', 'currency', 'revenue_date', 'source__revenue_type']
    search_fields = ['campaign__title', 'description', 'source__name']
    readonly_fields = ['created_at', 'updated_at', 'verified_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('campaign', 'source', 'verified_by')


@admin.register(RoyaltyDistribution)
class RoyaltyDistributionAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'distribution_date', 'creator_amount', 'platform_amount', 'total_investor_amount', 'status']
    list_filter = ['status', 'distribution_date']
    search_fields = ['campaign__title', 'blockchain_tx_hash']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('campaign', 'revenue_entry')


@admin.register(InvestorRoyalty)
class InvestorRoyaltyAdmin(admin.ModelAdmin):
    list_display = ['investor', 'nft_id', 'contribution_amount', 'royalty_amount', 'status', 'claimed_at']
    list_filter = ['status', 'claimed_at', 'created_at']
    search_fields = ['investor__username', 'investor__email', 'nft_id']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('investor', 'distribution__campaign')


@admin.register(RevenueAnalytics)
class RevenueAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'total_revenue', 'total_creator_royalties', 'total_investor_royalties', 'total_distributions']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['campaign__title']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('campaign')


@admin.register(OTTPlatformIntegration)
class OTTPlatformIntegrationAdmin(admin.ModelAdmin):
    list_display = ['name', 'platform_type', 'is_active', 'created_at']
    list_filter = ['platform_type', 'is_active', 'created_at']
    search_fields = ['name', 'api_endpoint']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RevenueWebhook)
class RevenueWebhookAdmin(admin.ModelAdmin):
    list_display = ['platform', 'campaign', 'status', 'response_code', 'created_at']
    list_filter = ['status', 'response_code', 'created_at', 'platform__platform_type']
    search_fields = ['campaign__title', 'platform__name']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('platform', 'campaign')
