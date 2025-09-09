from rest_framework import serializers
from decimal import Decimal
from django.utils import timezone
from .models import NFTListing, NFTBid, NFTLike, NFTView, MarketplaceSettings


class NFTListingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating NFT listings"""
    
    class Meta:
        model = NFTListing
        fields = [
            'nft_id', 'campaign', 'price', 'currency', 'royalty_percentage',
            'description', 'image_url', 'metadata', 'listing_type', 'expires_at'
        ]
    
    def validate_price(self, value):
        """Validate listing price"""
        settings = MarketplaceSettings.objects.first()
        if settings:
            if value < settings.minimum_listing_price:
                raise serializers.ValidationError(
                    f"Price must be at least {settings.minimum_listing_price} {self.initial_data.get('currency', 'USDT')}"
                )
            if value > settings.maximum_listing_price:
                raise serializers.ValidationError(
                    f"Price must not exceed {settings.maximum_listing_price} {self.initial_data.get('currency', 'USDT')}"
                )
        return value
    
    def validate_expires_at(self, value):
        """Validate auction expiration time"""
        listing_type = self.initial_data.get('listing_type')
        if listing_type == 'auction' and not value:
            raise serializers.ValidationError("Auction listings must have an expiration time")
        return value


class NFTListingDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed NFT listing view"""
    
    campaign_title = serializers.CharField(source='campaign.title', read_only=True)
    creator_name = serializers.SerializerMethodField()
    owner_name = serializers.SerializerMethodField()
    image_url = serializers.URLField(required=False, allow_blank=True)
    metadata = serializers.JSONField(default=dict)
    view_count = serializers.IntegerField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    highest_bid = serializers.SerializerMethodField()
    bid_count = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()
    bids = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    views = serializers.SerializerMethodField()
    
    class Meta:
        model = NFTListing
        fields = [
            'id', 'nft_id', 'campaign', 'campaign_title', 'owner', 'owner_name',
            'price', 'currency', 'royalty_percentage', 'description', 'image_url',
            'metadata', 'listing_type', 'status', 'created_at', 'updated_at',
            'expires_at', 'view_count', 'like_count', 'highest_bid', 'bid_count',
            'time_remaining', 'bids', 'likes', 'views'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'view_count', 'like_count']
    
    def get_creator_name(self, obj):
        """Get creator's full name"""
        creator = obj.campaign.creator
        return f"{creator.first_name} {creator.last_name}".strip()
    
    def get_owner_name(self, obj):
        """Get owner's full name"""
        return f"{obj.owner.first_name} {obj.owner.last_name}".strip()
    
    def get_highest_bid(self, obj):
        """Get highest bid amount"""
        if obj.listing_type == 'auction':
            highest_bid = obj.bids.filter(status__in=['active', 'winning']).order_by('-amount').first()
            return float(highest_bid.amount) if highest_bid else 0.0
        return None
    
    def get_bid_count(self, obj):
        """Get total number of bids"""
        if obj.listing_type == 'auction':
            return obj.bids.filter(status__in=['active', 'winning', 'won']).count()
        return 0
    
    def get_time_remaining(self, obj):
        """Get time remaining for auction"""
        if obj.listing_type == 'auction' and obj.expires_at:
            now = timezone.now()
            if obj.expires_at > now:
                delta = obj.expires_at - now
                days = delta.days
                hours = delta.seconds // 3600
                minutes = (delta.seconds % 3600) // 60
                return f"{days}d {hours}h {minutes}m"
            return "Expired"
        return None
    
    def get_bids(self, obj):
        """Get all bids for this listing"""
        from .serializers import NFTBidSerializer
        return NFTBidSerializer(obj.bids.all(), many=True).data
    
    def get_likes(self, obj):
        """Get all likes for this listing"""
        from .serializers import NFTLikeSerializer
        return NFTLikeSerializer(obj.likes.all(), many=True).data
    
    def get_views(self, obj):
        """Get all views for this listing"""
        from .serializers import NFTViewSerializer
        return NFTViewSerializer(obj.views.all(), many=True).data


class NFTBidCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating NFT bids"""
    
    class Meta:
        model = NFTBid
        fields = ['amount', 'currency']
    
    def validate_amount(self, value):
        """Validate bid amount"""
        if value <= 0:
            raise serializers.ValidationError("Bid amount must be greater than zero")
        return value
