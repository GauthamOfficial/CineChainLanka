from django.urls import path
from . import views

app_name = 'campaigns'

urlpatterns = [
    # Campaign management
    path('', views.CampaignListView.as_view(), name='campaign-list'),
    path('create/', views.CampaignCreateView.as_view(), name='campaign-create'),
    path('<int:pk>/', views.CampaignDetailView.as_view(), name='campaign-detail'),
    path('<int:pk>/update/', views.CampaignUpdateView.as_view(), name='campaign-update'),
    path('<int:pk>/delete/', views.CampaignDeleteView.as_view(), name='campaign-delete'),
    
    # Campaign categories
    path('categories/', views.CampaignCategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CampaignCategoryDetailView.as_view(), name='category-detail'),
    
    # Campaign rewards
    path('<int:campaign_pk>/rewards/', views.CampaignRewardListView.as_view(), name='reward-list'),
    path('<int:campaign_pk>/rewards/create/', views.CampaignRewardCreateView.as_view(), name='reward-create'),
    path('rewards/<int:pk>/', views.CampaignRewardDetailView.as_view(), name='reward-detail'),
    path('rewards/<int:pk>/update/', views.CampaignRewardUpdateView.as_view(), name='reward-update'),
    path('rewards/<int:pk>/delete/', views.CampaignRewardDeleteView.as_view(), name='reward-delete'),
    
    # Campaign updates
    path('<int:campaign_pk>/updates/', views.CampaignUpdateListView.as_view(), name='update-list'),
    path('<int:campaign_pk>/updates/create/', views.CampaignUpdateCreateView.as_view(), name='update-create'),
    path('updates/<int:pk>/', views.CampaignUpdateDetailView.as_view(), name='update-detail'),
    path('updates/<int:pk>/update/', views.CampaignUpdateUpdateView.as_view(), name='update-update'),
    path('updates/<int:pk>/delete/', views.CampaignUpdateDeleteView.as_view(), name='update-delete'),
    
    # Campaign comments
    path('<int:campaign_pk>/comments/', views.CampaignCommentListView.as_view(), name='comment-list'),
    path('<int:campaign_pk>/comments/create/', views.CampaignCommentCreateView.as_view(), name='comment-create'),
    path('comments/<int:pk>/', views.CampaignCommentDetailView.as_view(), name='comment-detail'),
    path('comments/<int:pk>/update/', views.CampaignCommentUpdateView.as_view(), name='comment-update'),
    path('comments/<int:pk>/delete/', views.CampaignCommentDeleteView.as_view(), name='comment-delete'),
    
    # Campaign search and discovery
    path('search/', views.CampaignSearchView.as_view(), name='campaign-search'),
    path('featured/', views.FeaturedCampaignListView.as_view(), name='featured-campaigns'),
    path('trending/', views.TrendingCampaignListView.as_view(), name='trending-campaigns'),
    
    # Campaign actions
    path('<int:pk>/like/', views.CampaignLikeView.as_view(), name='campaign-like'),
    path('<int:pk>/unlike/', views.CampaignUnlikeView.as_view(), name='campaign-unlike'),
    path('<int:pk>/share/', views.CampaignShareView.as_view(), name='campaign-share'),
    path('<int:pk>/report/', views.CampaignReportView.as_view(), name='campaign-report'),
    
    # Campaign statistics
    path('<int:pk>/stats/', views.CampaignStatsView.as_view(), name='campaign-stats'),
    path('<int:pk>/analytics/', views.CampaignAnalyticsView.as_view(), name='campaign-analytics'),
]

