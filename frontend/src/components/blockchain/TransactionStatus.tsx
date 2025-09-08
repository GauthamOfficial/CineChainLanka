import React, { useState, useEffect } from 'react';
import { 
  CheckCircleIcon, 
  XCircleIcon, 
  ClockIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { CheckCircleIcon as CheckCircleSolidIcon } from '@heroicons/react/24/solid';

interface TransactionStatusProps {
  txHash: string;
  status: 'pending' | 'confirmed' | 'failed' | 'cancelled';
  blockNumber?: number;
  gasUsed?: number;
  errorMessage?: string;
  onStatusChange?: (status: string) => void;
  className?: string;
}

const TransactionStatus: React.FC<TransactionStatusProps> = ({
  txHash,
  status,
  blockNumber,
  gasUsed,
  errorMessage,
  onStatusChange,
  className = ''
}) => {
  const [isRefreshing, setIsRefreshing] = useState(false);

  const getStatusIcon = () => {
    switch (status) {
      case 'confirmed':
        return <CheckCircleSolidIcon className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'cancelled':
        return <XCircleIcon className="h-5 w-5 text-gray-500" />;
      case 'pending':
      default:
        return <ClockIcon className="h-5 w-5 text-yellow-500" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'confirmed':
        return 'text-green-600 bg-green-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      case 'cancelled':
        return 'text-gray-600 bg-gray-100';
      case 'pending':
      default:
        return 'text-yellow-600 bg-yellow-100';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'confirmed':
        return 'Confirmed';
      case 'failed':
        return 'Failed';
      case 'cancelled':
        return 'Cancelled';
      case 'pending':
      default:
        return 'Pending';
    }
  };

  const formatTxHash = (hash: string) => {
    return `${hash.slice(0, 6)}...${hash.slice(-4)}`;
  };

  const getExplorerUrl = (hash: string) => {
    // This would be determined based on the network
    // For now, using Etherscan as default
    return `https://etherscan.io/tx/${hash}`;
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    // Simulate API call to refresh transaction status
    setTimeout(() => {
      setIsRefreshing(false);
      if (onStatusChange) {
        onStatusChange('confirmed'); // Simulate status change
      }
    }, 1000);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className={`bg-white rounded-lg border p-4 ${className}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor()}`}>
            {getStatusText()}
          </span>
        </div>
        
        <button
          onClick={handleRefresh}
          disabled={isRefreshing || status === 'confirmed'}
          className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ArrowPathIcon className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <div className="space-y-2">
        {/* Transaction Hash */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Transaction Hash:</span>
          <div className="flex items-center space-x-2">
            <span className="text-sm font-mono text-gray-900">
              {formatTxHash(txHash)}
            </span>
            <button
              onClick={() => copyToClipboard(txHash)}
              className="text-xs text-blue-600 hover:text-blue-800 underline"
            >
              Copy
            </button>
          </div>
        </div>

        {/* Block Number */}
        {blockNumber && (
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Block Number:</span>
            <span className="text-sm font-mono text-gray-900">
              {blockNumber.toLocaleString()}
            </span>
          </div>
        )}

        {/* Gas Used */}
        {gasUsed && (
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Gas Used:</span>
            <span className="text-sm font-mono text-gray-900">
              {gasUsed.toLocaleString()}
            </span>
          </div>
        )}

        {/* Error Message */}
        {errorMessage && (
          <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-start space-x-2">
              <ExclamationTriangleIcon className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm text-red-800 font-medium">Error</p>
                <p className="text-sm text-red-700 mt-1">{errorMessage}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="mt-4 flex space-x-2">
        <a
          href={getExplorerUrl(txHash)}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 px-3 py-2 text-sm text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 transition-colors text-center"
        >
          View on Explorer
        </a>
        
        {status === 'pending' && (
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="px-3 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isRefreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        )}
      </div>

      {/* Progress Indicator for Pending Transactions */}
      {status === 'pending' && (
        <div className="mt-3">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
              <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
              <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
            </div>
            <span>Transaction is being processed...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default TransactionStatus;
