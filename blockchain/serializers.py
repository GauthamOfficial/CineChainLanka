from rest_framework import serializers
from .models import (
    BlockchainNetwork, SmartContract
)
from .models_extended import (
    Wallet, BlockchainTransaction
)


class BlockchainNetworkSerializer(serializers.ModelSerializer):
    """Serializer for BlockchainNetwork"""
    
    class Meta:
        model = BlockchainNetwork
        fields = [
            'id', 'name', 'network_type', 'chain_id', 
            'rpc_url', 'explorer_url', 'is_testnet', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SmartContractSerializer(serializers.ModelSerializer):
    """Serializer for SmartContract"""
    network = BlockchainNetworkSerializer(read_only=True)
    network_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = SmartContract
        fields = [
            'id', 'name', 'contract_type', 'address', 'network', 'network_id',
            'abi', 'bytecode', 'is_verified', 'is_active', 'deployment_tx_hash',
            'deployment_block', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WalletSerializer(serializers.ModelSerializer):
    """Serializer for Wallet"""
    network = BlockchainNetworkSerializer(read_only=True)
    network_id = serializers.IntegerField(write_only=True)
    balance = serializers.SerializerMethodField()
    
    class Meta:
        model = Wallet
        fields = [
            'id', 'address', 'wallet_type', 'network', 'network_id',
            'is_primary', 'is_verified', 'last_used', 'balance',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'balance']
    
    def get_balance(self, obj):
        """Get wallet balance"""
        try:
            from .services import Web3Service
            web3_service = Web3Service(obj.network)
            balance = web3_service.get_balance(obj.address)
            return str(balance)
        except Exception:
            return "0.0"


class BlockchainTransactionSerializer(serializers.ModelSerializer):
    """Serializer for BlockchainTransaction"""
    contract = SmartContractSerializer(read_only=True)
    contract_id = serializers.IntegerField(write_only=True, required=False)
    user = serializers.StringRelatedField(read_only=True)
    campaign = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = BlockchainTransaction
        fields = [
            'id', 'tx_hash', 'block_number', 'block_hash', 'from_address',
            'to_address', 'value', 'gas_used', 'gas_price', 'contract',
            'contract_id', 'function_name', 'function_args', 'status',
            'transaction_type', 'user', 'campaign', 'error_message',
            'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'block_number', 'block_hash', 'gas_used', 'created_at', 'updated_at'
        ]


# NFT and IPFSFile serializers will be added when those models are implemented
# class NFTSerializer(serializers.ModelSerializer):
#     """Serializer for NFT"""
#     contract = SmartContractSerializer(read_only=True)
#     contract_id = serializers.IntegerField(write_only=True)
#     owner = serializers.StringRelatedField(read_only=True)
#     creator = serializers.StringRelatedField(read_only=True)
#     campaign = serializers.StringRelatedField(read_only=True)
#     opensea_url = serializers.ReadOnlyField()
#     
#     class Meta:
#         model = NFT
#         fields = [
#             'id', 'token_id', 'contract', 'contract_id', 'owner', 'creator',
#             'name', 'description', 'image_url', 'metadata_uri', 'campaign',
#             'contribution_amount', 'royalty_percentage', 'status',
#             'is_transferable', 'mint_tx_hash', 'minted_at', 'opensea_url',
#             'created_at', 'updated_at'
#         ]
#         read_only_fields = [
#             'id', 'minted_at', 'created_at', 'updated_at', 'opensea_url'
#         ]


# class IPFSFileSerializer(serializers.ModelSerializer):
#     """Serializer for IPFSFile"""
#     uploaded_by = serializers.StringRelatedField(read_only=True)
#     campaign = serializers.StringRelatedField(read_only=True)
#     nft = serializers.StringRelatedField(read_only=True)
#     
#     class Meta:
#         model = IPFSFile
#         fields = [
#             'id', 'ipfs_hash', 'file_name', 'file_type', 'file_size',
#             'mime_type', 'ipfs_url', 'gateway_urls', 'uploaded_by',
#             'campaign', 'nft', 'is_pinned', 'created_at', 'updated_at'
#         ]
#         read_only_fields = ['id', 'created_at', 'updated_at']


class WalletConnectionSerializer(serializers.Serializer):
    """Serializer for wallet connection"""
    address = serializers.CharField(max_length=42)
    signature = serializers.CharField(max_length=132)
    message = serializers.CharField()
    wallet_type = serializers.ChoiceField(choices=Wallet.WALLET_TYPES)
    network_id = serializers.IntegerField()


class TransactionRequestSerializer(serializers.Serializer):
    """Serializer for transaction requests"""
    to_address = serializers.CharField(max_length=42)
    value = serializers.DecimalField(max_digits=36, decimal_places=18, required=False, default=0)
    gas_limit = serializers.IntegerField(required=False)
    gas_price = serializers.DecimalField(max_digits=36, decimal_places=18, required=False)
    data = serializers.CharField(required=False, allow_blank=True)


class ContractCallSerializer(serializers.Serializer):
    """Serializer for contract function calls"""
    contract_id = serializers.IntegerField()
    function_name = serializers.CharField(max_length=100)
    args = serializers.JSONField(default=dict)
    value = serializers.DecimalField(max_digits=36, decimal_places=18, required=False, default=0)
    gas_limit = serializers.IntegerField(required=False)
    gas_price = serializers.DecimalField(max_digits=36, decimal_places=18, required=False)


# NFTCreationSerializer will be added when NFT model is implemented
# class NFTCreationSerializer(serializers.Serializer):
#     """Serializer for NFT creation"""
#     campaign_id = serializers.IntegerField()
#     name = serializers.CharField(max_length=200)
#     description = serializers.CharField(required=False, allow_blank=True)
#     image_file = serializers.FileField(required=False)
#     image_url = serializers.URLField(required=False)
#     contribution_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
#     royalty_percentage = serializers.DecimalField(
#         max_digits=5, 
#         decimal_places=2, 
#         required=False, 
#         default=5.00
#     )
#     attributes = serializers.JSONField(default=list, required=False)


# IPFSUploadSerializer will be added when IPFSFile model is implemented
# class IPFSUploadSerializer(serializers.Serializer):
#     """Serializer for IPFS file upload"""
#     file = serializers.FileField()
#     file_type = serializers.ChoiceField(choices=IPFSFile.FILE_TYPES, default='other')
#     campaign_id = serializers.IntegerField(required=False)
#     nft_id = serializers.IntegerField(required=False)
#     pin_file = serializers.BooleanField(default=True)
