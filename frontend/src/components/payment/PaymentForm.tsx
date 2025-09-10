import React, { useState } from 'react';
import { useAppDispatch } from '../../store/hooks';
import { createTransaction, processPayment } from '../../store/slices/paymentSlice';
import PaymentMethodSelector from './PaymentMethodSelector';
import { 
  CreditCardIcon, 
  DevicePhoneMobileIcon,
  QrCodeIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

interface PaymentFormProps {
  campaignId: number;
  amount: number;
  rewardId?: number;
  onSuccess: () => void;
  onCancel: () => void;
}

interface PaymentDetails {
  accountNumber?: string;
  expiryDate?: string;
  cvv?: string;
  nameOnCard?: string;
  [key: string]: string | undefined;
}

const PaymentForm: React.FC<PaymentFormProps> = ({
  campaignId,
  amount,
  rewardId,
  onSuccess,
  onCancel
}) => {
  const dispatch = useAppDispatch();
  const [selectedMethod, setSelectedMethod] = useState<number | null>(null);
  const [paymentDetails, setPaymentDetails] = useState<PaymentDetails>({});
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleMethodSelect = (methodId: number, methodType: string) => {
    setSelectedMethod(methodId);
    setError(null);
  };

  const handlePaymentDetailsChange = (field: string, value: string) => {
    setPaymentDetails((prev: PaymentDetails) => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedMethod) {
      setError('Please select a payment method');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      // Create transaction
      const transactionResult = await dispatch(createTransaction({
        campaign_id: campaignId,
        amount: amount,
        payment_method_id: selectedMethod,
        payment_details: paymentDetails
      })).unwrap();

      // Process payment
      await dispatch(processPayment(transactionResult.id)).unwrap();
      
      onSuccess();
    } catch (error: any) {
      setError(error.message || 'Payment failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const renderPaymentDetailsForm = () => {
    if (!selectedMethod) return null;

    // This would be dynamic based on the selected payment method
    // For now, showing a generic form
    return (
      <div className="space-y-3">
        <h4 className="font-medium text-gray-900 text-sm">Payment Details</h4>
        
        {/* Generic payment form - in real implementation, this would be specific to each payment method */}
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            Account Number / Card Number
          </label>
          <input
            type="text"
            value={paymentDetails.accountNumber || ''}
            onChange={(e) => handlePaymentDetailsChange('accountNumber', e.target.value)}
            className="w-full px-2 sm:px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            placeholder="Enter account or card number"
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-2 sm:gap-3">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Expiry Date
            </label>
            <input
              type="text"
              value={paymentDetails.expiryDate || ''}
              onChange={(e) => handlePaymentDetailsChange('expiryDate', e.target.value)}
              className="w-full px-2 sm:px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              placeholder="MM/YY"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              CVV
            </label>
            <input
              type="text"
              value={paymentDetails.cvv || ''}
              onChange={(e) => handlePaymentDetailsChange('cvv', e.target.value)}
              className="w-full px-2 sm:px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              placeholder="123"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            Name on Card / Account
          </label>
          <input
            type="text"
            value={paymentDetails.nameOnCard || ''}
            onChange={(e) => handlePaymentDetailsChange('nameOnCard', e.target.value)}
            className="w-full px-2 sm:px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            placeholder="Enter name as it appears on card"
            required
          />
        </div>
      </div>
    );
  };

  return (
    <div className="w-full">
      <div className="mb-3">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Amount to pay:</span>
          <span className="text-base font-bold text-primary-600">
            LKR {amount.toLocaleString()}
          </span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-3">
        <PaymentMethodSelector
          onMethodSelect={handleMethodSelect}
          selectedMethod={selectedMethod}
        />

        {renderPaymentDetailsForm()}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-md flex items-center text-sm">
            <ExclamationTriangleIcon className="h-4 w-4 mr-2" />
            {error}
          </div>
        )}

        <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 px-3 py-2 text-sm border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
            disabled={isProcessing}
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={!selectedMethod || isProcessing}
            className="flex-1 px-3 py-2 text-sm bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
          >
            {isProcessing ? (
              <>
                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-2"></div>
                Processing...
              </>
            ) : (
              <>
                <CheckCircleIcon className="h-3 w-3 mr-2" />
                Pay Now
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default PaymentForm;
