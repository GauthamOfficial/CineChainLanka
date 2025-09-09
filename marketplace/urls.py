from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'listings', views.NFTListingViewSet, basename='nft-listings')
router.register(r'bids', views.NFTBidViewSet, basename='nft-bids')
router.register(r'sales', views.NFTSaleViewSet, basename='nft-sales')
router.register(r'settings', views.MarketplaceSettingsViewSet, basename='marketplace-settings')

urlpatterns = [
    path('', include(router.urls)),
]