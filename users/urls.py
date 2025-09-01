from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # User management
    path('', views.UserListView.as_view(), name='user-list'),
    path('me/', views.UserDetailView.as_view(), name='user-detail'),
    path('profile/', views.CurrentUserProfileView.as_view(), name='user-profile'),
    path('profile/<int:pk>/', views.UserProfileView.as_view(), name='user-profile-detail'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='user-profile-update'),
    path('test/', views.TestProfileView.as_view(), name='test-profile'),
    
    # User documents
    path('documents/', views.UserDocumentListView.as_view(), name='user-document-list'),
    path('documents/<int:pk>/', views.UserDocumentDetailView.as_view(), name='user-document-detail'),
    path('documents/upload/', views.UserDocumentUploadView.as_view(), name='user-document-upload'),
    
    # User search and discovery
    path('search/', views.UserSearchView.as_view(), name='user-search'),
    path('creators/', views.CreatorListView.as_view(), name='creator-list'),
    path('investors/', views.InvestorListView.as_view(), name='investor-list'),
    
    # User statistics
    path('stats/', views.UserStatsView.as_view(), name='user-stats'),
]

