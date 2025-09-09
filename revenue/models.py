from django.db import models
from django.contrib.auth import get_user_model
from campaigns.models import Campaign
from blockchain.models import BlockchainNetwork, SmartContract

User = get_user_model()


class RevenueSource(models.Model):
    """Revenue source configuration"""
    
    REVENUE_TYPES = [
        ('box_office', 'Box Office'),
        ('ott_platform', 'OTT Platform'),
        ('streaming', 'Streaming'),
        ('dvd_sales', 'DVD Sales'),
        ('merchandise', 'Merchandise'),
        ('licensing', 'Licensing'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    revenue_type = models.CharField(max_length=20, choices=REVENUE_TYPES)
    description = models.TextField(blank=True)
    token_address = models.CharField(max_length=42, help_text="USDT or other stablecoin address")
    platform_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    creator_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=30.00)
    investor_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=65.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Revenue Source"
        verbose_name_plural = "Revenue Sources"
    
    def __str__(self):
        return f"{self.name} ({self.get_revenue_type_display()})"


class RevenueEntry(models.Model):
    """Individual revenue entries for campaigns"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    ]
    
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='revenue_entries')
    source = models.ForeignKey(RevenueSource, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=6)
    currency = models.CharField(max_length=10, default='USDT')
    description = models.TextField()
    revenue_date = models.DateField()
    verification_document = models.FileField(upload_to='revenue_documents/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_revenues')
    verified_at = models.DateTimeField(null=True, blank=True)
    blockchain_tx_hash = models.CharField(max_length=66, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Revenue Entry"
        verbose_name_plural = "Revenue Entries"
        ordering = ['-revenue_date']
    
    def __str__(self):
        return f"{self.campaign.title} - {self.amount} {self.currency} ({self.get_status_display()})"


class RoyaltyDistribution(models.Model):
    """Royalty distribution records"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='royalty_distributions')
    revenue_entry = models.ForeignKey(RevenueEntry, on_delete=models.CASCADE)
    distribution_date = models.DateTimeField()
    creator_amount = models.DecimalField(max_digits=20, decimal_places=6)
    platform_amount = models.DecimalField(max_digits=20, decimal_places=6)
    total_investor_amount = models.DecimalField(max_digits=20, decimal_places=6)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    blockchain_tx_hash = models.CharField(max_length=66, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Royalty Distribution"
        verbose_name_plural = "Royalty Distributions"
        ordering = ['-distribution_date']
    
    def __str__(self):
        return f"Distribution for {self.campaign.title} - {self.distribution_date}"


class InvestorRoyalty(models.Model):
    """Individual investor royalty claims"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('claimable', 'Claimable'),
        ('claimed', 'Claimed'),
        ('expired', 'Expired'),
    ]
    
    distribution = models.ForeignKey(RoyaltyDistribution, on_delete=models.CASCADE, related_name='investor_royalties')
    investor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='royalty_claims')
    nft_id = models.PositiveIntegerField()
    contribution_amount = models.DecimalField(max_digits=20, decimal_places=6)
    share_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    royalty_amount = models.DecimalField(max_digits=20, decimal_places=6)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    claimed_at = models.DateTimeField(null=True, blank=True)
    blockchain_tx_hash = models.CharField(max_length=66, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Investor Royalty"
        verbose_name_plural = "Investor Royalties"
        unique_together = ['distribution', 'investor', 'nft_id']
    
    def __str__(self):
        return f"{self.investor.username} - {self.royalty_amount} USDT"


class RevenueAnalytics(models.Model):
    """Revenue analytics and reporting data"""
    
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='revenue_analytics')
    total_revenue = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    total_creator_royalties = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    total_platform_fees = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    total_investor_royalties = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    total_distributions = models.PositiveIntegerField(default=0)
    last_distribution_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Revenue Analytics"
        verbose_name_plural = "Revenue Analytics"
    
    def __str__(self):
        return f"Analytics for {self.campaign.title}"


class OTTPlatformIntegration(models.Model):
    """OTT platform integration configuration"""
    
    PLATFORM_CHOICES = [
        ('netflix', 'Netflix'),
        ('amazon_prime', 'Amazon Prime'),
        ('disney_plus', 'Disney+'),
        ('hulu', 'Hulu'),
        ('hbo_max', 'HBO Max'),
        ('paramount_plus', 'Paramount+'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    platform_type = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    api_endpoint = models.URLField(blank=True, null=True)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    webhook_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "OTT Platform Integration"
        verbose_name_plural = "OTT Platform Integrations"
    
    def __str__(self):
        return f"{self.name} ({self.get_platform_type_display()})"


class RevenueWebhook(models.Model):
    """Webhook logs for revenue updates"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    ]
    
    platform = models.ForeignKey(OTTPlatformIntegration, on_delete=models.CASCADE, related_name='webhooks')
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='revenue_webhooks')
    payload = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    response_code = models.PositiveIntegerField(null=True, blank=True)
    response_message = models.TextField(blank=True, null=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Revenue Webhook"
        verbose_name_plural = "Revenue Webhooks"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Webhook for {self.campaign.title} - {self.get_status_display()}"
