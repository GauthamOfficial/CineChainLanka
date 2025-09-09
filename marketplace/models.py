from django.db import models
from django.contrib.auth import get_user_model
from campaigns.models import Campaign
from blockchain.models import BlockchainNetwork

User = get_user_model()


class NFTListing(models.Model):
    """NFT marketplace listing"""
    
    LISTING_TYPE_CHOICES = [
        ('fixed', 'Fixed Price'),
        ('auction', 'Auction'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    nft_id = models.PositiveIntegerField(help_text="NFT ID from blockchain")
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='nft_listings')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nft_listings')
    price = models.DecimalField(max_digits=20, decimal_places=6, help_text="Listing price in USDT")
    currency = models.CharField(max_length=10, default='USDT')
    royalty_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Royalty percentage for future sales")
    description = models.TextField(blank=True, help_text="Listing description")
    image_url = models.URLField(blank=True, help_text="NFT image URL")
    metadata = models.JSONField(default=dict, help_text="NFT metadata")
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPE_CHOICES, default='fixed')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Auction end time")
    
    # Engagement metrics
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "NFT Listing"
        verbose_name_plural = "NFT Listings"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"NFT #{self.nft_id} - {self.campaign.title}"


class NFTBid(models.Model):
    """NFT auction bids"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('outbid', 'Outbid'),
        ('winning', 'Winning'),
        ('won', 'Won'),
        ('cancelled', 'Cancelled'),
    ]
    
    listing = models.ForeignKey(NFTListing, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nft_bids')
    amount = models.DecimalField(max_digits=20, decimal_places=6, help_text="Bid amount in USDT")
    currency = models.CharField(max_length=10, default='USDT')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    blockchain_tx_hash = models.CharField(max_length=66, blank=True, null=True)
    
    class Meta:
        verbose_name = "NFT Bid"
        verbose_name_plural = "NFT Bids"
        ordering = ['-amount', '-created_at']
        unique_together = ['listing', 'bidder']
    
    def __str__(self):
        return f"Bid by {self.bidder.username} - {self.amount} {self.currency}"


class NFTSale(models.Model):
    """NFT sales record"""
    
    listing = models.OneToOneField(NFTListing, on_delete=models.CASCADE, related_name='sale')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nft_purchases')
    sale_price = models.DecimalField(max_digits=20, decimal_places=6, help_text="Final sale price")
    currency = models.CharField(max_length=10, default='USDT')
    platform_fee = models.DecimalField(max_digits=20, decimal_places=6, help_text="Platform fee")
    creator_royalty = models.DecimalField(max_digits=20, decimal_places=6, help_text="Creator royalty")
    seller_amount = models.DecimalField(max_digits=20, decimal_places=6, help_text="Amount received by seller")
    blockchain_tx_hash = models.CharField(max_length=66, help_text="Blockchain transaction hash")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "NFT Sale"
        verbose_name_plural = "NFT Sales"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Sale of NFT #{self.listing.nft_id} - {self.sale_price} {self.currency}"


class NFTLike(models.Model):
    """NFT likes/favorites"""
    
    listing = models.ForeignKey(NFTListing, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nft_likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "NFT Like"
        verbose_name_plural = "NFT Likes"
        unique_together = ['listing', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} likes NFT #{self.listing.nft_id}"


class NFTView(models.Model):
    """NFT view tracking"""
    
    listing = models.ForeignKey(NFTListing, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nft_views', null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "NFT View"
        verbose_name_plural = "NFT Views"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"View of NFT #{self.listing.nft_id}"


class MarketplaceSettings(models.Model):
    """Marketplace configuration settings"""
    
    platform_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=2.50)
    creator_royalty_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    minimum_listing_price = models.DecimalField(max_digits=20, decimal_places=6, default=1.00)
    maximum_listing_price = models.DecimalField(max_digits=20, decimal_places=6, default=1000000.00)
    auction_duration_hours = models.PositiveIntegerField(default=72)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Marketplace Settings"
        verbose_name_plural = "Marketplace Settings"
    
    def __str__(self):
        return f"Marketplace Settings - {self.platform_fee_percentage}% fee"
