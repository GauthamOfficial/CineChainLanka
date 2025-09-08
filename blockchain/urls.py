from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'networks', views.BlockchainNetworkViewSet)
router.register(r'contracts', views.SmartContractViewSet)
router.register(r'wallets', views.WalletViewSet)
router.register(r'transactions', views.BlockchainTransactionViewSet)
# router.register(r'nfts', views.NFTViewSet)  # Temporarily disabled until NFT model is implemented
router.register(r'ipfs', views.IPFSFileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('contracts/interact/', views.ContractInteractionView.as_view(), name='contract-interact'),
    path('transactions/<str:tx_hash>/', views.TransactionStatusView.as_view(), name='transaction-status'),
    path('web3/status/', views.Web3StatusView.as_view(), name='web3-status'),
]
