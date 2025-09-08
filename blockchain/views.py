import logging
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction

from .models import (
    BlockchainNetwork, SmartContract
)
from .models_extended import (
    Wallet, BlockchainTransaction
)
from .serializers import (
    BlockchainNetworkSerializer, SmartContractSerializer, WalletSerializer,
    BlockchainTransactionSerializer,
    WalletConnectionSerializer, TransactionRequestSerializer, 
    ContractCallSerializer
)
from .services import (
    Web3Service, ContractService, CampaignFundingService, 
    NFTService, WalletService, TransactionService
)
from .ipfs_service import IPFSService, NFTMetadataService

logger = logging.getLogger(__name__)


class BlockchainNetworkViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for blockchain networks"""
    queryset = BlockchainNetwork.objects.filter(is_active=True)
    serializer_class = BlockchainNetworkSerializer
    permission_classes = [permissions.AllowAny]


class SmartContractViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for smart contracts"""
    queryset = SmartContract.objects.filter(is_active=True)
    serializer_class = SmartContractSerializer
    permission_classes = [permissions.AllowAny]


class WalletViewSet(viewsets.ModelViewSet):
    """ViewSet for user wallets"""
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def connect(self, request):
        """Connect a new wallet"""
        serializer = WalletConnectionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Verify wallet ownership
                if not WalletService.verify_wallet_ownership(
                    serializer.validated_data['address'],
                    serializer.validated_data['signature'],
                    serializer.validated_data['message']
                ):
                    return Response(
                        {'error': 'Invalid signature'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Create or get wallet
                wallet, created = Wallet.objects.get_or_create(
                    user=request.user,
                    address=serializer.validated_data['address'],
                    network_id=serializer.validated_data['network_id'],
                    defaults={
                        'wallet_type': serializer.validated_data['wallet_type'],
                        'is_verified': True,
                        'last_used': timezone.now()
                    }
                )
                
                if not created:
                    wallet.last_used = timezone.now()
                    wallet.save()
                
                return Response(WalletSerializer(wallet).data)
                
            except Exception as e:
                logger.error(f"Error connecting wallet: {e}")
                return Response(
                    {'error': 'Failed to connect wallet'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlockchainTransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for blockchain transactions"""
    queryset = BlockchainTransaction.objects.all()
    serializer_class = BlockchainTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return BlockchainTransaction.objects.filter(user=self.request.user)


class NFTViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for NFTs - placeholder for future implementation"""
    # This will be implemented when NFT model is created
    def get_queryset(self):
        return []  # Empty queryset for now
    
    def get_serializer_class(self):
        return None  # Will be implemented when NFT model is created
    
    permission_classes = [permissions.IsAuthenticated]


class IPFSFileViewSet(viewsets.ModelViewSet):
    """ViewSet for IPFS files"""
    from .models_extended import IPFSFile
    queryset = IPFSFile.objects.all()
    serializer_class = None  # Will be implemented when IPFSSerializer is uncommented
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return IPFSFile.objects.filter(uploaded_by=self.request.user)


class ContractInteractionView(APIView):
    """View for smart contract interactions"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Interact with a smart contract"""
        serializer = ContractCallSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Implementation will be added when contract service is ready
                return Response({'message': 'Contract interaction not yet implemented'})
            except Exception as e:
                logger.error(f"Error in contract interaction: {e}")
                return Response(
                    {'error': 'Contract interaction failed'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionStatusView(APIView):
    """View for checking transaction status"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, tx_hash):
        """Get transaction status by hash"""
        try:
            transaction = get_object_or_404(
                BlockchainTransaction, 
                tx_hash=tx_hash, 
                user=request.user
            )
            serializer = BlockchainTransactionSerializer(transaction)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error getting transaction status: {e}")
            return Response(
                {'error': 'Failed to get transaction status'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class Web3StatusView(APIView):
    """View for checking Web3 connection status"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get Web3 connection status"""
        try:
            # Implementation will be added when Web3 service is ready
            return Response({
                'status': 'connected',
                'networks': [],
                'message': 'Web3 status check not yet implemented'
            })
        except Exception as e:
            logger.error(f"Error checking Web3 status: {e}")
            return Response(
                {'error': 'Failed to check Web3 status'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )