import json
import logging
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from eth_account import Account
from eth_account.messages import encode_defunct
from django.conf import settings
from django.utils import timezone
from .models import BlockchainNetwork, SmartContract
from .models_extended import BlockchainTransaction, Wallet

logger = logging.getLogger(__name__)


class Web3Service:
    """
    Service for Web3 blockchain interactions
    """
    
    def __init__(self, network: BlockchainNetwork):
        self.network = network
        self.w3 = Web3(Web3.HTTPProvider(network.rpc_url))
        
        # Add PoA middleware for networks that use it (like BSC)
        if network.network_type in ['bsc', 'bsc_testnet']:
            self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    
    def is_connected(self) -> bool:
        """Check if Web3 connection is active"""
        try:
            return self.w3.is_connected()
        except Exception as e:
            logger.error(f"Web3 connection error: {e}")
            return False
    
    def get_latest_block(self) -> int:
        """Get latest block number"""
        try:
            return self.w3.eth.block_number
        except Exception as e:
            logger.error(f"Error getting latest block: {e}")
            return 0
    
    def get_gas_price(self) -> int:
        """Get current gas price in wei"""
        try:
            return self.w3.eth.gas_price
        except Exception as e:
            logger.error(f"Error getting gas price: {e}")
            return 20000000000  # 20 gwei default
    
    def estimate_gas(self, transaction: Dict) -> int:
        """Estimate gas for a transaction"""
        try:
            return self.w3.eth.estimate_gas(transaction)
        except Exception as e:
            logger.error(f"Error estimating gas: {e}")
            return 21000  # Basic transfer gas limit
    
    def get_balance(self, address: str) -> Decimal:
        """Get ETH/BNB balance of an address"""
        try:
            balance_wei = self.w3.eth.get_balance(address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            return Decimal(str(balance_eth))
        except Exception as e:
            logger.error(f"Error getting balance for {address}: {e}")
            return Decimal('0')
    
    def get_token_balance(self, token_address: str, wallet_address: str, decimals: int = 18) -> Decimal:
        """Get ERC20 token balance"""
        try:
            # ERC20 balanceOf function ABI
            balance_abi = [{
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            }]
            
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(token_address),
                abi=balance_abi
            )
            
            balance = contract.functions.balanceOf(wallet_address).call()
            return Decimal(str(balance)) / (10 ** decimals)
        except Exception as e:
            logger.error(f"Error getting token balance: {e}")
            return Decimal('0')
    
    def send_transaction(self, transaction: Dict, private_key: str) -> str:
        """Send a signed transaction"""
        try:
            # Sign the transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
            
            # Send the transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return tx_hash.hex()
        except Exception as e:
            logger.error(f"Error sending transaction: {e}")
            raise
    
    def wait_for_transaction(self, tx_hash: str, timeout: int = 300) -> Dict:
        """Wait for transaction confirmation"""
        try:
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
            return dict(receipt)
        except Exception as e:
            logger.error(f"Error waiting for transaction {tx_hash}: {e}")
            raise
    
    def get_transaction_receipt(self, tx_hash: str) -> Optional[Dict]:
        """Get transaction receipt"""
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            return dict(receipt)
        except Exception as e:
            logger.error(f"Error getting transaction receipt {tx_hash}: {e}")
            return None
    
    def get_transaction(self, tx_hash: str) -> Optional[Dict]:
        """Get transaction details"""
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            return dict(tx)
        except Exception as e:
            logger.error(f"Error getting transaction {tx_hash}: {e}")
            return None


class ContractService:
    """
    Service for smart contract interactions
    """
    
    def __init__(self, contract: SmartContract, web3_service: Web3Service):
        self.contract = contract
        self.web3_service = web3_service
        self.w3 = web3_service.w3
        
        # Create contract instance
        self.contract_instance = self.w3.eth.contract(
            address=Web3.to_checksum_address(contract.address),
            abi=contract.abi
        )
    
    def call_function(self, function_name: str, *args, **kwargs) -> Any:
        """Call a contract function (read-only)"""
        try:
            function = getattr(self.contract_instance.functions, function_name)
            return function(*args, **kwargs).call()
        except Exception as e:
            logger.error(f"Error calling function {function_name}: {e}")
            raise
    
    def send_function(self, function_name: str, private_key: str, *args, **kwargs) -> str:
        """Send a contract function transaction"""
        try:
            function = getattr(self.contract_instance.functions, function_name)
            
            # Build transaction
            transaction = function(*args, **kwargs).build_transaction({
                'from': Account.from_key(private_key).address,
                'gas': self.web3_service.estimate_gas({
                    'to': self.contract.address,
                    'data': function(*args, **kwargs)._encode_transaction_data()
                }),
                'gasPrice': self.web3_service.get_gas_price(),
                'nonce': self.w3.eth.get_transaction_count(Account.from_key(private_key).address),
            })
            
            # Send transaction
            return self.web3_service.send_transaction(transaction, private_key)
        except Exception as e:
            logger.error(f"Error sending function {function_name}: {e}")
            raise


class CampaignFundingService:
    """
    Service for campaign funding contract interactions
    """
    
    def __init__(self, contract: SmartContract, web3_service: Web3Service):
        self.contract_service = ContractService(contract, web3_service)
        self.contract = contract
    
    def create_campaign(
        self, 
        creator_address: str, 
        private_key: str,
        title: str, 
        description: str, 
        funding_goal: int, 
        duration: int
    ) -> str:
        """Create a new campaign"""
        try:
            tx_hash = self.contract_service.send_function(
                'createCampaign',
                private_key,
                title,
                description,
                funding_goal,
                duration
            )
            
            # Create blockchain transaction record
            BlockchainTransaction.objects.create(
                tx_hash=tx_hash,
                from_address=creator_address,
                to_address=self.contract.address,
                contract=self.contract,
                function_name='createCampaign',
                function_args={
                    'title': title,
                    'description': description,
                    'funding_goal': funding_goal,
                    'duration': duration
                },
                transaction_type='contribution',
                user_id=1,  # This should be passed as parameter
                status='pending'
            )
            
            return tx_hash
        except Exception as e:
            logger.error(f"Error creating campaign: {e}")
            raise
    
    def contribute(
        self, 
        backer_address: str, 
        private_key: str,
        campaign_id: int, 
        amount: int
    ) -> str:
        """Contribute to a campaign"""
        try:
            tx_hash = self.contract_service.send_function(
                'contribute',
                private_key,
                campaign_id,
                amount
            )
            
            # Create blockchain transaction record
            BlockchainTransaction.objects.create(
                tx_hash=tx_hash,
                from_address=backer_address,
                to_address=self.contract.address,
                contract=self.contract,
                function_name='contribute',
                function_args={
                    'campaign_id': campaign_id,
                    'amount': amount
                },
                transaction_type='contribution',
                user_id=1,  # This should be passed as parameter
                status='pending'
            )
            
            return tx_hash
        except Exception as e:
            logger.error(f"Error contributing to campaign: {e}")
            raise
    
    def get_campaign(self, campaign_id: int) -> Dict:
        """Get campaign details"""
        try:
            return self.contract_service.call_function('getCampaign', campaign_id)
        except Exception as e:
            logger.error(f"Error getting campaign {campaign_id}: {e}")
            raise
    
    def get_contribution(self, campaign_id: int, backer_address: str) -> int:
        """Get backer's contribution amount"""
        try:
            return self.contract_service.call_function('getContribution', campaign_id, backer_address)
        except Exception as e:
            logger.error(f"Error getting contribution: {e}")
            raise


class NFTService:
    """
    Service for NFT contract interactions
    """
    
    def __init__(self, contract: SmartContract, web3_service: Web3Service):
        self.contract_service = ContractService(contract, web3_service)
        self.contract = contract
    
    def mint_nft(
        self,
        to_address: str,
        private_key: str,
        campaign_id: int,
        contribution_amount: int,
        metadata_uri: str,
        royalty_percentage: int
    ) -> str:
        """Mint a new NFT"""
        try:
            tx_hash = self.contract_service.send_function(
                'mintNFT',
                private_key,
                to_address,
                campaign_id,
                contribution_amount,
                metadata_uri,
                royalty_percentage
            )
            
            # Create blockchain transaction record
            BlockchainTransaction.objects.create(
                tx_hash=tx_hash,
                from_address=Account.from_key(private_key).address,
                to_address=self.contract.address,
                contract=self.contract,
                function_name='mintNFT',
                function_args={
                    'to': to_address,
                    'campaign_id': campaign_id,
                    'contribution_amount': contribution_amount,
                    'metadata_uri': metadata_uri,
                    'royalty_percentage': royalty_percentage
                },
                transaction_type='nft_mint',
                user_id=1,  # This should be passed as parameter
                status='pending'
            )
            
            return tx_hash
        except Exception as e:
            logger.error(f"Error minting NFT: {e}")
            raise
    
    def get_nft_data(self, token_id: int) -> Dict:
        """Get NFT data"""
        try:
            return self.contract_service.call_function('getNFTData', token_id)
        except Exception as e:
            logger.error(f"Error getting NFT data {token_id}: {e}")
            raise
    
    def transfer_nft(
        self,
        from_address: str,
        private_key: str,
        to_address: str,
        token_id: int
    ) -> str:
        """Transfer NFT"""
        try:
            tx_hash = self.contract_service.send_function(
                'transferFrom',
                private_key,
                from_address,
                to_address,
                token_id
            )
            
            # Create blockchain transaction record
            BlockchainTransaction.objects.create(
                tx_hash=tx_hash,
                from_address=from_address,
                to_address=to_address,
                contract=self.contract,
                function_name='transferFrom',
                function_args={
                    'from': from_address,
                    'to': to_address,
                    'token_id': token_id
                },
                transaction_type='nft_transfer',
                user_id=1,  # This should be passed as parameter
                status='pending'
            )
            
            return tx_hash
        except Exception as e:
            logger.error(f"Error transferring NFT: {e}")
            raise


class WalletService:
    """
    Service for wallet management
    """
    
    @staticmethod
    def create_wallet_from_private_key(private_key: str, user_id: int, network_id: int) -> Wallet:
        """Create wallet from private key"""
        try:
            account = Account.from_key(private_key)
            address = account.address
            
            # Check if wallet already exists
            wallet, created = Wallet.objects.get_or_create(
                user_id=user_id,
                address=address,
                network_id=network_id,
                defaults={
                    'wallet_type': 'other',
                    'is_verified': True
                }
            )
            
            return wallet
        except Exception as e:
            logger.error(f"Error creating wallet: {e}")
            raise
    
    @staticmethod
    def verify_wallet_ownership(wallet_address: str, signature: str, message: str) -> bool:
        """Verify wallet ownership using signature"""
        try:
            # Recover address from signature
            message_hash = encode_defunct(text=message)
            recovered_address = Account.recover_message(message_hash, signature=signature)
            
            return recovered_address.lower() == wallet_address.lower()
        except Exception as e:
            logger.error(f"Error verifying wallet ownership: {e}")
            return False
    
    @staticmethod
    def get_user_primary_wallet(user_id: int) -> Optional[Wallet]:
        """Get user's primary wallet"""
        try:
            return Wallet.objects.filter(
                user_id=user_id,
                is_primary=True
            ).first()
        except Exception as e:
            logger.error(f"Error getting primary wallet: {e}")
            return None


class TransactionService:
    """
    Service for transaction management
    """
    
    @staticmethod
    def update_transaction_status(tx_hash: str, status: str, **kwargs):
        """Update transaction status"""
        try:
            transaction = BlockchainTransaction.objects.get(tx_hash=tx_hash)
            transaction.status = status
            
            if 'block_number' in kwargs:
                transaction.block_number = kwargs['block_number']
            if 'block_hash' in kwargs:
                transaction.block_hash = kwargs['block_hash']
            if 'gas_used' in kwargs:
                transaction.gas_used = kwargs['gas_used']
            if 'error_message' in kwargs:
                transaction.error_message = kwargs['error_message']
            
            transaction.updated_at = timezone.now()
            transaction.save()
            
        except BlockchainTransaction.DoesNotExist:
            logger.error(f"Transaction {tx_hash} not found")
        except Exception as e:
            logger.error(f"Error updating transaction status: {e}")
    
    @staticmethod
    def get_pending_transactions() -> List[BlockchainTransaction]:
        """Get all pending transactions"""
        try:
            return BlockchainTransaction.objects.filter(status='pending')
        except Exception as e:
            logger.error(f"Error getting pending transactions: {e}")
            return []
    
    @staticmethod
    def process_transaction_updates():
        """Process pending transaction updates"""
        try:
            pending_transactions = TransactionService.get_pending_transactions()
            
            for transaction in pending_transactions:
                try:
                    # Get network and Web3 service
                    network = transaction.contract.network
                    web3_service = Web3Service(network)
                    
                    # Get transaction receipt
                    receipt = web3_service.get_transaction_receipt(transaction.tx_hash)
                    
                    if receipt:
                        if receipt['status'] == 1:  # Success
                            TransactionService.update_transaction_status(
                                transaction.tx_hash,
                                'confirmed',
                                block_number=receipt['blockNumber'],
                                block_hash=receipt['blockHash'].hex(),
                                gas_used=receipt['gasUsed']
                            )
                        else:  # Failed
                            TransactionService.update_transaction_status(
                                transaction.tx_hash,
                                'failed',
                                error_message='Transaction failed on blockchain'
                            )
                    else:
                        # Check if transaction is still pending or if it's been too long
                        tx_details = web3_service.get_transaction(transaction.tx_hash)
                        if not tx_details:
                            # Transaction not found, might be failed
                            TransactionService.update_transaction_status(
                                transaction.tx_hash,
                                'failed',
                                error_message='Transaction not found on blockchain'
                            )
                
                except Exception as e:
                    logger.error(f"Error processing transaction {transaction.tx_hash}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error processing transaction updates: {e}")
