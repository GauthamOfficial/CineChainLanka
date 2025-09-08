import React, { useState } from 'react';
import { useWeb3 } from '../../contexts/Web3Context';
import { 
  WalletIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';

interface WalletConnectionProps {
  onConnect?: (account: string) => void;
  onDisconnect?: () => void;
  className?: string;
}

const WalletConnection: React.FC<WalletConnectionProps> = ({
  onConnect,
  onDisconnect,
  className = ''
}) => {
  const { 
    account, 
    chainId, 
    connect, 
    disconnect, 
    switchNetwork, 
    isConnected, 
    isLoading, 
    error 
  } = useWeb3();
  
  const [showNetworkMenu, setShowNetworkMenu] = useState(false);

  const handleConnect = async () => {
    try {
      await connect();
      if (account && onConnect) {
        onConnect(account);
      }
    } catch (err) {
      console.error('Connection failed:', err);
    }
  };

  const handleDisconnect = () => {
    disconnect();
    if (onDisconnect) {
      onDisconnect();
    }
  };

  const handleSwitchNetwork = async (targetChainId: number) => {
    try {
      await switchNetwork(targetChainId);
      setShowNetworkMenu(false);
    } catch (err) {
      console.error('Network switch failed:', err);
    }
  };

  const formatAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const getNetworkName = (chainId: number | null) => {
    switch (chainId) {
      case 1:
        return 'Ethereum';
      case 137:
        return 'Polygon';
      case 80001:
        return 'Polygon Mumbai';
      default:
        return 'Unknown';
    }
  };

  const getNetworkColor = (chainId: number | null) => {
    switch (chainId) {
      case 1:
        return 'bg-blue-100 text-blue-800';
      case 137:
        return 'bg-purple-100 text-purple-800';
      case 80001:
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <ArrowPathIcon className="h-5 w-5 animate-spin text-blue-600" />
        <span className="text-sm text-gray-600">Connecting...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />
        <span className="text-sm text-red-600">{error}</span>
        <button
          onClick={handleConnect}
          className="ml-2 text-sm text-blue-600 hover:text-blue-800 underline"
        >
          Retry
        </button>
      </div>
    );
  }

  if (isConnected && account) {
    return (
      <div className={`flex items-center space-x-3 ${className}`}>
        {/* Network Indicator */}
        <div className="relative">
          <button
            onClick={() => setShowNetworkMenu(!showNetworkMenu)}
            className={`px-3 py-1 rounded-full text-xs font-medium ${getNetworkColor(chainId)}`}
          >
            {getNetworkName(chainId)}
          </button>
          
          {showNetworkMenu && (
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border">
              <div className="py-1">
                <button
                  onClick={() => handleSwitchNetwork(1)}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Ethereum Mainnet
                </button>
                <button
                  onClick={() => handleSwitchNetwork(137)}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Polygon Mainnet
                </button>
                <button
                  onClick={() => handleSwitchNetwork(80001)}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Polygon Mumbai Testnet
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Account Info */}
        <div className="flex items-center space-x-2">
          <CheckCircleIcon className="h-5 w-5 text-green-500" />
          <span className="text-sm font-medium text-gray-900">
            {formatAddress(account)}
          </span>
        </div>

        {/* Disconnect Button */}
        <button
          onClick={handleDisconnect}
          className="text-sm text-gray-500 hover:text-gray-700 underline"
        >
          Disconnect
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={handleConnect}
      className={`flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors ${className}`}
    >
      <WalletIcon className="h-5 w-5" />
      <span>Connect Wallet</span>
    </button>
  );
};

export default WalletConnection;
