from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RevenueSourceViewSet, RevenueEntryViewSet, RoyaltyDistributionViewSet,
    InvestorRoyaltyViewSet, RevenueAnalyticsViewSet, InvestorPortfolioViewSet,
    OTTPlatformIntegrationViewSet, RevenueWebhookViewSet
)
from .webhook_views import (
    OTTWebhookView, NetflixWebhookView, AmazonPrimeWebhookView,
    DisneyPlusWebhookView, BoxOfficeWebhookView, webhook_health_check
)

router = DefaultRouter()
router.register(r'sources', RevenueSourceViewSet)
router.register(r'entries', RevenueEntryViewSet)
router.register(r'distributions', RoyaltyDistributionViewSet)
router.register(r'royalties', InvestorRoyaltyViewSet)
router.register(r'analytics', RevenueAnalyticsViewSet)
router.register(r'portfolio', InvestorPortfolioViewSet, basename='portfolio')
router.register(r'ott-platforms', OTTPlatformIntegrationViewSet)
router.register(r'webhooks', RevenueWebhookViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # Webhook endpoints
    path('webhooks/ott/<int:platform_id>/', OTTWebhookView.as_view(), name='ott-webhook'),
    path('webhooks/netflix/', NetflixWebhookView.as_view(), name='netflix-webhook'),
    path('webhooks/amazon-prime/', AmazonPrimeWebhookView.as_view(), name='amazon-prime-webhook'),
    path('webhooks/disney-plus/', DisneyPlusWebhookView.as_view(), name='disney-plus-webhook'),
    path('webhooks/box-office/', BoxOfficeWebhookView.as_view(), name='box-office-webhook'),
    path('webhooks/health/', webhook_health_check, name='webhook-health'),
]
