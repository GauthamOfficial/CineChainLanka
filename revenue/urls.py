from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import webhook_views

router = DefaultRouter()
router.register(r'entries', views.RevenueEntryViewSet, basename='revenue-entries')
router.register(r'distributions', views.RoyaltyDistributionViewSet, basename='royalty-distributions')
router.register(r'royalties', views.InvestorRoyaltyViewSet, basename='investor-royalties')
router.register(r'analytics', views.RevenueAnalyticsViewSet, basename='revenue-analytics')

urlpatterns = [
    path('', include(router.urls)),
    
    # Webhook endpoints
    path('webhooks/netflix/', webhook_views.NetflixWebhookView.as_view(), name='netflix-webhook'),
    path('webhooks/amazon-prime/', webhook_views.AmazonPrimeWebhookView.as_view(), name='amazon-prime-webhook'),
    path('webhooks/disney-plus/', webhook_views.DisneyPlusWebhookView.as_view(), name='disney-plus-webhook'),
    path('webhooks/<str:platform_name>/', webhook_views.GenericOTTWebhookView.as_view(), name='generic-ott-webhook'),
    
    # Webhook management
    path('webhooks/status/<int:webhook_id>/', webhook_views.webhook_status, name='webhook-status'),
    path('webhooks/test/<str:platform_name>/', webhook_views.test_webhook, name='test-webhook'),
    path('integrations/', webhook_views.platform_integrations, name='platform-integrations'),
]