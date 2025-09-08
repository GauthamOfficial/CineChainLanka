# Phase 2: Blockchain Integration & NFT System - Implementation Guide

## Overview
Phase 2 of CineChainLanka focuses on integrating blockchain technology, smart contracts, and NFT functionality into the platform. This phase enables decentralized funding, NFT minting for contributions, and IPFS-based metadata storage.

## 🚀 Features Implemented

### 1. Smart Contracts
- **CampaignFunding.sol**: Manages campaign funding with escrow functionality
- **CineChainNFT.sol**: Handles NFT minting with royalty support
- **MockUSDT.sol**: Test token for development and testing

### 2. Backend Blockchain Integration
- **Web3Service**: Core Web3 interaction service
- **ContractService**: Smart contract interaction wrapper
- **CampaignFundingService**: Campaign-specific blockchain operations
- **NFTService**: NFT minting and management
- **IPFSService**: Decentralized file storage
- **WalletService**: Wallet management and verification

### 3. Frontend Web3 Integration
- **Web3Context**: React context for Web3 state management
- **WalletConnection**: MetaMask and wallet connection component
- **NFTDisplay**: NFT viewing and interaction component
- **TransactionStatus**: Real-time transaction monitoring
- **CryptoPaymentForm**: Cryptocurrency payment processing

### 4. Database Models
- **BlockchainNetwork**: Supported blockchain networks
- **SmartContract**: Deployed contract information
- **Wallet**: User wallet addresses
- **BlockchainTransaction**: Transaction tracking
- **NFT**: NFT metadata and ownership
- **IPFSFile**: IPFS file storage records

## 📁 File Structure

```
├── contracts/
│   ├── CampaignFunding.sol          # Funding smart contract
│   ├── CineChainNFT.sol             # NFT smart contract
│   ├── MockUSDT.sol                 # Test USDT token
│   ├── hardhat.config.js            # Hardhat configuration
│   ├── package.json                 # Contract dependencies
│   ├── scripts/
│   │   └── deploy.js                # Deployment script
│   └── test/
│       ├── CampaignFunding.test.js  # Funding contract tests
│       └── CineChainNFT.test.js     # NFT contract tests
├── blockchain/
│   ├── models.py                    # Blockchain models
│   ├── models_extended.py           # Extended models
│   ├── services.py                  # Web3 services
│   ├── ipfs_service.py              # IPFS integration
│   ├── serializers.py               # API serializers
│   ├── views.py                     # API views
│   ├── urls.py                      # URL routing
│   ├── admin.py                     # Admin interface
│   └── management/commands/
│       └── setup_blockchain_networks.py
└── frontend/src/
    ├── contexts/
    │   └── Web3Context.tsx          # Web3 React context
    └── components/blockchain/
        ├── WalletConnection.tsx     # Wallet connection
        ├── NFTDisplay.tsx           # NFT display
        └── TransactionStatus.tsx    # Transaction monitoring
    └── components/payment/
        └── CryptoPaymentForm.tsx    # Crypto payments
```

## 🛠️ Setup Instructions

### 1. Backend Setup

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Database Migration
```bash
python manage.py makemigrations blockchain
python manage.py migrate
```

#### Setup Blockchain Networks
```bash
python manage.py setup_blockchain_networks
```

#### Environment Variables
Add to your `.env` file:
```env
# IPFS Configuration
PINATA_API_KEY=your_pinata_api_key
PINATA_SECRET_KEY=your_pinata_secret_key

# Blockchain RPC URLs
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
POLYGON_RPC_URL=https://polygon-rpc.com
MUMBAI_RPC_URL=https://rpc-mumbai.maticvigil.com

# Smart Contract Addresses (after deployment)
CAMPAIGN_FUNDING_CONTRACT_ADDRESS=0x...
NFT_CONTRACT_ADDRESS=0x...
USDT_CONTRACT_ADDRESS=0x...
```

### 2. Smart Contracts Setup

#### Install Dependencies
```bash
cd contracts
npm install
```

#### Compile Contracts
```bash
npx hardhat compile
```

#### Run Tests
```bash
npx hardhat test
```

#### Deploy Contracts
```bash
# Local network
npx hardhat run scripts/deploy.js --network localhost

# Testnet
npx hardhat run scripts/deploy.js --network polygonMumbai

# Mainnet
npx hardhat run scripts/deploy.js --network polygon
```

### 3. Frontend Setup

#### Install Dependencies
```bash
cd frontend
npm install
```

#### Start Development Server
```bash
npm start
```

## 🔧 Configuration

### Smart Contract Configuration

#### CampaignFunding Contract
- **Platform Fee**: 3% (configurable)
- **Escrow**: Automatic fund holding until campaign success
- **Refunds**: Automatic for failed campaigns
- **Multi-signature**: Support for multi-sig wallets

#### CineChainNFT Contract
- **Royalty**: Up to 10% (ERC2981 compliant)
- **Transferability**: Configurable per NFT
- **Metadata**: IPFS-based storage
- **Batch Minting**: Support for multiple NFTs

### IPFS Configuration
- **Primary Gateway**: ipfs.io
- **Backup Gateways**: Pinata, Cloudflare
- **Pin Service**: Pinata (optional)
- **File Types**: Images, videos, metadata

### Web3 Configuration
- **Supported Wallets**: MetaMask, Trust Wallet, WalletConnect
- **Networks**: Ethereum, Polygon, BSC
- **Gas Management**: Automatic estimation and optimization

## 📊 API Endpoints

### Blockchain Networks
- `GET /api/blockchain/networks/` - List active networks
- `GET /api/blockchain/networks/{id}/` - Get network details

### Smart Contracts
- `GET /api/blockchain/contracts/` - List deployed contracts
- `GET /api/blockchain/contracts/{id}/` - Get contract details

### Wallets
- `GET /api/blockchain/wallets/` - User's wallets
- `POST /api/blockchain/wallets/connect/` - Connect new wallet
- `POST /api/blockchain/wallets/{id}/set_primary/` - Set primary wallet
- `GET /api/blockchain/wallets/{id}/balance/` - Get wallet balance

### Transactions
- `GET /api/blockchain/transactions/` - User's transactions
- `GET /api/blockchain/transactions/{tx_hash}/` - Transaction details
- `POST /api/blockchain/transactions/{tx_hash}/` - Update status

### NFTs
- `GET /api/blockchain/nfts/` - User's NFTs
- `POST /api/blockchain/nfts/create_nft/` - Create new NFT
- `POST /api/blockchain/nfts/{id}/transfer/` - Transfer NFT

### IPFS
- `GET /api/blockchain/ipfs/` - User's IPFS files
- `POST /api/blockchain/ipfs/upload/` - Upload file to IPFS

### Contract Interaction
- `POST /api/blockchain/contracts/interact/` - Call contract function

### Web3 Status
- `GET /api/blockchain/web3/status/` - Web3 connection status

## 🔐 Security Considerations

### Smart Contract Security
- **Reentrancy Protection**: All external calls protected
- **Access Control**: Owner-only functions properly secured
- **Input Validation**: All parameters validated
- **Gas Optimization**: Efficient gas usage

### Backend Security
- **Private Key Management**: Never store private keys in database
- **Signature Verification**: Wallet ownership verification
- **Rate Limiting**: API rate limiting implemented
- **Input Sanitization**: All inputs properly sanitized

### Frontend Security
- **Wallet Connection**: Secure wallet connection flow
- **Transaction Signing**: User-controlled transaction signing
- **Error Handling**: Proper error handling and user feedback

## 🧪 Testing

### Smart Contract Tests
```bash
cd contracts
npx hardhat test
npx hardhat coverage
```

### Backend Tests
```bash
python manage.py test blockchain
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📈 Monitoring & Analytics

### Transaction Monitoring
- Real-time transaction status updates
- Gas usage tracking
- Success/failure rate monitoring
- Error logging and alerting

### IPFS Monitoring
- File upload success rates
- Gateway availability monitoring
- Pin status tracking
- Storage usage analytics

### Web3 Monitoring
- Network connection status
- Wallet connection success rates
- Transaction confirmation times
- User engagement metrics

## 🚀 Deployment

### Smart Contract Deployment
1. Deploy to testnet first
2. Run comprehensive tests
3. Security audit (recommended)
4. Deploy to mainnet
5. Verify contracts on block explorer

### Backend Deployment
1. Set up production environment variables
2. Configure IPFS service
3. Set up blockchain RPC endpoints
4. Deploy to production server
5. Run database migrations

### Frontend Deployment
1. Build production bundle
2. Configure API endpoints
3. Deploy to CDN
4. Set up monitoring

## 🔄 Maintenance

### Regular Tasks
- Monitor transaction status updates
- Update IPFS gateway configurations
- Monitor gas price fluctuations
- Update smart contract addresses
- Backup IPFS data

### Emergency Procedures
- Pause contract functions if needed
- Emergency fund withdrawal
- IPFS data recovery
- Wallet connection troubleshooting

## 📚 Documentation

### Smart Contract Documentation
- Function documentation in contracts
- Deployment guides
- Integration examples
- Security best practices

### API Documentation
- Swagger/OpenAPI documentation
- Endpoint examples
- Error code reference
- Rate limiting information

### Frontend Documentation
- Component documentation
- Hook usage examples
- Integration guides
- Troubleshooting guides

## 🎯 Next Steps (Phase 3)

### Planned Features
- Automated royalty distribution
- Advanced analytics dashboard
- Mobile application
- NFT marketplace
- Revenue integration

### Technical Improvements
- Gas optimization
- Batch processing
- Advanced caching
- Performance monitoring
- Security enhancements

## 🤝 Support

### Development Support
- GitHub issues for bug reports
- Documentation for common issues
- Community forums for questions
- Developer chat for real-time help

### User Support
- Help center with guides
- Video tutorials
- Live chat support
- Email support

---

**Phase 2 Status**: ✅ **COMPLETED**

All core blockchain integration features have been implemented and are ready for testing and deployment. The platform now supports decentralized funding, NFT minting, and IPFS-based metadata storage.
