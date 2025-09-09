import logging
from decimal import Decimal
from typing import Dict, List, Optional, Any
from django.db import transaction
from django.utils import timezone
from .models import NFTListing, NFTBid, NFTSale, NFTLike, NFTView, MarketplaceSettings
from revenue.models import RevenueEntry, RevenueSource
from revenue.blockchain_service import RoyaltyDistributionService

logger = logging.getLogger(__name__)


class MarketplaceService:
    """Service for marketplace operations"""
    
    def __init__(self):
        self.royalty_service = RoyaltyDistributionService()
    
    def process_sale(self, listing: NFTListing, buyer) -> NFTSale:
        """Process a fixed price sale"""
        try:
            with transaction.atomic():
                # Get marketplace settings
                settings = MarketplaceSettings.objects.first()
                if not settings:
                    raise Exception("Marketplace settings not found")
                
                # Calculate fees
                sale_price = listing.price
                platform_fee = sale_price * (settings.platform_fee_percentage / 100)
                creator_royalty = sale_price * (settings.creator_royalty_percentage / 100)
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
                    blockchain_tx_hash="",  # Will be updated after blockchain transaction
                    status='pending'
                )
                
                # Update listing status
                listing.status = 'sold'
                listing.save()
                
                # Process blockchain transaction
                try:
                    # This would integrate with the actual blockchain service
                    # For now, we'll simulate a successful transaction
                    sale.blockchain_tx_hash = f"0x{timezone.now().timestamp():.0f}"
                    sale.status = 'completed'
                    sale.save()
                    
                    # Create revenue entry for platform fee
                    self._create_revenue_entry(
                        campaign=listing.campaign,
                        amount=platform_fee,
                        description=f"Platform fee from NFT sale #{listing.nft_id}",
                        source_name="Marketplace Platform Fee"
                    )
                    
                    # Create revenue entry for creator royalty
                    self._create_revenue_entry(
                        campaign=listing.campaign,
                        amount=creator_royalty,
                        description=f"Creator royalty from NFT sale #{listing.nft_id}",
                        source_name="NFT Creator Royalty"
                    )
                    
                except Exception as e:
                    logger.error(f"Blockchain transaction failed: {e}")
                    sale.status = 'failed'
                    sale.save()
                    raise
                
                logger.info(f"Sale processed: {sale.id}")
                return sale
                
        except Exception as e:
            logger.error(f"Error processing sale: {e}")
            raise
    
    def process_auction_end(self, listing: NFTListing) -> Optional[NFTSale]:
        """Process the end of an auction"""
        try:
            if listing.listing_type != 'auction':
                return None
            
            if listing.status != 'active':
                return None
            
            # Get winning bid
            winning_bid = listing.bids.filter(status='winning').first()
            if not winning_bid:
                # No winning bid, mark as expired
                listing.status = 'expired'
                listing.save()
                return None
            
            # Process sale with winning bid
            with transaction.atomic():
                # Get marketplace settings
                settings = MarketplaceSettings.objects.first()
                if not settings:
                    raise Exception("Marketplace settings not found")
                
                # Calculate fees
                sale_price = winning_bid.amount
                platform_fee = sale_price * (settings.platform_fee_percentage / 100)
                creator_royalty = sale_price * (settings.creator_royalty_percentage / 100)
                seller_amount = sale_price - platform_fee - creator_royalty
                
                # Create sale record
                sale = NFTSale.objects.create(
                    listing=listing,
                    buyer=winning_bid.bidder,
                    sale_price=sale_price,
                    currency=listing.currency,
                    platform_fee=platform_fee,
                    creator_royalty=creator_royalty,
                    seller_amount=seller_amount,
                    blockchain_tx_hash="",  # Will be updated after blockchain transaction
                    status='pending'
                )
                
                # Update listing status
                listing.status = 'sold'
                listing.save()
                
                # Update bid status
                winning_bid.status = 'won'
                winning_bid.save()
                
                # Process blockchain transaction
                try:
                    sale.blockchain_tx_hash = f"0x{timezone.now().timestamp():.0f}"
                    sale.status = 'completed'
                    sale.save()
                    
                    # Create revenue entries
                    self._create_revenue_entry(
                        campaign=listing.campaign,
                        amount=platform_fee,
                        description=f"Platform fee from NFT auction #{listing.nft_id}",
                        source_name="Marketplace Platform Fee"
                    )
                    
                    self._create_revenue_entry(
                        campaign=listing.campaign,
                        amount=creator_royalty,
                        description=f"Creator royalty from NFT auction #{listing.nft_id}",
                        source_name="NFT Creator Royalty"
                    )
                    
                except Exception as e:
                    logger.error(f"Blockchain transaction failed: {e}")
                    sale.status = 'failed'
                    sale.save()
                    raise
                
                logger.info(f"Auction sale processed: {sale.id}")
                return sale
                
        except Exception as e:
            logger.error(f"Error processing auction end: {e}")
            raise
    
    def place_bid(self, listing: NFTListing, bidder, amount: Decimal) -> NFTBid:
        """Place a bid on an auction listing"""
        try:
            with transaction.atomic():
                # Validate bid
                if listing.listing_type != 'auction':
                    raise Exception("Can only bid on auction listings")
                
                if listing.status != 'active':
                    raise Exception("Listing is not active")
                
                if listing.owner == bidder:
                    raise Exception("Cannot bid on your own listing")
                
                # Check if auction has expired
                if listing.expires_at and listing.expires_at <= timezone.now():
                    raise Exception("Auction has expired")
                
                # Check if bid is higher than current highest bid
                highest_bid = listing.bids.filter(status__in=['active', 'winning']).order_by('-amount').first()
                if highest_bid and amount <= highest_bid.amount:
                    raise Exception("Bid must be higher than current highest bid")
                
                # Check if bid is higher than minimum price
                if amount < listing.price:
                    raise Exception("Bid must be at least the minimum price")
                
                # Create bid
                bid = NFTBid.objects.create(
                    listing=listing,
                    bidder=bidder,
                    amount=amount,
                    currency=listing.currency,
                    status='active'
                )
                
                # Update previous bids to outbid status
                listing.bids.filter(status='active').exclude(id=bid.id).update(status='outbid')
                
                # Update bid status to winning
                bid.status = 'winning'
                bid.save()
                
                logger.info(f"Bid placed: {bid.id}")
                return bid
                
        except Exception as e:
            logger.error(f"Error placing bid: {e}")
            raise
    
    def like_listing(self, listing: NFTListing, user) -> bool:
        """Like or unlike a listing"""
        try:
            like, created = NFTLike.objects.get_or_create(
                listing=listing,
                user=user
            )
            
            if not created:
                like.delete()
                listing.like_count = max(0, listing.like_count - 1)
                listing.save()
                return False
            else:
                listing.like_count += 1
                listing.save()
                return True
                
        except Exception as e:
            logger.error(f"Error liking listing: {e}")
            raise
    
    def view_listing(self, listing: NFTListing, user=None, ip_address=None, user_agent=None) -> None:
        """Record a view of a listing"""
        try:
            # Create view record
            NFTView.objects.create(
                listing=listing,
                user=user,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Update view count
            listing.view_count += 1
            listing.save()
            
        except Exception as e:
            logger.error(f"Error recording view: {e}")
    
    def get_listing_stats(self, listing: NFTListing) -> Dict:
        """Get statistics for a listing"""
        try:
            stats = {
                'view_count': listing.view_count,
                'like_count': listing.like_count,
                'bid_count': 0,
                'highest_bid': None,
                'time_remaining': None
            }
            
            if listing.listing_type == 'auction':
                bids = listing.bids.filter(status__in=['active', 'winning', 'won'])
                stats['bid_count'] = bids.count()
                
                highest_bid = bids.order_by('-amount').first()
                if highest_bid:
                    stats['highest_bid'] = {
                        'amount': float(highest_bid.amount),
                        'bidder': highest_bid.bidder.username,
                        'created_at': highest_bid.created_at.isoformat()
                    }
                
                if listing.expires_at:
                    now = timezone.now()
                    if listing.expires_at > now:
                        delta = listing.expires_at - now
                        stats['time_remaining'] = {
                            'days': delta.days,
                            'hours': delta.seconds // 3600,
                            'minutes': (delta.seconds % 3600) // 60
                        }
                    else:
                        stats['time_remaining'] = 'expired'
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting listing stats: {e}")
            return {}
    
    def get_marketplace_stats(self) -> Dict:
        """Get overall marketplace statistics"""
        try:
            total_listings = NFTListing.objects.count()
            active_listings = NFTListing.objects.filter(status='active').count()
            sold_listings = NFTListing.objects.filter(status='sold').count()
            
            total_volume = NFTSale.objects.aggregate(
                total=Sum('sale_price')
            )['total'] or Decimal('0')
            
            total_fees = NFTSale.objects.aggregate(
                total=Sum('platform_fee')
            )['total'] or Decimal('0')
            
            total_royalties = NFTSale.objects.aggregate(
                total=Sum('creator_royalty')
            )['total'] or Decimal('0')
            
            return {
                'total_listings': total_listings,
                'active_listings': active_listings,
                'sold_listings': sold_listings,
                'total_volume': float(total_volume),
                'total_fees': float(total_fees),
                'total_royalties': float(total_royalties)
            }
            
        except Exception as e:
            logger.error(f"Error getting marketplace stats: {e}")
            return {}
    
    def _create_revenue_entry(self, campaign, amount: Decimal, description: str, source_name: str) -> None:
        """Create a revenue entry for marketplace fees"""
        try:
            # Get or create revenue source
            source, created = RevenueSource.objects.get_or_create(
                name=source_name,
                revenue_type='marketplace',
                defaults={
                    'description': f'{source_name} from NFT marketplace',
                    'platform_fee_percentage': Decimal('0.00'),
                    'creator_fee_percentage': Decimal('0.00'),
                    'investor_fee_percentage': Decimal('0.00'),
                }
            )
            
            # Create revenue entry
            RevenueEntry.objects.create(
                campaign=campaign,
                source=source,
                amount=amount,
                currency='USDT',
                description=description,
                revenue_date=timezone.now().date(),
                status='verified'
            )
            
        except Exception as e:
            logger.error(f"Error creating revenue entry: {e}")
    
    def check_expired_auctions(self) -> List[NFTSale]:
        """Check for expired auctions and process them"""
        try:
            expired_listings = NFTListing.objects.filter(
                listing_type='auction',
                status='active',
                expires_at__lte=timezone.now()
            )
            
            processed_sales = []
            for listing in expired_listings:
                sale = self.process_auction_end(listing)
                if sale:
                    processed_sales.append(sale)
            
            logger.info(f"Processed {len(processed_sales)} expired auctions")
            return processed_sales
            
        except Exception as e:
            logger.error(f"Error checking expired auctions: {e}")
            return []