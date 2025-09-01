from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import (
    FundingRound, FundingMilestone, FundingAllocation,
    FundingProgress, FundingAnalytics
)


@admin.register(FundingRound)
class FundingRoundAdmin(admin.ModelAdmin):
    """
    Admin configuration for FundingRound model
    """
    list_display = [
        'title', 'campaign', 'round_type', 'funding_goal',
        'current_funding', 'funding_percentage', 'is_active',
        'start_date', 'end_date'
    ]
    
    list_filter = [
        'round_type', 'is_active', 'campaign__status',
        'start_date', 'end_date', 'created_at'
    ]
    
    search_fields = [
        'title', 'description', 'campaign__title',
        'campaign__creator__username'
    ]
    
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Round Information'), {
            'fields': (
                'campaign', 'round_type', 'title', 'description'
            )
        }),
        (_('Funding Details'), {
            'fields': ('funding_goal', 'current_funding')
        }),
        (_('Timeline'), {
            'fields': ('start_date', 'end_date')
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ['current_funding', 'created_at', 'updated_at']
    
    def funding_percentage(self, obj):
        return f"{obj.funding_percentage:.1f}%"
    funding_percentage.short_description = _('Funding %')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('campaign')


@admin.register(FundingMilestone)
class FundingMilestoneAdmin(admin.ModelAdmin):
    """
    Admin configuration for FundingMilestone model
    """
    list_display = [
        'title', 'campaign', 'funding_target', 'is_achieved',
        'achieved_at', 'order', 'created_at'
    ]
    
    list_filter = [
        'is_achieved', 'campaign__status', 'campaign__category',
        'created_at'
    ]
    
    search_fields = [
        'title', 'description', 'campaign__title',
        'campaign__creator__username'
    ]
    
    ordering = ['campaign', 'order']
    
    fieldsets = (
        (_('Milestone Information'), {
            'fields': (
                'campaign', 'title', 'description', 'funding_target'
            )
        }),
        (_('Status'), {
            'fields': ('is_achieved', 'achieved_at', 'order')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('campaign')
    
    actions = ['mark_as_achieved', 'mark_as_not_achieved']
    
    def mark_as_achieved(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(is_achieved=False).update(
            is_achieved=True,
            achieved_at=timezone.now()
        )
        self.message_user(
            request,
            f'{updated} milestone(s) were successfully marked as achieved.'
        )
    mark_as_achieved.short_description = _('Mark selected milestones as achieved')
    
    def mark_as_not_achieved(self, request, queryset):
        updated = queryset.filter(is_achieved=True).update(
            is_achieved=False,
            achieved_at=None
        )
        self.message_user(
            request,
            f'{updated} milestone(s) were successfully marked as not achieved.'
        )
    mark_as_not_achieved.short_description = _('Mark selected milestones as not achieved')


@admin.register(FundingAllocation)
class FundingAllocationAdmin(admin.ModelAdmin):
    """
    Admin configuration for FundingAllocation model
    """
    list_display = [
        'campaign', 'allocation_type', 'budgeted_amount',
        'actual_amount', 'remaining_budget', 'spending_percentage',
        'percentage_of_total'
    ]
    
    list_filter = [
        'allocation_type', 'campaign__status', 'campaign__category',
        'created_at'
    ]
    
    search_fields = [
        'description', 'campaign__title', 'campaign__creator__username'
    ]
    
    ordering = ['campaign', 'percentage_of_total']
    
    fieldsets = (
        (_('Allocation Information'), {
            'fields': (
                'campaign', 'allocation_type', 'description'
            )
        }),
        (_('Budget Details'), {
            'fields': (
                'budgeted_amount', 'actual_amount', 'percentage_of_total'
            )
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def remaining_budget(self, obj):
        return f"LKR {obj.remaining_budget:,.2f}"
    remaining_budget.short_description = _('Remaining Budget')
    
    def spending_percentage(self, obj):
        return f"{obj.spending_percentage:.1f}%"
    spending_percentage.short_description = _('Spending %')
    
    def percentage_of_total(self, obj):
        return f"{obj.percentage_of_total:.1f}%"
    percentage_of_total.short_description = _('Total %')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('campaign')


@admin.register(FundingProgress)
class FundingProgressAdmin(admin.ModelAdmin):
    """
    Admin configuration for FundingProgress model
    """
    list_display = [
        'campaign', 'date', 'total_funding', 'daily_funding',
        'backer_count', 'new_backers'
    ]
    
    list_filter = [
        'campaign__status', 'campaign__category', 'date',
        'created_at'
    ]
    
    search_fields = [
        'campaign__title', 'campaign__creator__username'
    ]
    
    ordering = ['-date', 'campaign']
    
    fieldsets = (
        (_('Progress Information'), {
            'fields': (
                'campaign', 'date', 'total_funding', 'daily_funding'
            )
        }),
        (_('Backer Information'), {
            'fields': ('backer_count', 'new_backers')
        }),
    )
    
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('campaign')
    
    def has_add_permission(self, request):
        # Progress records are typically created automatically
        return False
    
    def has_change_permission(self, request, obj=None):
        # Progress records should not be manually edited
        return False


@admin.register(FundingAnalytics)
class FundingAnalyticsAdmin(admin.ModelAdmin):
    """
    Admin configuration for FundingAnalytics model
    """
    list_display = [
        'campaign', 'total_contributions', 'average_contribution',
        'unique_backers', 'repeat_backer_rate', 'funding_efficiency',
        'updated_at'
    ]
    
    list_filter = [
        'campaign__status', 'campaign__category', 'created_at',
        'updated_at'
    ]
    
    search_fields = [
        'campaign__title', 'campaign__creator__username'
    ]
    
    ordering = ['-updated_at']
    
    fieldsets = (
        (_('Campaign'), {
            'fields': ('campaign',)
        }),
        (_('Funding Metrics'), {
            'fields': (
                'total_contributions', 'average_contribution',
                'median_contribution', 'largest_contribution'
            )
        }),
        (_('Backer Metrics'), {
            'fields': (
                'unique_backers', 'repeat_backers', 'new_backers'
            )
        }),
        (_('Conversion Metrics'), {
            'fields': ('view_to_backer_rate',)
        }),
        (_('Geographic & Payment Distribution'), {
            'fields': (
                'top_locations', 'payment_method_distribution'
            )
        }),
        (_('Time-based Metrics'), {
            'fields': (
                'peak_funding_day', 'peak_funding_amount'
            )
        }),
        (_('Projections'), {
            'fields': (
                'projected_completion_date', 'funding_velocity'
            )
        }),
    )
    
    readonly_fields = [
        'created_at', 'updated_at'
    ]
    
    def repeat_backer_rate(self, obj):
        return f"{obj.repeat_backer_rate:.1f}%"
    repeat_backer_rate.short_description = _('Repeat Backer Rate')
    
    def funding_efficiency(self, obj):
        return f"{obj.funding_efficiency:.1f}%"
    funding_efficiency.short_description = _('Funding Efficiency')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('campaign')
    
    def has_add_permission(self, request):
        # Analytics records are typically created automatically
        return False
    
    def has_change_permission(self, request, obj=None):
        # Analytics records should not be manually edited
        return False
