from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import (
    KYCRequest, KYCVerification, KYCDocument, KYCComplianceCheck
)


@admin.register(KYCRequest)
class KYCRequestAdmin(admin.ModelAdmin):
    """
    Admin configuration for KYCRequest model
    """
    list_display = [
        'user', 'verification_level', 'status', 'legal_name',
        'nationality', 'submitted_at', 'reviewed_at'
    ]
    
    list_filter = [
        'status', 'verification_level', 'nationality', 'source_of_funds',
        'employment_status', 'political_exposure', 'submitted_at',
        'reviewed_at', 'created_at'
    ]
    
    search_fields = [
        'user__username', 'user__email', 'legal_name',
        'identity_document_number', 'employer_name'
    ]
    
    ordering = ['-submitted_at']
    
    list_per_page = 25
    
    # Fieldsets for editing
    fieldsets = (
        (_('User Information'), {
            'fields': ('user', 'verification_level', 'status')
        }),
        (_('Personal Information'), {
            'fields': (
                'legal_name', 'date_of_birth', 'nationality'
            )
        }),
        (_('Address Information'), {
            'fields': ('residential_address',)
        }),
        (_('Identity Verification'), {
            'fields': (
                'identity_document_type', 'identity_document_number',
                'identity_document_expiry'
            )
        }),
        (_('Address Verification'), {
            'fields': (
                'address_proof_type', 'address_proof_date'
            )
        }),
        (_('Financial Information'), {
            'fields': (
                'source_of_funds', 'annual_income', 'employment_status',
                'employer_name'
            )
        }),
        (_('Risk Assessment'), {
            'fields': (
                'political_exposure', 'politically_exposed_person',
                'sanctions_check'
            )
        }),
        (_('Review Information'), {
            'fields': (
                'reviewed_by', 'reviewed_at', 'review_notes',
                'rejection_reason'
            )
        }),
    )
    
    readonly_fields = [
        'submitted_at', 'created_at', 'updated_at'
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'reviewed_by'
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
                    '<a href="{}" class="button">Review</a>',
                    reverse('admin:kyc_kycrequest_change', args=[obj.id])
                )
            )
        elif obj.status == 'under_review':
            actions.append(
                format_html(
                    '<a href="{}" class="button">Continue Review</a>',
                    reverse('admin:kyc_kycrequest_change', args=[obj.id])
                )
            )
        elif obj.status == 'requires_additional_info':
            actions.append(
                format_html(
                    '<a href="{}" class="button">Request Info</a>',
                    reverse('admin:kyc_kycrequest_change', args=[obj.id])
                )
            )
        return format_html(' '.join(actions)) if actions else '-'
    admin_actions.short_description = _('Actions')
    
    actions = ['approve_kyc', 'reject_kyc', 'request_additional_info']
    
    def approve_kyc(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status__in=['pending', 'under_review']).update(
            status='approved',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(
            request,
            f'{updated} KYC request(s) were successfully approved.'
        )
    approve_kyc.short_description = _('Approve selected KYC requests')
    
    def reject_kyc(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status__in=['pending', 'under_review']).update(
            status='rejected',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(
            request,
            f'{updated} KYC request(s) were successfully rejected.'
        )
    reject_kyc.short_description = _('Reject selected KYC requests')
    
    def request_additional_info(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status__in=['pending', 'under_review']).update(
            status='requires_additional_info',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(
            request,
            f'{updated} KYC request(s) were marked as requiring additional information.'
        )
    request_additional_info.short_description = _('Mark selected KYC requests as requiring additional information')


@admin.register(KYCVerification)
class KYCVerificationAdmin(admin.ModelAdmin):
    """
    Admin configuration for KYCVerification model
    """
    list_display = [
        'kyc_request', 'verification_type', 'status', 'is_verified',
        'confidence_score', 'started_at', 'completed_at'
    ]
    
    list_filter = [
        'verification_type', 'status', 'verification_provider',
        'started_at', 'completed_at'
    ]
    
    search_fields = [
        'kyc_request__user__username', 'kyc_request__user__email',
        'verification_reference'
    ]
    
    ordering = ['-started_at']
    
    fieldsets = (
        (_('Verification Information'), {
            'fields': (
                'kyc_request', 'verification_type', 'status'
            )
        }),
        (_('Verification Details'), {
            'fields': (
                'verification_method', 'verification_provider',
                'verification_reference'
            )
        }),
        (_('Results'), {
            'fields': (
                'is_verified', 'confidence_score', 'verification_data'
            )
        }),
        (_('Timing'), {
            'fields': ('started_at', 'completed_at')
        }),
        (_('Notes & Errors'), {
            'fields': ('notes', 'error_message')
        }),
    )
    
    readonly_fields = [
        'started_at', 'created_at', 'updated_at'
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('kyc_request__user')
    
    actions = ['mark_as_completed', 'mark_as_failed']
    
    def mark_as_completed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='in_progress').update(
            status='completed',
            completed_at=timezone.now()
        )
        self.message_user(
            request,
            f'{updated} verification(s) were successfully marked as completed.'
        )
    mark_as_completed.short_description = _('Mark selected verifications as completed')
    
    def mark_as_failed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='in_progress').update(
            status='failed',
            completed_at=timezone.now()
        )
        self.message_user(
            request,
            f'{updated} verification(s) were successfully marked as failed.'
        )
    mark_as_failed.short_description = _('Mark selected verifications as failed')


@admin.register(KYCDocument)
class KYCDocumentAdmin(admin.ModelAdmin):
    """
    Admin configuration for KYCDocument model
    """
    list_display = [
        'kyc_request', 'document_type', 'document_name',
        'document_number', 'status', 'verified_by',
        'created_at'
    ]
    
    list_filter = [
        'document_type', 'status', 'created_at',
        'verified_at'
    ]
    
    search_fields = [
        'kyc_request__user__username', 'kyc_request__user__email',
        'document_name', 'document_number'
    ]
    
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Document Information'), {
            'fields': (
                'kyc_request', 'document_type', 'document_name',
                'document_number'
            )
        }),
        (_('Document File'), {
            'fields': ('document_file',)
        }),
        (_('Document Details'), {
            'fields': (
                'issue_date', 'expiry_date', 'issuing_authority'
            )
        }),
        (_('Verification Status'), {
            'fields': (
                'status', 'is_verified', 'verified_by', 'verified_at'
            )
        }),
        (_('Notes'), {
            'fields': ('verification_notes', 'rejection_reason')
        }),
    )
    
    readonly_fields = [
        'created_at', 'updated_at', 'file_size'
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'kyc_request__user', 'verified_by'
        )
    
    def save_model(self, request, obj, form, change):
        if not change and obj.is_verified:
            obj.verified_by = request.user
        super().save_model(request, obj, form, change)
    
    actions = ['verify_documents', 'reject_documents']
    
    def verify_documents(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='verified',
            is_verified=True,
            verified_by=request.user,
            verified_at=timezone.now()
        )
        self.message_user(
            request,
            f'{updated} document(s) were successfully verified.'
        )
    verify_documents.short_description = _('Verify selected documents')
    
    def reject_documents(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='rejected',
            is_verified=False
        )
        self.message_user(
            request,
            f'{updated} document(s) were successfully rejected.'
        )
    reject_documents.short_description = _('Reject selected documents')


@admin.register(KYCComplianceCheck)
class KYCComplianceCheckAdmin(admin.ModelAdmin):
    """
    Admin configuration for KYCComplianceCheck model
    """
    list_display = [
        'kyc_request', 'check_type', 'status', 'risk_score',
        'risk_level', 'initiated_at', 'completed_at'
    ]
    
    list_filter = [
        'check_type', 'status', 'risk_level', 'initiated_at',
        'completed_at'
    ]
    
    search_fields = [
        'kyc_request__user__username', 'kyc_request__user__email',
        'check_reference'
    ]
    
    ordering = ['-initiated_at']
    
    fieldsets = (
        (_('Check Information'), {
            'fields': (
                'kyc_request', 'check_type', 'status'
            )
        }),
        (_('Check Details'), {
            'fields': (
                'check_provider', 'check_reference'
            )
        }),
        (_('Results'), {
            'fields': (
                'risk_score', 'risk_level', 'check_data'
            )
        }),
        (_('Timing'), {
            'fields': ('initiated_at', 'completed_at')
        }),
        (_('Findings'), {
            'fields': ('notes', 'findings')
        }),
    )
    
    readonly_fields = [
        'initiated_at', 'created_at', 'updated_at'
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('kyc_request__user')
    
    actions = ['mark_as_passed', 'mark_as_failed']
    
    def mark_as_passed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='passed',
            completed_at=timezone.now()
        )
        self.message_user(
            request,
            f'{updated} compliance check(s) were successfully marked as passed.'
        )
    mark_as_passed.short_description = _('Mark selected compliance checks as passed')
    
    def mark_as_failed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='failed',
            completed_at=timezone.now()
        )
        self.message_user(
            request,
            f'{updated} compliance check(s) were successfully marked as failed.'
        )
    mark_as_failed.short_description = _('Mark selected compliance checks as failed')
