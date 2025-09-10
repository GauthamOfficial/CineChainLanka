import React, { useState } from 'react';
import { useAppSelector, useAppDispatch } from '../../store/hooks';
import { fetchPaymentMethods } from '../../store/slices/paymentSlice';
import { 
  CreditCardIcon, 
  DevicePhoneMobileIcon,
  QrCodeIcon,
  BanknotesIcon
} from '@heroicons/react/24/outline';

interface PaymentMethodSelectorProps {
  onMethodSelect: (methodId: number, methodType: string) => void;
  selectedMethod: number | null;
}

const PaymentMethodSelector: React.FC<PaymentMethodSelectorProps> = ({
  onMethodSelect,
  selectedMethod
}) => {
  const dispatch = useAppDispatch();
  const { paymentMethods, isLoading } = useAppSelector((state) => state.payments);

  React.useEffect(() => {
    dispatch(fetchPaymentMethods());
  }, [dispatch]);

  const getMethodIcon = (methodType: string) => {
    switch (methodType) {
      case 'lanka_qr':
        return <QrCodeIcon className="h-6 w-6" />;
      case 'ez_cash':
      case 'frimi':
        return <DevicePhoneMobileIcon className="h-6 w-6" />;
      case 'bank_transfer':
        return <BanknotesIcon className="h-6 w-6" />;
      case 'credit_card':
      case 'debit_card':
        return <CreditCardIcon className="h-6 w-6" />;
      default:
        return <BanknotesIcon className="h-6 w-6" />;
    }
  };

  const getMethodDescription = (methodType: string) => {
    switch (methodType) {
      case 'lanka_qr':
        return 'Scan QR code with your mobile banking app';
      case 'ez_cash':
        return 'Pay using Dialog eZ Cash mobile wallet';
      case 'frimi':
        return 'Pay using FriMi mobile wallet';
      case 'bank_transfer':
        return 'Direct bank transfer to our account';
      case 'credit_card':
        return 'Pay with your credit card';
      case 'debit_card':
        return 'Pay with your debit card';
      default:
        return 'Secure payment method';
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-2">
        {[...Array(3)].map((_, index) => (
          <div key={index} className="animate-pulse">
            <div className="h-12 bg-gray-200 rounded-lg"></div>
          </div>
        ))}
      </div>
    );
  }

  // Ensure paymentMethods is an array
  const methods = Array.isArray(paymentMethods) ? paymentMethods : [];

  return (
    <div className="space-y-1.5">
      <h3 className="text-sm font-medium text-gray-900 mb-2">Select Payment Method</h3>
      {methods.length === 0 ? (
        <div className="text-center py-4">
          <BanknotesIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
          <p className="text-gray-500 text-sm">No payment methods available</p>
        </div>
      ) : (
        methods
          .filter(method => method.is_active)
          .map((method) => (
            <div
              key={method.id}
              onClick={() => onMethodSelect(method.id, method.payment_type)}
              className={`p-2.5 border-2 rounded-lg cursor-pointer transition-all ${
                selectedMethod === method.id
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center">
                <div className={`p-1 rounded-lg mr-2 ${
                  selectedMethod === method.id ? 'bg-primary-100' : 'bg-gray-100'
                }`}>
                  {getMethodIcon(method.payment_type)}
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900 text-sm">{method.name}</h4>
                  <p className="text-xs text-gray-600">{getMethodDescription(method.payment_type)}</p>
                  {method.processing_fee_percentage > 0 && (
                    <p className="text-xs text-gray-500 mt-0.5">
                      Fee: {method.processing_fee_percentage}% + LKR {method.processing_fee_fixed}
                    </p>
                  )}
                </div>
                <div className="ml-2">
                  <div className={`w-3 h-3 rounded-full border-2 ${
                    selectedMethod === method.id
                      ? 'border-primary-500 bg-primary-500'
                      : 'border-gray-300'
                  }`}>
                    {selectedMethod === method.id && (
                      <div className="w-1 h-1 bg-white rounded-full m-0.5"></div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
      )}
    </div>
  );
};

export default PaymentMethodSelector;
