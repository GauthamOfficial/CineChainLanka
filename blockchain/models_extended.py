from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from users.models import User
from campaigns.models import Campaign


class Wallet(models.Model):
    """
    User wallet addresses
    """
    WALLET_TYPES = [
        ('metamask', _('MetaMask')),
        ('trustwallet', _('Trust Wallet')),
        ('coinbase', _('Coinbase Wallet')),
        ('walletconnect', _('WalletConnect')),
        ('other', _('Other')),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wallets',
        help_text=_('Wallet owner')
    )
    
    address = models.CharField(
        max_length=42,
        help_text=_('Wallet address')
    )
    
    wallet_type = models.CharField(
        max_length=20,
        choices=WALLET_TYPES,
        help_text=_('Type of wallet')
    )
    
    network = models.ForeignKey(
        'BlockchainNetwork',
        on_delete=models.CASCADE,
        related_name='wallets',
        help_text=_('Primary network for this wallet')
    )
    
    is_primary = models.BooleanField(
        default=False,
        help_text=_('Whether this is the user\'s primary wallet')
    )
    
    is_verified = models.BooleanField(
        default=False,
        help_text=_('Whether wallet is verified')
    )
    
    last_used = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('Last time wallet was used')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Wallet')
        verbose_name_plural = _('Wallets')
        db_table = 'wallets'
        unique_together = ['user', 'address', 'network']
        ordering = ['-is_primary', '-last_used']
    
    def __str__(self):
        return f"{self.user.username} - {self.address[:10]}...{self.address[-8:]}"


class BlockchainTransaction(models.Model):
    """
    Blockchain transactions
    """
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
    ]
    
    TRANSACTION_TYPES = [
        ('contribution', _('Campaign Contribution')),
        ('nft_mint', _('NFT Minting')),
        ('nft_transfer', _('NFT Transfer')),
        ('refund', _('Refund')),
        ('withdrawal', _('Withdrawal')),
        ('royalty_payment', _('Royalty Payment')),
    ]
    
    # Transaction identification
    tx_hash = models.CharField(
        max_length=66,
        unique=True,
        help_text=_('Transaction hash')
    )
    
    block_number = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_('Block number')
    )
    
    block_hash = models.CharField(
        max_length=66,
        blank=True,
        help_text=_('Block hash')
    )
    
    # Transaction details
    from_address = models.CharField(
        max_length=42,
        help_text=_('Sender address')
    )
    
    to_address = models.CharField(
        max_length=42,
        help_text=_('Recipient address')
    )
    
    value = models.DecimalField(
        max_digits=36,
        decimal_places=18,
        default=0,
        help_text=_('Transaction value in ETH/BNB')
    )
    
    gas_used = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_('Gas used')
    )
    
    gas_price = models.DecimalField(
        max_digits=36,
        decimal_places=18,
        blank=True,
        null=True,
        help_text=_('Gas price in Gwei')
    )
    
    # Smart contract interaction
    contract = models.ForeignKey(
        'SmartContract',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='transactions',
        help_text=_('Smart contract involved')
    )
    
    function_name = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Function called on contract')
    )
    
    function_args = models.JSONField(
        default=dict,
        blank=True,
        help_text=_('Function arguments')
    )
    
    # Status and timing
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
        help_text=_('Type of transaction')
    )
    
    # Related models
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blockchain_transactions',
        help_text=_('User who initiated transaction')
    )
    
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='blockchain_transactions',
        help_text=_('Related campaign')
    )
    
    # Error information
    error_message = models.TextField(
        blank=True,
        help_text=_('Error message if transaction failed')
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
        verbose_name = _('Blockchain Transaction')
        verbose_name_plural = _('Blockchain Transactions')
        db_table = 'blockchain_transactions'
        indexes = [
            models.Index(fields=['tx_hash']),
            models.Index(fields=['status']),
            models.Index(fields=['user']),
            models.Index(fields=['campaign']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tx_hash[:10]}...{self.tx_hash[-8:]} - {self.get_status_display()}"


class IPFSFile(models.Model):
    """
    IPFS file storage records
    """
    FILE_TYPES = [
        ('image', _('Image')),
        ('video', _('Video')),
        ('audio', _('Audio')),
        ('document', _('Document')),
        ('metadata', _('Metadata')),
        ('other', _('Other')),
    ]
    
    ipfs_hash = models.CharField(
        max_length=46,
        unique=True,
        help_text=_('IPFS hash of the file')
    )
    
    file_name = models.CharField(
        max_length=255,
        help_text=_('Original file name')
    )
    
    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPES,
        default='other',
        help_text=_('Type of file')
    )
    
    file_size = models.PositiveIntegerField(
        help_text=_('File size in bytes')
    )
    
    mime_type = models.CharField(
        max_length=100,
        help_text=_('MIME type of the file')
    )
    
    ipfs_url = models.URLField(
        help_text=_('IPFS URL for the file')
    )
    
    gateway_urls = models.JSONField(
        default=list,
        help_text=_('Available gateway URLs')
    )
    
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ipfs_files',
        help_text=_('User who uploaded the file')
    )
    
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='ipfs_files',
        help_text=_('Related campaign')
    )
    
    nft_id = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_('Related NFT ID')
    )
    
    is_pinned = models.BooleanField(
        default=False,
        help_text=_('Whether file is pinned to IPFS')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('IPFS File')
        verbose_name_plural = _('IPFS Files')
        db_table = 'ipfs_files'
        indexes = [
            models.Index(fields=['ipfs_hash']),
            models.Index(fields=['file_type']),
            models.Index(fields=['uploaded_by']),
            models.Index(fields=['campaign']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.file_name} ({self.ipfs_hash[:10]}...)"