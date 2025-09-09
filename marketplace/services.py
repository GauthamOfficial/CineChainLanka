import logging
from decimal import Decimal
from typing import Optional
from django.db import transaction
from django.utils import timezone
from .models import NFTListing, NFTSale, MarketplaceSettings

logger = logging.getLogger(__name__)


class MarketplaceService:
    """Service for marketplace operations"""
    
    def __init__(self):
        self.settings = self._get_marketplace_settings()
    
    def _get_marketplace_settings(self) -> MarketplaceSettings:
        """Get marketplace settings"""
        settings, created = MarketplaceSettings.objects.get_or_create(
            is_active=True,
            defaults={
                'platform_fee_percentage': Decimal('2.50'),
                'creator_royalty_percentage': Decimal('5.00'),
                'minimum_listing_price': Decimal('1.00'),
                'maximum_listing_price': Decimal('1000000.00'),
                'auction_duration_hours': 72,
                'is_active': True
            }
        )
        return settings
    
    def process_sale(self, listing: NFTListing, buyer) -> NFTSale:
        """Process a sale of an NFT listing"""
        try:
            with transaction.atomic():
                # Calculate fees
                sale_price = listing.price
                platform_fee = sale_price * (self.settings.platform_fee_percentage / 100)
                creator_royalty = sale_price * (self.settings.creator_royalty_percentage / 100)
                seller_amount = sale_price - platform_fee - creator_royalty
                
                # Create sale record
                sale = NFTSale.objects.create(
                    listing=listing,
                    buyer=buyer,
                    sale_price=sale_price,
                    currency=listing.currency,
                    platform_fee=platform_fee,
                    creator_royalty=creator_royalty,
                    seller_amount=seller_amount,
                    blockchain_tx_hash='0x0000000000000000000000000000000000000000000000000000000000000000'  # Placeholder
                )
                
                # Update listing status
                listing.status = 'sold'
                listing.save()
                
                logger.info(f"Sale processed: {sale.id} for NFT #{listing.nft_id}")
                return sale
                
        except Exception as e:
            logger.error(f"Error processing sale: {e}")
            raise
    
    def process_auction_end(self, listing: NFTListing) -> Optional[NFTSale]:
        """Process the end of an auction"""
        try:
            if listing.listing_type != 'auction' or listing.status != 'active':
                return None
            
            if not listing.expires_at or listing.expires_at > timezone.now():
                return None
            
            # Get winning bid
            winning_bid = listing.bids.filter(status='active').order_by('-amount').first()
            if not winning_bid:
                # No bids, mark as expired
                listing.status = 'expired'
                listing.save()
                return None
            
            # Process sale
            sale = self.process_sale(listing, winning_bid.bidder)
            
            # Update bid status
            winning_bid.status = 'won'
            winning_bid.save()
            
            return sale
            
        except Exception as e:
            logger.error(f"Error processing auction end: {e}")
            raise
    
    def get_listing_stats(self, listing: NFTListing) -> dict:
        """Get statistics for a listing"""
        try:
            stats = {
                'view_count': listing.view_count,
                'like_count': listing.like_count,
                'bid_count': listing.bids.filter(status='active').count(),
                'highest_bid': None,
                'time_remaining': None
            }
            
            # Get highest bid
            highest_bid = listing.bids.filter(status='active').order_by('-amount').first()
            if highest_bid:
                stats['highest_bid'] = {
                    'amount': highest_bid.amount,
                    'currency': highest_bid.currency,
                    'bidder': highest_bid.bidder.username
                }
            
            # Calculate time remaining for auctions
            if listing.listing_type == 'auction' and listing.expires_at:
                remaining = listing.expires_at - timezone.now()
                if remaining.total_seconds() > 0:
                    stats['time_remaining'] = {
                        'days': remaining.days,
                        'hours': remaining.seconds // 3600,
                        'minutes': (remaining.seconds % 3600) // 60
                    }
                else:
                    stats['time_remaining'] = {'expired': True}
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting listing stats: {e}")
            return {}
    
    def get_marketplace_stats(self) -> dict:
        """Get overall marketplace statistics"""
        try:
            from django.db.models import Count, Sum, Avg
            
            stats = {
                'total_listings': NFTListing.objects.filter(status='active').count(),
                'total_sales': NFTSale.objects.count(),
                'total_volume': NFTSale.objects.aggregate(
                    total=Sum('sale_price')
                )['total'] or Decimal('0'),
                'average_sale_price': NFTSale.objects.aggregate(
                    avg=Avg('sale_price')
                )['avg'] or Decimal('0'),
                'active_auctions': NFTListing.objects.filter(
                    listing_type='auction',
                    status='active'
                ).count(),
                'fixed_price_listings': NFTListing.objects.filter(
                    listing_type='fixed',
                    status='active'
                ).count()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting marketplace stats: {e}")
            return {}
