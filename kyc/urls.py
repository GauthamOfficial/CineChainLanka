from django.urls import path
from . import views

app_name = 'kyc'

urlpatterns = [
    # KYC requests
    path('requests/', views.KYCRequestListView.as_view(), name='kyc-request-list'),
    path('requests/create/', views.KYCRequestCreateView.as_view(), name='kyc-request-create'),
    path('requests/<int:pk>/', views.KYCRequestDetailView.as_view(), name='kyc-request-detail'),
    path('requests/<int:pk>/update/', views.KYCRequestUpdateView.as_view(), name='kyc-request-update'),
    path('requests/<int:pk>/submit/', views.KYCRequestSubmitView.as_view(), name='kyc-request-submit'),
    
    # KYC verifications
    path('verifications/', views.KYCVerificationListView.as_view(), name='verification-list'),
    path('verifications/<int:pk>/', views.KYCVerificationDetailView.as_view(), name='verification-detail'),
    path('verifications/<int:pk>/update/', views.KYCVerificationUpdateView.as_view(), name='verification-update'),
    
    # KYC documents
    path('documents/', views.KYCDocumentListView.as_view(), name='document-list'),
    path('documents/upload/', views.KYCDocumentUploadView.as_view(), name='document-upload'),
    path('documents/<int:pk>/', views.KYCDocumentDetailView.as_view(), name='document-detail'),
    path('documents/<int:pk>/update/', views.KYCDocumentUpdateView.as_view(), name='document-update'),
    path('documents/<int:pk>/delete/', views.KYCDocumentDeleteView.as_view(), name='document-delete'),
    
    # KYC compliance checks
    path('compliance/', views.KYCComplianceCheckListView.as_view(), name='compliance-check-list'),
    path('compliance/<int:pk>/', views.KYCComplianceCheckDetailView.as_view(), name='compliance-check-detail'),
    path('compliance/<int:pk>/update/', views.KYCComplianceCheckUpdateView.as_view(), name='compliance-check-update'),
    
    # KYC review and approval
    path('review/', views.KYCReviewListView.as_view(), name='review-list'),
    path('review/<int:pk>/', views.KYCReviewDetailView.as_view(), name='review-detail'),
    path('review/<int:pk>/approve/', views.KYCApproveView.as_view(), name='approve-kyc'),
    path('review/<int:pk>/reject/', views.KYCRejectView.as_view(), name='reject-kyc'),
    path('review/<int:pk>/request-info/', views.KYCRequestInfoView.as_view(), name='request-info'),
    
    # KYC status and tracking
    path('status/', views.KYCStatusView.as_view(), name='kyc-status'),
    path('tracking/<int:pk>/', views.KYCTrackingView.as_view(), name='kyc-tracking'),
    
    # KYC analytics and reporting
    path('analytics/', views.KYCAnalyticsView.as_view(), name='kyc-analytics'),
    path('reports/', views.KYCReportView.as_view(), name='kyc-reports'),
]

