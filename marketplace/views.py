from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, F, Count, Max
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import (
    NFTListing, NFTBid, NFTSale, NFTLike, NFTView, MarketplaceSettings
)
from .serializers import (
    NFTListingSerializer, NFTListingCreateSerializer, NFTListingDetailSerializer,
    NFTBidSerializer, NFTBidCreateSerializer, NFTSaleSerializer,
    NFTLikeSerializer, NFTViewSerializer, MarketplaceSettingsSerializer
)
from .services import MarketplaceService


class NFTListingViewSet(viewsets.ModelViewSet):
    """ViewSet for NFT marketplace listings"""
    queryset = NFTListing.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return NFTListingCreateSerializer
        elif self.action == 'retrieve':
            return NFTListingDetailSerializer
        return NFTListingSerializer
    
    def get_queryset(self):
        queryset = NFTListing.objects.select_related('campaign', 'owner').prefetch_related('bids', 'likes')
        
        # Filter by search query
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(campaign__title__icontains=search) |
                Q(description__icontains=search) |
                Q(metadata__title__icontains=search)
            )
        
        # Filter by price range
        price_min = self.request.query_params.get('price_min')
        price_max = self.request.query_params.get('price_max')
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
        
        # Filter by listing type
        listing_type = self.request.query_params.get('listing_type')
        if listing_type and listing_type != 'all':
            queryset = queryset.filter(listing_type=listing_type)
        
        # Filter by campaign
        campaign_id = self.request.query_params.get('campaign_id')
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        
        # Filter by royalty range
        royalty_min = self.request.query_params.get('royalty_min')
        royalty_max = self.request.query_params.get('royalty_max')
        if royalty_min:
            queryset = queryset.filter(royalty_percentage__gte=royalty_min)
        if royalty_max:
            queryset = queryset.filter(royalty_percentage__lte=royalty_max)
        
        # Sort by
        sort_by = self.request.query_params.get('sort_by', 'newest')
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort_by == 'popularity':
            queryset = queryset.order_by('-view_count', '-like_count')
        else:  # newest
            queryset = queryset.order_by('-created_at')
        
        # Only show active listings
        queryset = queryset.filter(status='active')
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def bid(self, request, pk=None):
        """Place a bid on an NFT listing"""
        listing = self.get_object()
        
        if listing.listing_type != 'auction':
            return Response(
                {'error': 'This listing is not an auction'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if listing.owner == request.user:
            return Response(
                {'error': 'You cannot bid on your own listing'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if listing.status != 'active':
            return Response(
                {'error': 'This listing is not active'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = NFTBidCreateSerializer(data=request.data)
        if serializer.is_valid():
            bid_amount = serializer.validated_data['amount']
            
            # Check if bid is higher than current highest bid
            highest_bid = listing.bids.filter(status='active').order_by('-amount').first()
            if highest_bid and bid_amount <= highest_bid.amount:
                return Response(
                    {'error': 'Bid must be higher than current highest bid'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if bid is higher than minimum price
            if bid_amount < listing.price:
                return Response(
                    {'error': 'Bid must be at least the minimum price'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create bid
            bid = serializer.save(
                listing=listing,
                bidder=request.user
            )
            
            # Update previous bids to outbid status
            listing.bids.filter(status='active').exclude(id=bid.id).update(status='outbid')
            
            return Response(NFTBidSerializer(bid).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def buy(self, request, pk=None):
        """Buy an NFT at fixed price"""
        listing = self.get_object()
        
        if listing.listing_type != 'fixed':
            return Response(
                {'error': 'This listing is not for sale at fixed price'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if listing.owner == request.user:
            return Response(
                {'error': 'You cannot buy your own listing'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if listing.status != 'active':
            return Response(
                {'error': 'This listing is not active'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            marketplace_service = MarketplaceService()
            sale = marketplace_service.process_sale(listing, request.user)
            
            return Response(NFTSaleSerializer(sale).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': f'Failed to process sale: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like/unlike an NFT listing"""
        listing = self.get_object()
        
        like, created = NFTLike.objects.get_or_create(
            listing=listing,
            user=request.user
        )
        
        if not created:
            like.delete()
            listing.like_count = max(0, listing.like_count - 1)
            listing.save()
            return Response({'liked': False})
        else:
            listing.like_count += 1
            listing.save()
            return Response({'liked': True})
    
    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        """Record a view of an NFT listing"""
        listing = self.get_object()
        
        # Get client IP
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Create view record
        NFTView.objects.create(
            listing=listing,
            user=request.user if request.user.is_authenticated else None,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Update view count
        listing.view_count += 1
        listing.save()
        
        return Response({'viewed': True})


class NFTBidViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for NFT bids"""
    queryset = NFTBid.objects.all()
    serializer_class = NFTBidSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return NFTBid.objects.filter(bidder=self.request.user).select_related('listing', 'bidder')


class NFTSaleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for NFT sales"""
    queryset = NFTSale.objects.all()
    serializer_class = NFTSaleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return NFTSale.objects.filter(
            Q(buyer=self.request.user) | Q(listing__owner=self.request.user)
        ).select_related('listing', 'buyer')


class MarketplaceSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for marketplace settings"""
    queryset = MarketplaceSettings.objects.all()
    serializer_class = MarketplaceSettingsSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return MarketplaceSettings.objects.filter(is_active=True)
