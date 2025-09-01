from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment methods
    path('methods/', views.PaymentMethodListView.as_view(), name='payment-method-list'),
    path('methods/<int:pk>/', views.PaymentMethodDetailView.as_view(), name='payment-method-detail'),
    
    # Transactions
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('transactions/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
    path('transactions/create/', views.TransactionCreateView.as_view(), name='transaction-create'),
    
    # Contributions
    path('contributions/', views.ContributionListView.as_view(), name='contribution-list'),
    path('contributions/<int:pk>/', views.ContributionDetailView.as_view(), name='contribution-detail'),
    path('contributions/create/', views.ContributionCreateView.as_view(), name='contribution-create'),
    
    # Refunds
    path('refunds/', views.RefundListView.as_view(), name='refund-list'),
    path('refunds/<int:pk>/', views.RefundDetailView.as_view(), name='refund-detail'),
    path('refunds/create/', views.RefundCreateView.as_view(), name='refund-create'),
    
    # Payment providers
    path('providers/', views.PaymentProviderListView.as_view(), name='provider-list'),
    path('providers/<int:pk>/', views.PaymentProviderDetailView.as_view(), name='provider-detail'),
    
    # Payment processing
    path('process/', views.PaymentProcessView.as_view(), name='payment-process'),
    path('webhook/<str:provider>/', views.PaymentWebhookView.as_view(), name='payment-webhook'),
    path('callback/<str:provider>/', views.PaymentCallbackView.as_view(), name='payment-callback'),
    
    # Payment verification
    path('verify/<str:transaction_id>/', views.PaymentVerificationView.as_view(), name='payment-verify'),
    path('status/<str:transaction_id>/', views.PaymentStatusView.as_view(), name='payment-status'),
    
    # Payment analytics
    path('analytics/', views.PaymentAnalyticsView.as_view(), name='payment-analytics'),
    path('reports/', views.PaymentReportView.as_view(), name='payment-reports'),
]

