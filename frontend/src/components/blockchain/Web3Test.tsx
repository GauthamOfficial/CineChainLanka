import React from 'react';
import { useWeb3 } from '../../contexts/Web3Context';

const Web3Test: React.FC = () => {
  const { 
    account, 
    chainId, 
    web3,
    isConnected, 
    isLoading, 
    error,
    connect,
    disconnect 
  } = useWeb3();

  return (
    <div className="p-4 bg-gray-100 rounded-lg">
      <h3 className="text-lg font-semibold mb-4">Web3 Connection Test</h3>
      
      <div className="space-y-2">
        <div>
          <strong>Connected:</strong> {isConnected ? 'Yes' : 'No'}
        </div>
        <div>
          <strong>Loading:</strong> {isLoading ? 'Yes' : 'No'}
        </div>
        <div>
          <strong>Account:</strong> {account || 'Not connected'}
        </div>
        <div>
          <strong>Chain ID:</strong> {chainId || 'Unknown'}
        </div>
        <div>
          <strong>Web3 Instance:</strong> {web3 ? 'Available' : 'Not available'}
        </div>
        {error && (
          <div className="text-red-600">
            <strong>Error:</strong> {error}
          </div>
        )}
      </div>

      <div className="mt-4 space-x-2">
        {!isConnected ? (
          <button
            onClick={connect}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Connect Wallet
          </button>
        ) : (
          <button
            onClick={disconnect}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Disconnect
          </button>
        )}
      </div>
    </div>
  );
};

export default Web3Test;
