from rest_framework import serializers
from decimal import Decimal
from django.utils import timezone
from .models import NFTListing, NFTBid, NFTSale, NFTLike, NFTView, MarketplaceSettings


class NFTListingSerializer(serializers.ModelSerializer):
    """Serializer for NFT listings"""
    
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
    
    class Meta:
        model = NFTListing
        fields = [
            'id', 'nft_id', 'campaign', 'campaign_title', 'owner', 'owner_name',
            'price', 'currency', 'royalty_percentage', 'description', 'image_url',
            'metadata', 'listing_type', 'status', 'created_at', 'updated_at',
            'expires_at', 'view_count', 'like_count', 'highest_bid', 'bid_count',
            'time_remaining'
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
            from django.utils import timezone
            now = timezone.now()
            if obj.expires_at > now:
                delta = obj.expires_at - now
                days = delta.days
                hours = delta.seconds // 3600
                minutes = (delta.seconds % 3600) // 60
                return f"{days}d {hours}h {minutes}m"
            return "Expired"
        return None


class NFTBidSerializer(serializers.ModelSerializer):
    """Serializer for NFT bids"""
    
    bidder_name = serializers.SerializerMethodField()
    listing_title = serializers.CharField(source='listing.campaign.title', read_only=True)
    
    class Meta:
        model = NFTBid
        fields = [
            'id', 'listing', 'listing_title', 'bidder', 'bidder_name',
            'amount', 'currency', 'status', 'created_at', 'updated_at',
            'blockchain_tx_hash'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_bidder_name(self, obj):
        """Get bidder's full name"""
        return f"{obj.bidder.first_name} {obj.bidder.last_name}".strip()
    
    def validate_amount(self, value):
        """Validate bid amount"""
        if value <= 0:
            raise serializers.ValidationError("Bid amount must be greater than zero")
        return value
    
    def validate(self, data):
        """Validate bid data"""
        listing = data['listing']
        amount = data['amount']
        
        # Check if listing is active auction
        if listing.listing_type != 'auction':
            raise serializers.ValidationError("Can only bid on auction listings")
        
        if listing.status != 'active':
            raise serializers.ValidationError("Can only bid on active listings")
        
        # Check if auction has expired
        if listing.expires_at and listing.expires_at <= timezone.now():
            raise serializers.ValidationError("Auction has expired")
        
        # Check if bid is higher than current highest bid
        highest_bid = listing.bids.filter(status__in=['active', 'winning']).order_by('-amount').first()
        if highest_bid and amount <= highest_bid.amount:
            raise serializers.ValidationError("Bid must be higher than current highest bid")
        
        return data


class NFTSaleSerializer(serializers.ModelSerializer):
    """Serializer for NFT sales"""
    
    listing_title = serializers.CharField(source='listing.campaign.title', read_only=True)
    buyer_name = serializers.SerializerMethodField()
    seller_name = serializers.CharField(source='listing.owner.first_name', read_only=True)
    
    class Meta:
        model = NFTSale
        fields = [
            'id', 'listing', 'listing_title', 'buyer', 'buyer_name', 'seller_name',
            'sale_price', 'currency', 'platform_fee', 'creator_royalty',
            'seller_amount', 'blockchain_tx_hash', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_buyer_name(self, obj):
        """Get buyer's full name"""
        return f"{obj.buyer.first_name} {obj.buyer.last_name}".strip()


class NFTLikeSerializer(serializers.ModelSerializer):
    """Serializer for NFT likes"""
    
    user_name = serializers.SerializerMethodField()
    listing_title = serializers.CharField(source='listing.campaign.title', read_only=True)
    
    class Meta:
        model = NFTLike
        fields = ['id', 'listing', 'listing_title', 'user', 'user_name', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_user_name(self, obj):
        """Get user's full name"""
        return f"{obj.user.first_name} {obj.user.last_name}".strip()


class NFTViewSerializer(serializers.ModelSerializer):
    """Serializer for NFT views"""
    
    listing_title = serializers.CharField(source='listing.campaign.title', read_only=True)
    
    class Meta:
        model = NFTView
        fields = [
            'id', 'listing', 'listing_title', 'user', 'ip_address',
            'user_agent', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MarketplaceSettingsSerializer(serializers.ModelSerializer):
    """Serializer for marketplace settings"""
    
    class Meta:
        model = MarketplaceSettings
        fields = [
            'id', 'platform_fee_percentage', 'creator_royalty_percentage',
            'minimum_listing_price', 'maximum_listing_price',
            'auction_duration_hours', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CreateListingSerializer(serializers.ModelSerializer):
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


class BuyNowSerializer(serializers.Serializer):
    """Serializer for buy now transactions"""
    
    listing_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=['usdt', 'credit_card', 'bank_transfer'])
    
    def validate_listing_id(self, value):
        """Validate listing exists and is available for purchase"""
        try:
            listing = NFTListing.objects.get(id=value)
            if listing.listing_type != 'fixed':
                raise serializers.ValidationError("Can only buy fixed price listings")
            if listing.status != 'active':
                raise serializers.ValidationError("Listing is not active")
            return value
        except NFTListing.DoesNotExist:
            raise serializers.ValidationError("Listing not found")


class PlaceBidSerializer(serializers.Serializer):
    """Serializer for placing bids"""
    
    listing_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=20, decimal_places=6)
    
    def validate_amount(self, value):
        """Validate bid amount"""
        if value <= 0:
            raise serializers.ValidationError("Bid amount must be greater than zero")
        return value
    
    def validate(self, data):
        """Validate bid data"""
        listing_id = data['listing_id']
        amount = data['amount']
        
        try:
            listing = NFTListing.objects.get(id=listing_id)
        except NFTListing.DoesNotExist:
            raise serializers.ValidationError("Listing not found")
        
        if listing.listing_type != 'auction':
            raise serializers.ValidationError("Can only bid on auction listings")
        
        if listing.status != 'active':
            raise serializers.ValidationError("Listing is not active")
        
        # Check if auction has expired
        if listing.expires_at and listing.expires_at <= timezone.now():
            raise serializers.ValidationError("Auction has expired")
        
        # Check if bid is higher than current highest bid
        highest_bid = listing.bids.filter(status__in=['active', 'winning']).order_by('-amount').first()
        if highest_bid and amount <= highest_bid.amount:
            raise serializers.ValidationError("Bid must be higher than current highest bid")
        
        return data