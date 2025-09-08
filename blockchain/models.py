from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from users.models import User
from campaigns.models import Campaign


class BlockchainNetwork(models.Model):
    """
    Supported blockchain networks
    """
    NETWORK_CHOICES = [
        ('ethereum', _('Ethereum')),
        ('polygon', _('Polygon')),
        ('polygon_mumbai', _('Polygon Mumbai')),
        ('bsc', _('Binance Smart Chain')),
        ('bsc_testnet', _('BSC Testnet')),
    ]
    
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text=_('Network name')
    )
    
    network_type = models.CharField(
        max_length=20,
        choices=NETWORK_CHOICES,
        help_text=_('Type of blockchain network')
    )
    
    chain_id = models.PositiveIntegerField(
        unique=True,
        help_text=_('Blockchain chain ID')
    )
    
    rpc_url = models.URLField(
        help_text=_('RPC endpoint URL')
    )
    
    explorer_url = models.URLField(
        blank=True,
        help_text=_('Block explorer URL')
    )
    
    is_testnet = models.BooleanField(
        default=False,
        help_text=_('Whether this is a testnet')
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether this network is active')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Blockchain Network')
        verbose_name_plural = _('Blockchain Networks')
        db_table = 'blockchain_networks'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_network_type_display()})"


class SmartContract(models.Model):
    """
    Deployed smart contracts
    """
    CONTRACT_TYPES = [
        ('campaign_funding', _('Campaign Funding')),
        ('nft', _('NFT Contract')),
        ('royalty', _('Royalty Distribution')),
        ('token', _('Token Contract')),
    ]
    
    name = models.CharField(
        max_length=100,
        help_text=_('Contract name')
    )
    
    contract_type = models.CharField(
        max_length=20,
        choices=CONTRACT_TYPES,
        help_text=_('Type of smart contract')
    )
    
    address = models.CharField(
        max_length=42,
        unique=True,
        help_text=_('Contract address on blockchain')
    )
    
    network = models.ForeignKey(
        BlockchainNetwork,
        on_delete=models.CASCADE,
        related_name='contracts',
        help_text=_('Blockchain network')
    )
    
    abi = models.JSONField(
        help_text=_('Contract ABI (Application Binary Interface)')
    )
    
    bytecode = models.TextField(
        blank=True,
        help_text=_('Contract bytecode')
    )
    
    is_verified = models.BooleanField(
        default=False,
        help_text=_('Whether contract is verified on block explorer')
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether contract is active')
    )
    
    deployment_tx_hash = models.CharField(
        max_length=66,
        blank=True,
        help_text=_('Deployment transaction hash')
    )
    
    deployment_block = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_('Block number when deployed')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Smart Contract')
        verbose_name_plural = _('Smart Contracts')
        db_table = 'smart_contracts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.address[:10]}...{self.address[-8:]})"