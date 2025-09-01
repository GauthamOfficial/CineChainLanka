from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from users.models import User
from campaigns.models import Campaign, CampaignReward
from payments.models import Transaction


class FundingRound(models.Model):
    """
    Funding rounds for campaigns (initial, follow-up, etc.)
    """
    ROUND_TYPE_CHOICES = [
        ('initial', _('Initial Funding')),
        ('follow_up', _('Follow-up Funding')),
        ('emergency', _('Emergency Funding')),
        ('completion', _('Completion Funding')),
    ]
    
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='funding_rounds'
    )
    
    round_type = models.CharField(
        max_length=20,
        choices=ROUND_TYPE_CHOICES,
        default='initial',
        help_text=_('Type of funding round')
    )
    
    title = models.CharField(
        max_length=200,
        help_text=_('Title of the funding round')
    )
    
    description = models.TextField(
        help_text=_('Description of the funding round')
    )
    
    funding_goal = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text=_('Funding goal for this round in LKR')
    )
    
    current_funding = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text=_('Current amount raised in this round')
    )
    
    start_date = models.DateTimeField(
        help_text=_('Start date of the funding round')
    )
    
    end_date = models.DateTimeField(
        help_text=_('End date of the funding round')
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether this funding round is active')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Funding Round')
        verbose_name_plural = _('Funding Rounds')
        db_table = 'funding_rounds'
        ordering = ['start_date']
    
    def __str__(self):
        return f"{self.title} - {self.campaign.title}"
    
    @property
    def funding_percentage(self):
        if self.funding_goal > 0:
            return (self.current_funding / self.funding_goal) * 100
        return 0
    
    @property
    def is_funded(self):
        return self.current_funding >= self.funding_goal


class FundingMilestone(models.Model):
    """
    Milestones for campaign funding with specific goals
    """
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='funding_milestones'
    )
    
    title = models.CharField(
        max_length=200,
        help_text=_('Milestone title')
    )
    
    description = models.TextField(
        help_text=_('Milestone description')
    )
    
    funding_target = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text=_('Funding target for this milestone in LKR')
    )
    
    is_achieved = models.BooleanField(
        default=False,
        help_text=_('Whether this milestone has been achieved')
    )
    
    achieved_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('When the milestone was achieved')
    )
    
    order = models.PositiveIntegerField(
        default=0,
        help_text=_('Order of the milestone')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Funding Milestone')
        verbose_name_plural = _('Funding Milestones')
        db_table = 'funding_milestones'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.title} - {self.campaign.title}"


class FundingAllocation(models.Model):
    """
    How campaign funds are allocated and used
    """
    ALLOCATION_TYPE_CHOICES = [
        ('production', _('Production Costs')),
        ('equipment', _('Equipment & Technology')),
        ('personnel', _('Personnel & Cast')),
        ('marketing', _('Marketing & Promotion')),
        ('post_production', _('Post-Production')),
        ('distribution', _('Distribution & Release')),
        ('contingency', _('Contingency Fund')),
        ('other', _('Other Expenses')),
    ]
    
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='funding_allocations'
    )
    
    allocation_type = models.CharField(
        max_length=30,
        choices=ALLOCATION_TYPE_CHOICES,
        help_text=_('Type of fund allocation')
    )
    
    description = models.TextField(
        help_text=_('Description of how funds will be used')
    )
    
    budgeted_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text=_('Budgeted amount for this allocation in LKR')
    )
    
    actual_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text=_('Actual amount spent in this allocation')
    )
    
    percentage_of_total = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text=_('Percentage of total funding for this allocation')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Funding Allocation')
        verbose_name_plural = _('Funding Allocations')
        db_table = 'funding_allocations'
        ordering = ['percentage_of_total']
    
    def __str__(self):
        return f"{self.get_allocation_type_display()} - {self.campaign.title}"
    
    @property
    def remaining_budget(self):
        return self.budgeted_amount - self.actual_amount
    
    @property
    def spending_percentage(self):
        if self.budgeted_amount > 0:
            return (self.actual_amount / self.budgeted_amount) * 100
        return 0


class FundingProgress(models.Model):
    """
    Track funding progress over time
    """
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='funding_progress'
    )
    
    date = models.DateField(
        help_text=_('Date of the progress record')
    )
    
    total_funding = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text=_('Total funding at this date')
    )
    
    daily_funding = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text=_('Funding received on this date')
    )
    
    backer_count = models.PositiveIntegerField(
        default=0,
        help_text=_('Total number of backers at this date')
    )
    
    new_backers = models.PositiveIntegerField(
        default=0,
        help_text=_('New backers on this date')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Funding Progress')
        verbose_name_plural = _('Funding Progress')
        db_table = 'funding_progress'
        ordering = ['date']
        unique_together = ['campaign', 'date']
    
    def __str__(self):
        return f"{self.campaign.title} - {self.date} - LKR {self.total_funding}"


class FundingAnalytics(models.Model):
    """
    Analytics and insights for campaign funding
    """
    campaign = models.OneToOneField(
        Campaign,
        on_delete=models.CASCADE,
        related_name='funding_analytics'
    )
    
    # Funding metrics
    total_contributions = models.PositiveIntegerField(
        default=0,
        help_text=_('Total number of contributions received')
    )
    
    average_contribution = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text=_('Average contribution amount')
    )
    
    median_contribution = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text=_('Median contribution amount')
    )
    
    largest_contribution = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text=_('Largest single contribution received')
    )
    
    # Backer metrics
    unique_backers = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of unique backers')
    )
    
    repeat_backers = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of repeat backers')
    )
    
    new_backers = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of new backers')
    )
    
    # Conversion metrics
    view_to_backer_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text=_('Percentage of viewers who became backers')
    )
    
    # Geographic distribution
    top_locations = models.JSONField(
        default=list,
        blank=True,
        help_text=_('Top contributing locations')
    )
    
    # Payment method distribution
    payment_method_distribution = models.JSONField(
        default=dict,
        blank=True,
        help_text=_('Distribution of contributions by payment method')
    )
    
    # Time-based metrics
    peak_funding_day = models.DateField(
        blank=True,
        null=True,
        help_text=_('Day with highest funding')
    )
    
    peak_funding_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text=_('Highest funding amount in a single day')
    )
    
    # Projections
    projected_completion_date = models.DateField(
        blank=True,
        null=True,
        help_text=_('Projected date to reach funding goal')
    )
    
    funding_velocity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text=_('Average daily funding rate')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Funding Analytics')
        verbose_name_plural = _('Funding Analytics')
        db_table = 'funding_analytics'
    
    def __str__(self):
        return f"Analytics for {self.campaign.title}"
    
    @property
    def repeat_backer_rate(self):
        if self.unique_backers > 0:
            return (self.repeat_backers / self.unique_backers) * 100
        return 0
    
    @property
    def funding_efficiency(self):
        if self.campaign.view_count > 0:
            return (self.unique_backers / self.campaign.view_count) * 100
        return 0
