from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import (
    CampaignCategory, Campaign, CampaignReward, 
    CampaignUpdate, CampaignComment
)


@admin.register(CampaignCategory)
class CampaignCategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for CampaignCategory model
    """
    list_display = [
        'name', 'description', 'icon', 'is_active', 'created_at'
    ]
    
    list_filter = ['is_active', 'created_at']
    
    search_fields = ['name', 'description']
    
    ordering = ['name']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'icon', 'is_active')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    """
    Admin configuration for Campaign model
    """
    list_display = [
        'title', 'creator', 'category', 'status', 'funding_goal',
        'current_funding', 'funding_percentage', 'days_remaining',
        'backer_count', 'created_at'
    ]
    
    list_filter = [
        'status', 'category', 'creator__user_type', 'start_date',
        'end_date', 'created_at'
    ]
    
    search_fields = [
        'title', 'subtitle', 'description', 'creator__username',
        'creator__email', 'tags'
    ]
    
    ordering = ['-created_at']
    
    list_per_page = 25
    
    # Fieldsets for editing
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'creator', 'title', 'subtitle', 'description', 'short_description'
            )
        }),
        (_('Category & Classification'), {
            'fields': ('category', 'tags')
        }),
        (_('Media Content'), {
            'fields': ('cover_image', 'video_url', 'gallery_images')
        }),
        (_('Funding Details'), {
            'fields': ('funding_goal', 'current_funding')
        }),
        (_('Campaign Timeline'), {
            'fields': (
                'start_date', 'end_date', 'estimated_completion_date'
            )
        }),
        (_('Campaign Status'), {
            'fields': ('status',)
        }),
        (_('Review & Approval'), {
            'fields': (
                'submitted_for_review', 'reviewed_by', 'reviewed_at',
                'review_notes'
            )
        }),
        (_('Campaign Metrics'), {
            'fields': ('view_count', 'backer_count')
        }),
        (_('Additional Information'), {
            'fields': ('risks_and_challenges', 'team_members')
        }),
    )
    
    readonly_fields = [
        'current_funding', 'view_count', 'backer_count', 'created_at',
        'updated_at'
    ]
    
    def funding_percentage(self, obj):
        return f"{obj.funding_percentage:.1f}%"
    funding_percentage.short_description = _('Funding %')
    
    def days_remaining(self, obj):
        days = obj.days_remaining
        if days > 0:
            return f"{days} days"
        elif days == 0:
            return "Today"
        else:
            return "Expired"
    days_remaining.short_description = _('Days Remaining')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'creator', 'category'
        )
    
    def get_list_display(self, request):
        list_display = list(super().get_list_display(request))
        if request.user.is_superuser:
            list_display.append('admin_actions')
        return list_display
    
    def admin_actions(self, obj):
        actions = []
        if obj.status == 'pending_review':
            actions.append(
                format_html(
                    '<a href="{}" class="button">Review</a>',
                    reverse('admin:campaigns_campaign_change', args=[obj.id])
                )
            )
        if obj.status == 'active':
            actions.append(
                format_html(
                    '<a href="{}" class="button">View Details</a>',
                    reverse('admin:campaigns_campaign_change', args=[obj.id])
                )
            )
        return format_html(' '.join(actions)) if actions else '-'
    admin_actions.short_description = _('Actions')


@admin.register(CampaignReward)
class CampaignRewardAdmin(admin.ModelAdmin):
    """
    Admin configuration for CampaignReward model
    """
    list_display = [
        'title', 'campaign', 'amount', 'max_backers', 'current_backers',
        'remaining_slots', 'is_active', 'created_at'
    ]
    
    list_filter = [
        'is_active', 'campaign__status', 'campaign__category',
        'estimated_delivery', 'created_at'
    ]
    
    search_fields = [
        'title', 'description', 'campaign__title', 'campaign__creator__username'
    ]
    
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Reward Information'), {
            'fields': (
                'campaign', 'title', 'description', 'amount'
            )
        }),
        (_('Availability'), {
            'fields': (
                'max_backers', 'current_backers', 'is_active'
            )
        }),
        (_('Delivery'), {
            'fields': ('estimated_delivery',)
        }),
    )
    
    readonly_fields = ['current_backers', 'created_at', 'updated_at']
    
    def remaining_slots(self, obj):
        slots = obj.remaining_slots
        if slots is None:
            return "Unlimited"
        return slots
    remaining_slots.short_description = _('Remaining Slots')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('campaign')


@admin.register(CampaignUpdate)
class CampaignUpdateAdmin(admin.ModelAdmin):
    """
    Admin configuration for CampaignUpdate model
    """
    list_display = [
        'title', 'campaign', 'is_public', 'created_at'
    ]
    
    list_filter = [
        'is_public', 'campaign__status', 'created_at'
    ]
    
    search_fields = [
        'title', 'content', 'campaign__title', 'campaign__creator__username'
    ]
    
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Update Information'), {
            'fields': ('campaign', 'title', 'content', 'is_public')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('campaign')


@admin.register(CampaignComment)
class CampaignCommentAdmin(admin.ModelAdmin):
    """
    Admin configuration for CampaignComment model
    """
    list_display = [
        'user', 'campaign', 'content_preview', 'is_reply', 'is_approved',
        'created_at'
    ]
    
    list_filter = [
        'is_approved', 'campaign__status', 'created_at'
    ]
    
    search_fields = [
        'content', 'user__username', 'campaign__title'
    ]
    
    ordering = ['-created_at']
    
    list_per_page = 50
    
    fieldsets = (
        (_('Comment Information'), {
            'fields': (
                'user', 'campaign', 'content', 'parent_comment'
            )
        }),
        (_('Moderation'), {
            'fields': ('is_approved',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def content_preview(self, obj):
        content = obj.content
        if len(content) > 100:
            return f"{content[:100]}..."
        return content
    content_preview.short_description = _('Content Preview')
    
    def is_reply(self, obj):
        return obj.is_reply
    is_reply.boolean = True
    is_reply.short_description = _('Is Reply')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'campaign', 'parent_comment'
        )
    
    actions = ['approve_comments', 'reject_comments']
    
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(
            request,
            f'{updated} comment(s) were successfully approved.'
        )
    approve_comments.short_description = _('Approve selected comments')
    
    def reject_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(
            request,
            f'{updated} comment(s) were successfully rejected.'
        )
    reject_comments.short_description = _('Reject selected comments')
