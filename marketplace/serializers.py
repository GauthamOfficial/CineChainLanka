from rest_framework import serializers
from .models import (
    NFTListing, NFTBid, NFTSale, NFTLike, NFTView, MarketplaceSettings
)
from campaigns.serializers import CampaignSerializer
from users.serializers import UserSerializer


class NFTListingSerializer(serializers.ModelSerializer):
    campaign = CampaignSerializer(read_only=True)
    owner = UserSerializer(read_only=True)
    
    class Meta:
        model = NFTListing
        fields = [
            'id', 'nft_id', 'campaign', 'owner', 'price', 'currency',
            'royalty_percentage', 'description', 'image_url', 'metadata',
            'listing_type', 'status', 'created_at', 'updated_at', 'expires_at',
            'view_count', 'like_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'view_count', 'like_count']


class NFTListingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NFTListing
        fields = [
            'nft_id', 'campaign', 'price', 'currency', 'royalty_percentage',
            'description', 'image_url', 'metadata', 'listing_type', 'expires_at'
        ]


class NFTBidSerializer(serializers.ModelSerializer):
    bidder = UserSerializer(read_only=True)
    
    class Meta:
        model = NFTBid
        fields = [
            'id', 'listing', 'bidder', 'amount', 'currency', 'status',
            'created_at', 'updated_at', 'blockchain_tx_hash'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NFTBidCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NFTBid
        fields = ['listing', 'amount', 'currency']


class NFTSaleSerializer(serializers.ModelSerializer):
    buyer = UserSerializer(read_only=True)
    listing = NFTListingSerializer(read_only=True)
    
    class Meta:
        model = NFTSale
        fields = [
            'id', 'listing', 'buyer', 'sale_price', 'currency',
            'platform_fee', 'creator_royalty', 'seller_amount',
            'blockchain_tx_hash', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class NFTLikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = NFTLike
        fields = ['id', 'listing', 'user', 'created_at']
        read_only_fields = ['id', 'created_at']


class NFTViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = NFTView
        fields = ['id', 'listing', 'user', 'ip_address', 'created_at']
        read_only_fields = ['id', 'created_at']


class MarketplaceSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketplaceSettings
        fields = [
            'id', 'platform_fee_percentage', 'creator_royalty_percentage',
            'minimum_listing_price', 'maximum_listing_price',
            'auction_duration_hours', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NFTListingDetailSerializer(serializers.ModelSerializer):
    campaign = CampaignSerializer(read_only=True)
    owner = UserSerializer(read_only=True)
    bids = NFTBidSerializer(many=True, read_only=True)
    likes = NFTLikeSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()
    highest_bid = serializers.SerializerMethodField()
    bid_count = serializers.SerializerMethodField()
    
    class Meta:
        model = NFTListing
        fields = [
            'id', 'nft_id', 'campaign', 'owner', 'price', 'currency',
            'royalty_percentage', 'description', 'image_url', 'metadata',
            'listing_type', 'status', 'created_at', 'updated_at', 'expires_at',
            'view_count', 'like_count', 'bids', 'likes', 'is_liked',
            'highest_bid', 'bid_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'view_count', 'like_count']
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def get_highest_bid(self, obj):
        highest_bid = obj.bids.filter(status='active').order_by('-amount').first()
        if highest_bid:
            return NFTBidSerializer(highest_bid).data
        return None
    
    def get_bid_count(self, obj):
        return obj.bids.filter(status='active').count()
