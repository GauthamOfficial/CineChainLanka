from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreatorAnalyticsViewSet, InvestorAnalyticsViewSet

router = DefaultRouter()
router.register(r'creator', CreatorAnalyticsViewSet, basename='creator-analytics')
router.register(r'investor', InvestorAnalyticsViewSet, basename='investor-analytics')

urlpatterns = [
    path('', include(router.urls)),
]
