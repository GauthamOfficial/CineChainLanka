# CineChainLanka Smart Contracts Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying the CineChainLanka smart contracts to various networks.

## Prerequisites
- Node.js (v16 or higher)
- npm or yarn
- Hardhat installed
- Private key with testnet/mainnet ETH/MATIC
- RPC URLs for target networks

## Contract Information

### Deployed Contracts
1. **CampaignFunding.sol** - Main funding contract with escrow functionality
2. **CineChainNFT.sol** - NFT contract for contribution tokens
3. **MockUSDT.sol** - Test USDT token (testnet only)

### Contract Features
- ✅ Campaign creation and management
- ✅ Escrow functionality with automatic refunds
- ✅ NFT minting for contributions
- ✅ Royalty system (ERC2981)
- ✅ Multi-signature support
- ✅ Gas optimization
- ✅ Comprehensive test coverage (42 tests passing)

## Deployment Steps

### 1. Environment Setup
```bash
cd contracts
npm install
```

### 2. Configure Environment Variables
Create a `.env` file in the contracts directory:
```env
# Private key for deployment (without 0x prefix)
PRIVATE_KEY=your_private_key_here

# RPC URLs
POLYGON_RPC_URL=https://polygon-rpc.com
MUMBAI_RPC_URL=https://rpc-mumbai.maticvigil.com
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID

# API Keys for verification
POLYGONSCAN_API_KEY=your_polygonscan_api_key
ETHERSCAN_API_KEY=your_etherscan_api_key
```

### 3. Compile Contracts
```bash
npx hardhat compile
```

### 4. Run Tests
```bash
npx hardhat test
```

### 5. Deploy to Networks

#### Deploy to Polygon Mumbai Testnet
```bash
npx hardhat run scripts/deploy.js --network polygonMumbai
```

#### Deploy to Polygon Mainnet
```bash
npx hardhat run scripts/deploy.js --network polygon
```

#### Deploy to Ethereum Mainnet
```bash
npx hardhat run scripts/deploy.js --network ethereum
```

### 6. Verify Contracts
```bash
npx hardhat verify --network polygonMumbai <CONTRACT_ADDRESS> <CONSTRUCTOR_ARGS>
```

## Deployment Output
The deployment script will create a `deployments/` directory with network-specific deployment information:

```json
{
  "network": "polygonMumbai",
  "chainId": 80001,
  "deployer": "0x...",
  "contracts": {
    "CampaignFunding": {
      "address": "0x...",
      "transactionHash": "0x..."
    },
    "CineChainNFT": {
      "address": "0x...",
      "transactionHash": "0x..."
    },
    "USDT": {
      "address": "0x...",
      "isMock": true
    }
  },
  "timestamp": "2025-01-08T..."
}
```

## Contract Addresses

### Polygon Mumbai Testnet
- **CampaignFunding**: `0x...` (To be deployed)
- **CineChainNFT**: `0x...` (To be deployed)
- **MockUSDT**: `0x...` (To be deployed)

### Polygon Mainnet
- **CampaignFunding**: `0x...` (To be deployed)
- **CineChainNFT**: `0x...` (To be deployed)
- **USDT**: `0xc2132D05D31c914a87C6611C10748AEb04B58e8F`

## Frontend Integration

### Update Web3Context
Update the contract addresses in your frontend Web3Context:

```typescript
const CONTRACT_ADDRESSES = {
  CampaignFunding: "0x...", // Deployed address
  CineChainNFT: "0x...",    // Deployed address
  USDT: "0x...",            // Deployed address
};
```

### Update Network Configuration
Ensure your frontend supports the deployed networks:

```typescript
const NETWORKS = {
  polygon: {
    chainId: 137,
    name: "Polygon",
    rpcUrl: "https://polygon-rpc.com",
    blockExplorer: "https://polygonscan.com"
  },
  mumbai: {
    chainId: 80001,
    name: "Polygon Mumbai",
    rpcUrl: "https://rpc-mumbai.maticvigil.com",
    blockExplorer: "https://mumbai.polygonscan.com"
  }
};
```

## Security Considerations

### Before Mainnet Deployment
1. **Audit**: Complete security audit (see AUDIT_REPORT.md)
2. **Testing**: Deploy to testnet and run comprehensive tests
3. **Verification**: Verify all contracts on block explorer
4. **Monitoring**: Set up monitoring and alerting
5. **Access Control**: Secure private keys and admin functions

### Post-Deployment
1. **Monitor**: Track contract interactions and events
2. **Update**: Keep contracts updated with latest security patches
3. **Backup**: Maintain backup of contract source code and ABI
4. **Documentation**: Keep deployment records and documentation updated

## Troubleshooting

### Common Issues
1. **RPC Connection Failed**: Check RPC URL and network connectivity
2. **Insufficient Funds**: Ensure deployer account has enough ETH/MATIC
3. **Gas Estimation Failed**: Check contract code for issues
4. **Verification Failed**: Ensure constructor arguments match deployment

### Support
For deployment issues, check:
1. Hardhat documentation
2. Network-specific documentation
3. Contract verification guides
4. Gas optimization guides

## Next Steps
1. Deploy to testnet
2. Run integration tests
3. Deploy to mainnet
4. Update frontend configuration
5. Monitor and maintain contracts
