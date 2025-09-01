from django.urls import path
from . import views

app_name = 'funding'

urlpatterns = [
    # Funding rounds
    path('rounds/', views.FundingRoundListView.as_view(), name='round-list'),
    path('rounds/create/', views.FundingRoundCreateView.as_view(), name='round-create'),
    path('rounds/<int:pk>/', views.FundingRoundDetailView.as_view(), name='round-detail'),
    path('rounds/<int:pk>/update/', views.FundingRoundUpdateView.as_view(), name='round-update'),
    path('rounds/<int:pk>/delete/', views.FundingRoundDeleteView.as_view(), name='round-delete'),
    
    # Funding milestones
    path('milestones/', views.FundingMilestoneListView.as_view(), name='milestone-list'),
    path('milestones/create/', views.FundingMilestoneCreateView.as_view(), name='milestone-create'),
    path('milestones/<int:pk>/', views.FundingMilestoneDetailView.as_view(), name='milestone-detail'),
    path('milestones/<int:pk>/update/', views.FundingMilestoneUpdateView.as_view(), name='milestone-update'),
    path('milestones/<int:pk>/delete/', views.FundingMilestoneDeleteView.as_view(), name='milestone-delete'),
    
    # Funding allocations
    path('allocations/', views.FundingAllocationListView.as_view(), name='allocation-list'),
    path('allocations/create/', views.FundingAllocationCreateView.as_view(), name='allocation-create'),
    path('allocations/<int:pk>/', views.FundingAllocationDetailView.as_view(), name='allocation-detail'),
    path('allocations/<int:pk>/update/', views.FundingAllocationUpdateView.as_view(), name='allocation-update'),
    path('allocations/<int:pk>/delete/', views.FundingAllocationDeleteView.as_view(), name='allocation-delete'),
    
    # Funding progress
    path('progress/', views.FundingProgressListView.as_view(), name='progress-list'),
    path('progress/<int:pk>/', views.FundingProgressDetailView.as_view(), name='progress-detail'),
    
    # Funding analytics
    path('analytics/', views.FundingAnalyticsListView.as_view(), name='analytics-list'),
    path('analytics/<int:pk>/', views.FundingAnalyticsDetailView.as_view(), name='analytics-detail'),
    
    # Funding dashboard
    path('dashboard/', views.FundingDashboardView.as_view(), name='funding-dashboard'),
    path('dashboard/creator/', views.CreatorDashboardView.as_view(), name='creator-dashboard'),
    path('dashboard/investor/', views.InvestorDashboardView.as_view(), name='investor-dashboard'),
    
    # Funding reports
    path('reports/', views.FundingReportView.as_view(), name='funding-reports'),
    path('reports/campaign/<int:campaign_pk>/', views.CampaignFundingReportView.as_view(), name='campaign-funding-report'),
    path('reports/user/<int:user_pk>/', views.UserFundingReportView.as_view(), name='user-funding-report'),
]
