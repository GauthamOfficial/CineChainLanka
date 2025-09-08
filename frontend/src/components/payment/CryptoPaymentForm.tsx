import React, { useState, useEffect } from 'react';
import { useWeb3 } from '../../contexts/Web3Context';
import Web3 from 'web3';
import { 
  CurrencyDollarIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';

interface CryptoPaymentFormProps {
  campaignId: number;
  amount: number;
  currency: 'USDT' | 'ETH' | 'MATIC';
  onPaymentSuccess: (txHash: string) => void;
  onPaymentError: (error: string) => void;
  className?: string;
}

const CryptoPaymentForm: React.FC<CryptoPaymentFormProps> = ({
  campaignId,
  amount,
  currency,
  onPaymentSuccess,
  onPaymentError,
  className = ''
}) => {
  const { account, chainId, web3, isConnected, switchNetwork } = useWeb3();
  const [isProcessing, setIsProcessing] = useState(false);
  const [gasEstimate, setGasEstimate] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [step, setStep] = useState<'connect' | 'approve' | 'confirm' | 'success'>('connect');

  // Token contract addresses (these would come from your backend)
  const TOKEN_ADDRESSES: {
    USDT: { [key: number]: string };
    ETH: null;
    MATIC: null;
  } = {
    USDT: {
      1: '0xdAC17F958D2ee523a2206206994597C13D831ec7', // Ethereum
      137: '0xc2132D05D31c914a87C6611C10748AEb04B58e8F', // Polygon
      80001: '0x3813e82e6f7098b9583FC0F33a962D02018B6803', // Mumbai
    },
    ETH: null, // Native token
    MATIC: null, // Native token
  };

  const getRequiredChainId = () => {
    switch (currency) {
      case 'USDT':
        return 137; // Default to Polygon for USDT
      case 'ETH':
        return 1; // Ethereum
      case 'MATIC':
        return 137; // Polygon
      default:
        return 1;
    }
  };

  const isCorrectNetwork = () => {
    const requiredChainId = getRequiredChainId();
    return chainId === requiredChainId;
  };

  const handleSwitchNetwork = async () => {
    try {
      const requiredChainId = getRequiredChainId();
      await switchNetwork(requiredChainId);
    } catch (err: any) {
      setError(`Failed to switch network: ${err.message}`);
    }
  };

  const estimateGas = async () => {
    if (!web3 || !account || !isCorrectNetwork()) return;

    try {
      const requiredChainId = getRequiredChainId();
      const tokenAddress = currency === 'USDT' ? TOKEN_ADDRESSES[currency][requiredChainId] : null;

      if (currency === 'ETH' || currency === 'MATIC') {
        // Estimate gas for native token transfer
        const gasEstimate = await web3.eth.estimateGas({
          to: '0x0000000000000000000000000000000000000000', // Placeholder
          value: web3.utils.toWei(amount.toString(), 'ether'),
        });
        setGasEstimate(gasEstimate.toString());
      } else if (tokenAddress) {
        // Estimate gas for ERC20 token transfer
        const tokenContract = new web3.eth.Contract([
          {
            "constant": false,
            "inputs": [
              {"name": "_to", "type": "address"},
              {"name": "_value", "type": "uint256"}
            ],
            "name": "transfer",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
          },
          {
            "constant": false,
            "inputs": [
              {"name": "_spender", "type": "address"},
              {"name": "_value", "type": "uint256"}
            ],
            "name": "approve",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
          },
          {
            "constant": true,
            "inputs": [
              {"name": "_owner", "type": "address"},
              {"name": "_spender", "type": "address"}
            ],
            "name": "allowance",
            "outputs": [{"name": "", "type": "uint256"}],
            "type": "function"
          }
        ], tokenAddress);

        // First check allowance
        const allowance = await tokenContract.methods.allowance(account!, '0x0000000000000000000000000000000000000000').call();
        const requiredAmount = web3.utils.toWei(amount.toString(), 'mwei'); // USDT has 6 decimals

        if (parseInt(String(allowance)) < parseInt(requiredAmount)) {
          setStep('approve');
        } else {
          setStep('confirm');
        }

        // Estimate gas for transfer
        const gasEstimate = await tokenContract.methods.transfer(
          '0x0000000000000000000000000000000000000000', // Placeholder
          requiredAmount
        ).estimateGas({ from: account! });
        setGasEstimate(gasEstimate.toString());
      }
    } catch (err: any) {
      setError(`Gas estimation failed: ${err.message}`);
    }
  };

  const handleApprove = async () => {
    if (!web3 || !account || !isCorrectNetwork()) return;

    setIsProcessing(true);
    setError('');

    try {
      const requiredChainId = getRequiredChainId();
      const tokenAddress = currency === 'USDT' ? TOKEN_ADDRESSES[currency][requiredChainId] : null;

      if (tokenAddress) {
        const tokenContract = new web3.eth.Contract([
          {
            "constant": false,
            "inputs": [
              {"name": "_spender", "type": "address"},
              {"name": "_value", "type": "uint256"}
            ],
            "name": "approve",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
          }
        ], tokenAddress);

        const requiredAmount = web3.utils.toWei(amount.toString(), 'mwei');
        const tx = await tokenContract.methods.approve(
          '0x0000000000000000000000000000000000000000', // Placeholder for campaign contract
          requiredAmount
        ).send({ from: account! });

        setStep('confirm');
      }
    } catch (err: any) {
      setError(`Approval failed: ${err.message}`);
      onPaymentError(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handlePayment = async () => {
    if (!web3 || !account || !isCorrectNetwork()) return;

    setIsProcessing(true);
    setError('');

    try {
      const requiredChainId = getRequiredChainId();
      const tokenAddress = currency === 'USDT' ? TOKEN_ADDRESSES[currency][requiredChainId] : null;

      let tx;

      if (currency === 'ETH' || currency === 'MATIC') {
        // Native token transfer
        tx = await web3.eth.sendTransaction({
          from: account!,
          to: '0x0000000000000000000000000000000000000000', // Placeholder
          value: web3.utils.toWei(amount.toString(), 'ether'),
        });
      } else if (tokenAddress) {
        // ERC20 token transfer
        const tokenContract = new web3.eth.Contract([
          {
            "constant": false,
            "inputs": [
              {"name": "_to", "type": "address"},
              {"name": "_value", "type": "uint256"}
            ],
            "name": "transfer",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
          }
        ], tokenAddress);

        const requiredAmount = web3.utils.toWei(amount.toString(), 'mwei');
        tx = await tokenContract.methods.transfer(
          '0x0000000000000000000000000000000000000000', // Placeholder
          requiredAmount
        ).send({ from: account! });
      }

      if (tx) {
        setStep('success');
        const txHash = tx.transactionHash || (tx as any).hash || String(tx);
        onPaymentSuccess(txHash);
      }
    } catch (err: any) {
      setError(`Payment failed: ${err.message}`);
      onPaymentError(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  useEffect(() => {
    if (isConnected && isCorrectNetwork()) {
      estimateGas();
    }
  }, [isConnected, chainId, amount, currency]);

  if (!isConnected) {
    return (
      <div className={`text-center py-8 ${className}`}>
        <ExclamationTriangleIcon className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Wallet Not Connected</h3>
        <p className="text-gray-600 mb-4">Please connect your wallet to make a crypto payment.</p>
      </div>
    );
  }

  if (!isCorrectNetwork()) {
    return (
      <div className={`text-center py-8 ${className}`}>
        <ExclamationTriangleIcon className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Wrong Network</h3>
        <p className="text-gray-600 mb-4">
          Please switch to {currency === 'ETH' ? 'Ethereum' : 'Polygon'} network to continue.
        </p>
        <button
          onClick={handleSwitchNetwork}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Switch Network
        </button>
      </div>
    );
  }

  if (step === 'success') {
    return (
      <div className={`text-center py-8 ${className}`}>
        <CheckCircleIcon className="h-12 w-12 text-green-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Payment Successful!</h3>
        <p className="text-gray-600">Your contribution has been processed successfully.</p>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg border p-6 ${className}`}>
      <div className="flex items-center space-x-3 mb-6">
        <CurrencyDollarIcon className="h-8 w-8 text-blue-600" />
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Crypto Payment</h3>
          <p className="text-sm text-gray-600">Pay with {currency}</p>
        </div>
      </div>

      <div className="space-y-4">
        {/* Payment Details */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-600">Amount</span>
            <span className="font-semibold">{amount} {currency}</span>
          </div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-600">Campaign ID</span>
            <span className="font-mono text-sm">#{campaignId}</span>
          </div>
          {gasEstimate && (
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Estimated Gas</span>
              <span className="font-mono text-sm">{gasEstimate}</span>
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <ExclamationTriangleIcon className="h-4 w-4 text-red-500" />
              <span className="text-sm text-red-700">{error}</span>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="space-y-2">
          {step === 'approve' && (
            <button
              onClick={handleApprove}
              disabled={isProcessing}
              className="w-full px-4 py-3 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
            >
              {isProcessing ? (
                <ArrowPathIcon className="h-4 w-4 animate-spin" />
              ) : null}
              <span>Approve {currency} Spending</span>
            </button>
          )}

          {step === 'confirm' && (
            <button
              onClick={handlePayment}
              disabled={isProcessing}
              className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
            >
              {isProcessing ? (
                <ArrowPathIcon className="h-4 w-4 animate-spin" />
              ) : null}
              <span>Confirm Payment</span>
            </button>
          )}
        </div>

        {/* Security Notice */}
        <div className="text-xs text-gray-500 text-center">
          <p>Your transaction will be processed on the blockchain and cannot be reversed.</p>
        </div>
      </div>
    </div>
  );
};

export default CryptoPaymentForm;
