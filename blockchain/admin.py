from django.contrib import admin
from django.utils.html import format_html
from .models import (
    BlockchainNetwork, SmartContract
)
from .models_extended import (
    Wallet, BlockchainTransaction
)


@admin.register(BlockchainNetwork)
class BlockchainNetworkAdmin(admin.ModelAdmin):
    list_display = ['name', 'network_type', 'chain_id', 'is_testnet', 'is_active', 'created_at']
    list_filter = ['network_type', 'is_testnet', 'is_active']
    search_fields = ['name', 'network_type']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SmartContract)
class SmartContractAdmin(admin.ModelAdmin):
    list_display = ['name', 'contract_type', 'address_short', 'network', 'is_verified', 'is_active', 'created_at']
    list_filter = ['contract_type', 'network', 'is_verified', 'is_active']
    search_fields = ['name', 'address', 'contract_type']
    readonly_fields = ['created_at', 'updated_at', 'address_short']
    
    def address_short(self, obj):
        if obj.address:
            return f"{obj.address[:10]}...{obj.address[-8:]}"
        return "-"
    address_short.short_description = "Address"


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'address_short', 'wallet_type', 'network', 'is_primary', 'is_verified', 'last_used']
    list_filter = ['wallet_type', 'network', 'is_primary', 'is_verified']
    search_fields = ['user__username', 'user__email', 'address']
    readonly_fields = ['created_at', 'updated_at', 'address_short']
    
    def address_short(self, obj):
        if obj.address:
            return f"{obj.address[:10]}...{obj.address[-8:]}"
        return "-"
    address_short.short_description = "Address"


@admin.register(BlockchainTransaction)
class BlockchainTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'tx_hash_short', 'from_address_short', 'to_address_short', 
        'transaction_type', 'status', 'value', 'created_at'
    ]
    list_filter = ['status', 'transaction_type', 'contract', 'created_at']
    search_fields = ['tx_hash', 'from_address', 'to_address', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'tx_hash_short', 'from_address_short', 'to_address_short']
    
    def tx_hash_short(self, obj):
        if obj.tx_hash:
            return f"{obj.tx_hash[:10]}...{obj.tx_hash[-8:]}"
        return "-"
    tx_hash_short.short_description = "Transaction Hash"
    
    def from_address_short(self, obj):
        if obj.from_address:
            return f"{obj.from_address[:10]}...{obj.from_address[-8:]}"
        return "-"
    from_address_short.short_description = "From"
    
    def to_address_short(self, obj):
        if obj.to_address:
            return f"{obj.to_address[:10]}...{obj.to_address[-8:]}"
        return "-"
    to_address_short.short_description = "To"


# NFT and IPFSFile admin classes will be added when those models are implemented