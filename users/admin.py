from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, UserDocument


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin configuration for the custom User model
    """
    list_display = [
        'username', 'email', 'full_name', 'user_type', 'kyc_status', 
        'is_active', 'date_joined', 'last_login'
    ]
    
    list_filter = [
        'user_type', 'kyc_status', 'is_active', 'is_staff', 'is_superuser',
        'preferred_language', 'creator_verified', 'date_joined'
    ]
    
    search_fields = [
        'username', 'email', 'first_name', 'last_name', 'phone_number'
    ]
    
    ordering = ['-date_joined']
    
    list_per_page = 25
    
    # Fieldsets for editing
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal Information'), {
            'fields': (
                'first_name', 'last_name', 'email', 'phone_number',
                'profile_picture', 'bio', 'date_of_birth'
            )
        }),
        (_('Address Information'), {
            'fields': (
                'address_line1', 'address_line2', 'city', 'state_province',
                'postal_code', 'country'
            )
        }),
        (_('Account Settings'), {
            'fields': (
                'user_type', 'preferred_language', 'email_notifications',
                'sms_notifications'
            )
        }),
        (_('KYC & Verification'), {
            'fields': (
                'kyc_status', 'kyc_submitted_at', 'kyc_verified_at',
                'creator_verified', 'creator_category'
            )
        }),
        (_('Investment Settings'), {
            'fields': ('investment_limit',)
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'groups',
                'user_permissions'
            )
        }),
        (_('Important Dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'user_type', 'is_active', 'is_staff'
            ),
        }),
    )
    
    readonly_fields = [
        'kyc_submitted_at', 'kyc_verified_at', 'last_login', 'date_joined'
    ]
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = _('Full Name')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('extended_profile')
    
    def get_list_display(self, request):
        list_display = list(super().get_list_display(request))
        if request.user.is_superuser:
            list_display.append('kyc_actions')
        return list_display
    
    def kyc_actions(self, obj):
        if obj.kyc_status == 'pending':
            return format_html(
                '<a href="{}" class="button">Review KYC</a>',
                reverse('admin:kyc_kycrequest_change', args=[obj.kyc_request.id])
                if hasattr(obj, 'kyc_request') else '#'
            )
        return obj.get_kyc_status_display()
    kyc_actions.short_description = _('KYC Actions')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserProfile model
    """
    list_display = [
        'user', 'occupation', 'company', 'experience_years',
        'annual_income_range', 'created_at'
    ]
    
    list_filter = [
        'occupation', 'annual_income_range', 'experience_years',
        'created_at'
    ]
    
    search_fields = [
        'user__username', 'user__email', 'occupation', 'company'
    ]
    
    ordering = ['-created_at']
    
    fieldsets = (
        (_('User'), {'fields': ('user',)}),
        (_('Professional Information'), {
            'fields': (
                'occupation', 'company', 'experience_years'
            )
        }),
        (_('Social Media'), {
            'fields': (
                'website', 'facebook', 'twitter', 'instagram', 'linkedin'
            )
        }),
        (_('Portfolio'), {
            'fields': ('portfolio_description', 'awards')
        }),
        (_('Financial Information'), {
            'fields': ('annual_income_range',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(UserDocument)
class UserDocumentAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserDocument model
    """
    list_display = [
        'user', 'document_type', 'document_number', 'is_verified',
        'verified_by', 'created_at'
    ]
    
    list_filter = [
        'document_type', 'is_verified', 'created_at', 'verified_at'
    ]
    
    search_fields = [
        'user__username', 'user__email', 'document_number',
        'document_name'
    ]
    
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Document Information'), {
            'fields': (
                'user', 'document_type', 'document_name', 'document_number'
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
        (_('Verification'), {
            'fields': (
                'is_verified', 'verified_by', 'verified_at', 'notes'
            )
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'verified_by')
    
    def save_model(self, request, obj, form, change):
        if not change and obj.is_verified:
            obj.verified_by = request.user
        super().save_model(request, obj, form, change)


# Customize admin site
admin.site.site_header = _('CineChainLanka Administration')
admin.site.site_title = _('CineChainLanka Admin')
admin.site.index_title = _('Welcome to CineChainLanka Administration')
