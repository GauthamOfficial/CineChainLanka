from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from users.models import User


class CampaignCategory(models.Model):
    """
    Categories for campaigns (Film, Documentary, Web Series, etc.)
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_('Category name')
    )
    
    description = models.TextField(
        blank=True,
        help_text=_('Category description')
    )
    
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Icon class or identifier')
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether this category is active')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Campaign Category')
        verbose_name_plural = _('Campaign Categories')
        db_table = 'campaign_categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Campaign(models.Model):
    """
    Main campaign model for film and content funding
    """
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('pending_review', _('Pending Review')),
        ('approved', _('Approved')),
        ('active', _('Active')),
        ('funded', _('Funded')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
        ('completed', _('Completed')),
    ]
    
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='campaigns',
        help_text=_('Campaign creator')
    )
    
    # Basic campaign information
    title = models.CharField(
        max_length=200,
        help_text=_('Campaign title')
    )
    
    subtitle = models.CharField(
        max_length=300,
        blank=True,
        help_text=_('Campaign subtitle or tagline')
    )
    
    description = models.TextField(
        help_text=_('Detailed campaign description')
    )
    
    short_description = models.TextField(
        max_length=500,
        help_text=_('Brief campaign summary')
    )
    
    category = models.ForeignKey(
        CampaignCategory,
        on_delete=models.PROTECT,
        related_name='campaigns',
        help_text=_('Campaign category')
    )
    
    # Media content
    cover_image = models.ImageField(
        upload_to='campaign_covers/',
        blank=True,
        null=True,
        help_text=_('Campaign cover image')
    )
    
    video_url = models.URLField(
        blank=True,
        help_text=_('Campaign video URL (YouTube, Vimeo, etc.)')
    )
    
    gallery_images = models.JSONField(
        default=list,
        blank=True,
        help_text=_('List of gallery image URLs')
    )
    
    # Funding details
    funding_goal = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text=_('Campaign funding goal in LKR')
    )
    
    current_funding = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text=_('Current amount raised')
    )
    
    # Campaign timeline
    start_date = models.DateTimeField(
        help_text=_('Campaign start date and time')
    )
    
    end_date = models.DateTimeField(
        help_text=_('Campaign end date and time')
    )
    
    estimated_completion_date = models.DateField(
        help_text=_('Estimated project completion date')
    )
    
    # Campaign status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text=_('Current campaign status')
    )
    
    # Review and approval
    submitted_for_review = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('When campaign was submitted for review')
    )
    
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='reviewed_campaigns',
        help_text=_('Admin who reviewed the campaign')
    )
    
    reviewed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('When campaign was reviewed')
    )
    
    review_notes = models.TextField(
        blank=True,
        help_text=_('Admin review notes')
    )
    
    # Campaign metrics
    view_count = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of campaign views')
    )
    
    backer_count = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of unique backers')
    )
    
    # Additional information
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text=_('List of campaign tags')
    )
    
    risks_and_challenges = models.TextField(
        blank=True,
        help_text=_('Potential risks and challenges')
    )
    
    team_members = models.JSONField(
        default=list,
        blank=True,
        help_text=_('List of team member information')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Campaign')
        verbose_name_plural = _('Campaigns')
        db_table = 'campaigns'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['category']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
            models.Index(fields=['funding_goal']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} by {self.creator.username}"
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def is_funded(self):
        return self.current_funding >= self.funding_goal
    
    @property
    def funding_percentage(self):
        if self.funding_goal > 0:
            return (self.current_funding / self.funding_goal) * 100
        return 0
    
    @property
    def days_remaining(self):
        from django.utils import timezone
        if self.end_date > timezone.now():
            return (self.end_date - timezone.now()).days
        return 0
    
    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.end_date


class CampaignReward(models.Model):
    """
    Rewards offered to campaign backers
    """
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='rewards'
    )
    
    title = models.CharField(
        max_length=200,
        help_text=_('Reward title')
    )
    
    description = models.TextField(
        help_text=_('Reward description')
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_('Minimum contribution amount for this reward')
    )
    
    max_backers = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_('Maximum number of backers for this reward (null for unlimited)')
    )
    
    current_backers = models.PositiveIntegerField(
        default=0,
        help_text=_('Current number of backers for this reward')
    )
    
    estimated_delivery = models.DateField(
        help_text=_('Estimated delivery date for this reward')
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether this reward is currently available')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Campaign Reward')
        verbose_name_plural = _('Campaign Rewards')
        db_table = 'campaign_rewards'
        ordering = ['amount']
    
    def __str__(self):
        return f"{self.title} - LKR {self.amount}"
    
    @property
    def is_available(self):
        if not self.is_active:
            return False
        if self.max_backers is None:
            return True
        return self.current_backers < self.max_backers
    
    @property
    def remaining_slots(self):
        if self.max_backers is None:
            return None
        return max(0, self.max_backers - self.current_backers)


class CampaignUpdate(models.Model):
    """
    Updates posted by campaign creators
    """
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='updates'
    )
    
    title = models.CharField(
        max_length=200,
        help_text=_('Update title')
    )
    
    content = models.TextField(
        help_text=_('Update content')
    )
    
    is_public = models.BooleanField(
        default=True,
        help_text=_('Whether this update is visible to all backers')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Campaign Update')
        verbose_name_plural = _('Campaign Updates')
        db_table = 'campaign_updates'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.campaign.title}"


class CampaignComment(models.Model):
    """
    Comments on campaigns
    """
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='campaign_comments'
    )
    
    content = models.TextField(
        help_text=_('Comment content')
    )
    
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='replies',
        help_text=_('Parent comment for replies')
    )
    
    is_approved = models.BooleanField(
        default=True,
        help_text=_('Whether this comment is approved and visible')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Campaign Comment')
        verbose_name_plural = _('Campaign Comments')
        db_table = 'campaign_comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.campaign.title}"
    
    @property
    def is_reply(self):
        return self.parent_comment is not None
