import React from 'react';
import { useTranslation } from 'react-i18next';
import { 
  DocumentTextIcon,
  PhotoIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

const KYC: React.FC = () => {
  const { t } = useTranslation();

  const documentTypes = [
    { name: t('kyc.nationalId'), icon: DocumentTextIcon },
    { name: t('kyc.passport'), icon: DocumentTextIcon },
    { name: t('kyc.driversLicense'), icon: DocumentTextIcon },
    { name: t('kyc.utilityBill'), icon: DocumentTextIcon },
    { name: t('kyc.bankStatement'), icon: DocumentTextIcon },
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">{t('kyc.title')}</h1>
          <p className="text-xl text-gray-600">{t('kyc.subtitle')}</p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <CheckCircleIcon className="h-16 w-16 text-primary-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Coming Soon</h2>
            <p className="text-gray-600">
              We're working hard to bring you a seamless KYC verification experience. 
              This feature will be available soon!
            </p>
          </div>

          <div className="border-t border-gray-200 pt-8">
            <h3 className="text-lg font-medium text-gray-900 mb-6 text-center">
              {t('kyc.uploadDocuments')}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {documentTypes.map((doc, index) => (
                <div key={index} className="flex items-center p-4 border border-gray-200 rounded-lg hover:border-primary-300 transition-colors">
                  <doc.icon className="h-6 w-6 text-gray-400 mr-3" />
                  <span className="text-sm font-medium text-gray-700">{doc.name}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-8 text-center">
            <button
              disabled
              className="px-6 py-3 bg-gray-300 text-gray-500 rounded-md cursor-not-allowed"
            >
              {t('kyc.uploadDocuments')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KYC;

