from django.contrib import admin
from .models import (
    NFTListing, NFTBid, NFTSale, NFTLike, NFTView, MarketplaceSettings
)


@admin.register(NFTListing)
class NFTListingAdmin(admin.ModelAdmin):
    list_display = ['nft_id', 'campaign', 'owner', 'price', 'currency', 'listing_type', 'status', 'created_at']
    list_filter = ['listing_type', 'status', 'currency', 'created_at']
    search_fields = ['nft_id', 'campaign__title', 'owner__username', 'description']
    readonly_fields = ['created_at', 'updated_at', 'view_count', 'like_count']
    raw_id_fields = ['campaign', 'owner']


@admin.register(NFTBid)
class NFTBidAdmin(admin.ModelAdmin):
    list_display = ['listing', 'bidder', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['listing__nft_id', 'bidder__username']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['listing', 'bidder']


@admin.register(NFTSale)
class NFTSaleAdmin(admin.ModelAdmin):
    list_display = ['listing', 'buyer', 'sale_price', 'currency', 'platform_fee', 'created_at']
    list_filter = ['currency', 'created_at']
    search_fields = ['listing__nft_id', 'buyer__username', 'blockchain_tx_hash']
    readonly_fields = ['created_at']
    raw_id_fields = ['listing', 'buyer']


@admin.register(NFTLike)
class NFTLikeAdmin(admin.ModelAdmin):
    list_display = ['listing', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['listing__nft_id', 'user__username']
    readonly_fields = ['created_at']
    raw_id_fields = ['listing', 'user']


@admin.register(NFTView)
class NFTViewAdmin(admin.ModelAdmin):
    list_display = ['listing', 'user', 'ip_address', 'created_at']
    list_filter = ['created_at']
    search_fields = ['listing__nft_id', 'user__username', 'ip_address']
    readonly_fields = ['created_at']
    raw_id_fields = ['listing', 'user']


@admin.register(MarketplaceSettings)
class MarketplaceSettingsAdmin(admin.ModelAdmin):
    list_display = ['platform_fee_percentage', 'creator_royalty_percentage', 'is_active', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
