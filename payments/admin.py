from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import (
    PaymentMethod, Transaction, Contribution, Refund, PaymentProvider
)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """
    Admin configuration for PaymentMethod model
    """
    list_display = [
        'name', 'payment_type', 'is_active', 'processing_fee_percentage',
        'processing_fee_fixed', 'minimum_amount', 'maximum_amount'
    ]
    
    list_filter = [
        'payment_type', 'is_active', 'created_at'
    ]
    
    search_fields = ['name', 'description']
    
    ordering = ['name']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'payment_type', 'description', 'is_active')
        }),
        (_('Fee Structure'), {
            'fields': (
                'processing_fee_percentage', 'processing_fee_fixed'
            )
        }),
        (_('Amount Limits'), {
            'fields': ('minimum_amount', 'maximum_amount')
        }),
        (_('Configuration'), {
            'fields': ('config_data',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Admin configuration for Transaction model
    """
    list_display = [
        'transaction_id', 'user', 'campaign', 'transaction_type',
        'amount', 'net_amount', 'payment_method', 'status',
        'initiated_at', 'completed_at'
    ]
    
    list_filter = [
        'status', 'transaction_type', 'payment_method__payment_type',
        'initiated_at', 'completed_at', 'created_at'
    ]
    
    search_fields = [
        'transaction_id', 'reference_id', 'user__username',
        'user__email', 'campaign__title'
    ]
    
    ordering = ['-initiated_at']
    
    list_per_page = 50
    
    # Fieldsets for editing
    fieldsets = (
        (_('Transaction Information'), {
            'fields': (
                'transaction_id', 'reference_id', 'transaction_type'
            )
        }),
        (_('User & Campaign'), {
            'fields': ('user', 'campaign', 'reward')
        }),
        (_('Amount Details'), {
            'fields': (
                'amount', 'processing_fee', 'net_amount'
            )
        }),
        (_('Payment Method'), {
            'fields': ('payment_method',)
        }),
        (_('Status & Timing'), {
            'fields': (
                'status', 'initiated_at', 'processed_at', 'completed_at'
            )
        }),
        (_('Error Information'), {
            'fields': ('error_message', 'failure_reason')
        }),
        (_('Additional Data'), {
            'fields': ('metadata',)
        }),
    )
    
    readonly_fields = [
        'transaction_id', 'initiated_at', 'processed_at', 'completed_at',
        'created_at', 'updated_at'
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'campaign', 'reward', 'payment_method'
        )
    
    def get_list_display(self, request):
        list_display = list(super().get_list_display(request))
        if request.user.is_superuser:
            list_display.append('admin_actions')
        return list_display
    
    def admin_actions(self, obj):
        actions = []
        if obj.status == 'pending':
            actions.append(
                format_html(
                    '<a href="{}" class="button">Process</a>',
                    reverse('admin:payments_transaction_change', args=[obj.id])
                )
            )
        if obj.status == 'failed':
            actions.append(
                format_html(
                    '<a href="{}" class="button">Retry</a>',
                    reverse('admin:payments_transaction_change', args=[obj.id])
                )
            )
        return format_html(' '.join(actions)) if actions else '-'
    admin_actions.short_description = _('Actions')
    
    actions = ['mark_as_completed', 'mark_as_failed']
    
    def mark_as_completed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            status='completed',
            completed_at=timezone.now()
        )
        self.message_user(
            request,
            f'{updated} transaction(s) were successfully marked as completed.'
        )
    mark_as_completed.short_description = _('Mark selected transactions as completed')
    
    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status='failed')
        self.message_user(
            request,
            f'{updated} transaction(s) were successfully marked as failed.'
        )
    mark_as_failed.short_description = _('Mark selected transactions as failed')


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    """
    Admin configuration for Contribution model
    """
    list_display = [
        'user', 'campaign', 'amount', 'reward', 'is_anonymous',
        'created_at'
    ]
    
    list_filter = [
        'is_anonymous', 'campaign__status', 'campaign__category',
        'created_at'
    ]
    
    search_fields = [
        'user__username', 'user__email', 'campaign__title',
        'message'
    ]
    
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Contribution Information'), {
            'fields': (
                'user', 'campaign', 'reward', 'transaction'
            )
        }),
        (_('Contribution Details'), {
            'fields': ('amount', 'is_anonymous', 'message')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'campaign', 'reward', 'transaction'
        )


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    """
    Admin configuration for Refund model
    """
    list_display = [
        'original_transaction', 'amount', 'status', 'reason',
        'processed_by', 'processed_at', 'created_at'
    ]
    
    list_filter = [
        'status', 'created_at', 'processed_at'
    ]
    
    search_fields = [
        'reason', 'notes', 'original_transaction__transaction_id'
    ]
    
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Refund Information'), {
            'fields': (
                'original_transaction', 'refund_transaction', 'amount'
            )
        }),
        (_('Refund Details'), {
            'fields': ('reason', 'status')
        }),
        (_('Processing'), {
            'fields': (
                'processed_by', 'processed_at', 'notes'
            )
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'original_transaction', 'refund_transaction', 'processed_by'
        )
    
    def save_model(self, request, obj, form, change):
        if not change and obj.status == 'completed':
            obj.processed_by = request.user
        super().save_model(request, obj, form, change)
    
    actions = ['process_refunds', 'mark_as_completed']
    
    def process_refunds(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='processing',
            processed_at=timezone.now()
        )
        self.message_user(
            request,
            f'{updated} refund(s) were successfully marked as processing.'
        )
    process_refunds.short_description = _('Mark selected refunds as processing')
    
    def mark_as_completed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='processing').update(
            status='completed',
            processed_at=timezone.now()
        )
        self.message_user(
            request,
            f'{updated} refund(s) were successfully marked as completed.'
        )
    mark_as_completed.short_description = _('Mark selected refunds as completed')


@admin.register(PaymentProvider)
class PaymentProviderAdmin(admin.ModelAdmin):
    """
    Admin configuration for PaymentProvider model
    """
    list_display = [
        'name', 'provider_type', 'is_active', 'api_endpoint',
        'created_at'
    ]
    
    list_filter = [
        'provider_type', 'is_active', 'created_at'
    ]
    
    search_fields = ['name', 'api_endpoint']
    
    ordering = ['name']
    
    fieldsets = (
        (_('Provider Information'), {
            'fields': ('name', 'provider_type', 'is_active')
        }),
        (_('API Configuration'), {
            'fields': (
                'api_key', 'api_secret', 'webhook_secret'
            )
        }),
        (_('Endpoints'), {
            'fields': ('api_endpoint', 'webhook_endpoint')
        }),
        (_('Additional Configuration'), {
            'fields': ('config_data',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not request.user.is_superuser:
            # Hide sensitive fields from non-superusers
            fieldsets = list(fieldsets)
            for i, (title, field_dict) in enumerate(fieldsets):
                if 'API Configuration' in title:
                    fieldsets[i] = (title, {
                        'fields': ('is_active',),
                        'description': 'API configuration is only visible to superusers.'
                    })
        return fieldsets
