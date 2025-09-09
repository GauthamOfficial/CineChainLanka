from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NFTListingViewSet, NFTBidViewSet, NFTSaleViewSet, MarketplaceSettingsViewSet
)

router = DefaultRouter()
router.register(r'nfts', NFTListingViewSet)
router.register(r'bids', NFTBidViewSet)
router.register(r'sales', NFTSaleViewSet)
router.register(r'settings', MarketplaceSettingsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
