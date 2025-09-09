import logging
import json
from decimal import Decimal
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.utils import timezone
from web3 import Web3
from .models import RevenueEntry, RoyaltyDistribution, InvestorRoyalty, Campaign
from campaigns.models import Campaign as CampaignModel

logger = logging.getLogger(__name__)


class RoyaltyDistributionService:
    """Service for managing royalty distribution on blockchain"""
    
    def __init__(self):
        self.w3 = None
        self.contract = None
        self._initialize_web3()
    
    def _initialize_web3(self):
        """Initialize Web3 connection and contract"""
        try:
            # Get contract addresses from settings
            royalty_contract_address = getattr(settings, 'ROYALTY_DISTRIBUTION_ADDRESS', None)
            usdt_contract_address = getattr(settings, 'USDT_CONTRACT_ADDRESS', None)
            rpc_url = getattr(settings, 'WEB3_RPC_URL', 'http://localhost:8545')
            
            if not royalty_contract_address or not usdt_contract_address:
                logger.error("Contract addresses not configured in settings")
                return
            
            # Initialize Web3
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))
            
            if not self.w3.is_connected():
                logger.error("Failed to connect to Web3 provider")
                return
            
            # Load contract ABI
            with open('contracts/artifacts/src/RoyaltyDistribution.sol/RoyaltyDistribution.json', 'r') as f:
                contract_abi = json.load(f)['abi']
            
            # Initialize contract
            self.contract = self.w3.eth.contract(
                address=royalty_contract_address,
                abi=contract_abi
            )
            
            logger.info(f"RoyaltyDistribution contract initialized at {royalty_contract_address}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Web3: {e}")
    
    def create_campaign_on_blockchain(self, campaign_id: int) -> bool:
        """Create a campaign on the blockchain for royalty distribution"""
        try:
            if not self.contract:
                logger.error("Contract not initialized")
                return False
            
            campaign = CampaignModel.objects.get(id=campaign_id)
            
            # Calculate percentages (in basis points)
            creator_percentage = int(Decimal('30.00') * 100)  # 30%
            platform_percentage = int(Decimal('5.00') * 100)  # 5%
            
            # Get the account for transactions
            account = self.w3.eth.account.from_key(settings.PRIVATE_KEY)
            
            # Create campaign on blockchain
            tx = self.contract.functions.createCampaign(
                campaign.creator.wallet_address,
                int(campaign.funding_goal * 10**6),  # Convert to USDT decimals
                creator_percentage,
                platform_percentage
            ).build_transaction({
                'from': account.address,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(account.address),
            })
            
            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Campaign {campaign_id} created on blockchain: {tx_hash.hex()}")
                return True
            else:
                logger.error(f"Transaction failed for campaign {campaign_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating campaign on blockchain: {e}")
            return False
    
    def add_investor_share(self, campaign_id: int, nft_id: int, investor_address: str, contribution_amount: Decimal) -> bool:
        """Add investor share to the blockchain"""
        try:
            if not self.contract:
                logger.error("Contract not initialized")
                return False
            
            account = self.w3.eth.account.from_key(settings.PRIVATE_KEY)
            
            # Add investor share
            tx = self.contract.functions.addInvestorShare(
                campaign_id,
                nft_id,
                investor_address,
                int(contribution_amount * 10**6)  # Convert to USDT decimals
            ).build_transaction({
                'from': account.address,
                'gas': 150000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(account.address),
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(tx, account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Investor share added for campaign {campaign_id}, NFT {nft_id}")
                return True
            else:
                logger.error(f"Failed to add investor share for campaign {campaign_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding investor share: {e}")
            return False
    
    def receive_revenue(self, campaign_id: int, amount: Decimal) -> bool:
        """Send revenue to the blockchain contract"""
        try:
            if not self.contract:
                logger.error("Contract not initialized")
                return False
            
            account = self.w3.eth.account.from_key(settings.PRIVATE_KEY)
            
            # First, approve USDT transfer
            usdt_contract_address = getattr(settings, 'USDT_CONTRACT_ADDRESS', None)
            if not usdt_contract_address:
                logger.error("USDT contract address not configured")
                return False
            
            # Load USDT ABI
            with open('contracts/artifacts/src/MockUSDT.sol/MockUSDT.json', 'r') as f:
                usdt_abi = json.load(f)['abi']
            
            usdt_contract = self.w3.eth.contract(
                address=usdt_contract_address,
                abi=usdt_abi
            )
            
            # Approve USDT transfer
            approve_tx = usdt_contract.functions.approve(
                self.contract.address,
                int(amount * 10**6)
            ).build_transaction({
                'from': account.address,
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(account.address),
            })
            
            signed_approve_tx = self.w3.eth.account.sign_transaction(approve_tx, account.key)
            approve_tx_hash = self.w3.eth.send_raw_transaction(signed_approve_tx.rawTransaction)
            self.w3.eth.wait_for_transaction_receipt(approve_tx_hash)
            
            # Send revenue to contract
            tx = self.contract.functions.receiveRevenue(
                campaign_id,
                int(amount * 10**6)
            ).build_transaction({
                'from': account.address,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(account.address),
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(tx, account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Revenue {amount} USDT sent to campaign {campaign_id}: {tx_hash.hex()}")
                return True
            else:
                logger.error(f"Failed to send revenue for campaign {campaign_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending revenue to blockchain: {e}")
            return False
    
    def distribute_royalties(self, campaign_id: int) -> bool:
        """Distribute royalties on the blockchain"""
        try:
            if not self.contract:
                logger.error("Contract not initialized")
                return False
            
            account = self.w3.eth.account.from_key(settings.PRIVATE_KEY)
            
            # Distribute royalties
            tx = self.contract.functions.distributeRoyalties(campaign_id).build_transaction({
                'from': account.address,
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(account.address),
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(tx, account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Royalties distributed for campaign {campaign_id}: {tx_hash.hex()}")
                
                # Update local database
                self._update_local_royalty_distribution(campaign_id, tx_hash.hex())
                return True
            else:
                logger.error(f"Failed to distribute royalties for campaign {campaign_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error distributing royalties: {e}")
            return False
    
    def _update_local_royalty_distribution(self, campaign_id: int, tx_hash: str):
        """Update local database with royalty distribution results"""
        try:
            campaign = CampaignModel.objects.get(id=campaign_id)
            
            # Get the latest revenue entry for this campaign
            latest_revenue = RevenueEntry.objects.filter(
                campaign=campaign,
                status='verified'
            ).order_by('-revenue_date').first()
            
            if not latest_revenue:
                logger.warning(f"No verified revenue found for campaign {campaign_id}")
                return
            
            # Create royalty distribution record
            distribution = RoyaltyDistribution.objects.create(
                campaign=campaign,
                revenue_entry=latest_revenue,
                distribution_date=timezone.now(),
                creator_amount=latest_revenue.amount * Decimal('0.30'),
                platform_amount=latest_revenue.amount * Decimal('0.05'),
                total_investor_amount=latest_revenue.amount * Decimal('0.65'),
                status='completed',
                blockchain_tx_hash=tx_hash
            )
            
            # Create investor royalty records
            # This would need to be populated with actual investor data
            # For now, we'll create a placeholder
            logger.info(f"Royalty distribution record created: {distribution.id}")
            
        except Exception as e:
            logger.error(f"Error updating local royalty distribution: {e}")
    
    def get_campaign_royalty_info(self, campaign_id: int) -> Dict:
        """Get royalty information for a campaign from blockchain"""
        try:
            if not self.contract:
                return {}
            
            # Get campaign info from blockchain
            campaign_info = self.contract.functions.campaigns(campaign_id).call()
            
            return {
                'creator': campaign_info[0],
                'total_raised': campaign_info[1] / 10**6,  # Convert from USDT decimals
                'creator_percentage': campaign_info[2],
                'platform_percentage': campaign_info[3],
                'is_active': campaign_info[4],
                'total_revenue': campaign_info[5] / 10**6,
                'total_distributed': campaign_info[6] / 10**6,
            }
            
        except Exception as e:
            logger.error(f"Error getting campaign royalty info: {e}")
            return {}
    
    def get_investor_royalties(self, investor_address: str) -> Decimal:
        """Get claimable royalties for an investor"""
        try:
            if not self.contract:
                return Decimal('0')
            
            # Get investor royalties from blockchain
            royalties = self.contract.functions.investorRoyalties(investor_address).call()
            return Decimal(royalties) / Decimal(10**6)  # Convert from USDT decimals
            
        except Exception as e:
            logger.error(f"Error getting investor royalties: {e}")
            return Decimal('0')
    
    def claim_investor_royalties(self, investor_address: str, private_key: str) -> bool:
        """Claim royalties for an investor"""
        try:
            if not self.contract:
                logger.error("Contract not initialized")
                return False
            
            account = self.w3.eth.account.from_key(private_key)
            
            # Claim royalties
            tx = self.contract.functions.claimInvestorRoyalties().build_transaction({
                'from': account.address,
                'gas': 150000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(account.address),
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(tx, account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Royalties claimed by {investor_address}: {tx_hash.hex()}")
                return True
            else:
                logger.error(f"Failed to claim royalties for {investor_address}")
                return False
                
        except Exception as e:
            logger.error(f"Error claiming investor royalties: {e}")
            return False
