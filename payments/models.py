from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from users.models import User
from campaigns.models import Campaign, CampaignReward


class PaymentMethod(models.Model):
    """
    Available payment methods for the platform
    """
    PAYMENT_TYPE_CHOICES = [
        ('lanka_qr', _('LankaQR')),
        ('ez_cash', _('eZ Cash')),
        ('frimi', _('FriMi')),
        ('bank_transfer', _('Bank Transfer')),
        ('credit_card', _('Credit Card')),
        ('debit_card', _('Debit Card')),
        ('paypal', _('PayPal')),
        ('crypto', _('Cryptocurrency')),
    ]
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_('Payment method name')
    )
    
    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPE_CHOICES,
        help_text=_('Type of payment method')
    )
    
    description = models.TextField(
        blank=True,
        help_text=_('Payment method description')
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether this payment method is available')
    )
    
    processing_fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text=_('Processing fee as percentage of transaction amount')
    )
    
    processing_fee_fixed = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text=_('Fixed processing fee amount')
    )
    
    minimum_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text=_('Minimum transaction amount')
    )
    
    maximum_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=999999.99,
        help_text=_('Maximum transaction amount')
    )
    
    # Configuration for specific payment methods
    config_data = models.JSONField(
        default=dict,
        blank=True,
        help_text=_('Configuration data for payment method (API keys, endpoints, etc.)')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Payment Method')
        verbose_name_plural = _('Payment Methods')
        db_table = 'payment_methods'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_payment_type_display()})"
    
    def calculate_fee(self, amount):
        """Calculate processing fee for a given amount"""
        percentage_fee = (amount * self.processing_fee_percentage) / 100
        return percentage_fee + self.processing_fee_fixed


class Transaction(models.Model):
    """
    Main transaction model for all payments
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
    ]
    
    TRANSACTION_TYPE_CHOICES = [
        ('contribution', _('Campaign Contribution')),
        ('refund', _('Refund')),
        ('withdrawal', _('Withdrawal')),
        ('fee', _('Platform Fee')),
    ]
    
    # Transaction identification
    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        help_text=_('Unique transaction identifier')
    )
    
    reference_id = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('External reference ID from payment provider')
    )
    
    # Transaction details
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='transactions',
        blank=True,
        null=True
    )
    
    reward = models.ForeignKey(
        CampaignReward,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='transactions'
    )
    
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
        default='contribution'
    )
    
    # Amount details
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text=_('Transaction amount in LKR')
    )
    
    processing_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text=_('Processing fee amount')
    )
    
    net_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text=_('Net amount after processing fees')
    )
    
    # Payment method
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    
    # Status and timing
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    initiated_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When transaction was initiated')
    )
    
    processed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('When transaction was processed')
    )
    
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('When transaction was completed')
    )
    
    # Error and failure information
    error_message = models.TextField(
        blank=True,
        help_text=_('Error message if transaction failed')
    )
    
    failure_reason = models.CharField(
        max_length=200,
        blank=True,
        help_text=_('Reason for transaction failure')
    )
    
    # Additional data
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_('Additional transaction metadata')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')
        db_table = 'transactions'
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['status']),
            models.Index(fields=['user']),
            models.Index(fields=['campaign']),
            models.Index(fields=['initiated_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transaction_id} - {self.user.username} - LKR {self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.net_amount:
            self.net_amount = self.amount - self.processing_fee
        super().save(*args, **kwargs)
    
    @property
    def is_successful(self):
        return self.status == 'completed'
    
    @property
    def is_failed(self):
        return self.status == 'failed'
    
    @property
    def is_pending(self):
        return self.status in ['pending', 'processing']


class Contribution(models.Model):
    """
    Campaign contributions made by users
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contributions'
    )
    
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='contributions'
    )
    
    reward = models.ForeignKey(
        CampaignReward,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='contributions'
    )
    
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        related_name='contribution'
    )
    
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text=_('Contribution amount in LKR')
    )
    
    is_anonymous = models.BooleanField(
        default=False,
        help_text=_('Whether this contribution is anonymous')
    )
    
    message = models.TextField(
        blank=True,
        help_text=_('Message from contributor to campaign creator')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Contribution')
        verbose_name_plural = _('Contributions')
        db_table = 'contributions'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['campaign']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} contributed LKR {self.amount} to {self.campaign.title}"


class Refund(models.Model):
    """
    Refunds for failed campaigns or cancelled contributions
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
    ]
    
    original_transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='refunds'
    )
    
    refund_transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        related_name='refund_for',
        blank=True,
        null=True
    )
    
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text=_('Refund amount in LKR')
    )
    
    reason = models.CharField(
        max_length=200,
        help_text=_('Reason for refund')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='processed_refunds',
        help_text=_('Admin who processed the refund')
    )
    
    processed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('When refund was processed')
    )
    
    notes = models.TextField(
        blank=True,
        help_text=_('Additional notes about the refund')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Refund')
        verbose_name_plural = _('Refunds')
        db_table = 'refunds'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['original_transaction']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Refund of LKR {self.amount} for {self.original_transaction.transaction_id}"


class PaymentProvider(models.Model):
    """
    External payment providers and their configurations
    """
    PROVIDER_TYPE_CHOICES = [
        ('lanka_qr', _('LankaQR')),
        ('ez_cash', _('eZ Cash')),
        ('frimi', _('FriMi')),
        ('stripe', _('Stripe')),
        ('paypal', _('PayPal')),
        ('bank', _('Bank Transfer')),
    ]
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_('Payment provider name')
    )
    
    provider_type = models.CharField(
        max_length=20,
        choices=PROVIDER_TYPE_CHOICES,
        help_text=_('Type of payment provider')
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether this provider is active')
    )
    
    # API configuration
    api_key = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('API key for the provider')
    )
    
    api_secret = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('API secret for the provider')
    )
    
    webhook_secret = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Webhook secret for verification')
    )
    
    # Endpoints
    api_endpoint = models.URLField(
        blank=True,
        help_text=_('API endpoint URL')
    )
    
    webhook_endpoint = models.URLField(
        blank=True,
        help_text=_('Webhook endpoint URL')
    )
    
    # Configuration
    config_data = models.JSONField(
        default=dict,
        blank=True,
        help_text=_('Additional configuration data')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Payment Provider')
        verbose_name_plural = _('Payment Providers')
        db_table = 'payment_providers'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_provider_type_display()})"
