import React from 'react';
import { 
  CurrencyDollarIcon,
  UserGroupIcon,
  BanknotesIcon,
  ChartBarIcon,
  ClockIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

interface RevenueSummaryProps {
  data: {
    total_revenue: number;
    total_creator_royalties: number;
    total_platform_fees: number;
    total_investor_royalties: number;
    total_distributions: number;
    pending_royalties: number;
    last_distribution_date?: string;
  };
}

const RevenueSummary: React.FC<RevenueSummaryProps> = ({ data }) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const summaryCards = [
    {
      title: 'Total Revenue',
      value: formatCurrency(data.total_revenue),
      icon: CurrencyDollarIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-600',
    },
    {
      title: 'Creator Royalties',
      value: formatCurrency(data.total_creator_royalties),
      icon: UserGroupIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      iconColor: 'text-green-600',
    },
    {
      title: 'Investor Royalties',
      value: formatCurrency(data.total_investor_royalties),
      icon: BanknotesIcon,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
      iconColor: 'text-yellow-600',
    },
    {
      title: 'Platform Fees',
      value: formatCurrency(data.total_platform_fees),
      icon: ChartBarIcon,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      iconColor: 'text-red-600',
    },
    {
      title: 'Total Distributions',
      value: data.total_distributions.toString(),
      icon: CheckCircleIcon,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      iconColor: 'text-purple-600',
    },
    {
      title: 'Pending Royalties',
      value: formatCurrency(data.pending_royalties),
      icon: ClockIcon,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      iconColor: 'text-orange-600',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {summaryCards.map((card, index) => (
          <div key={index} className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className={`p-3 rounded-lg ${card.bgColor}`}>
                <card.icon className={`h-6 w-6 ${card.iconColor}`} />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">{card.title}</p>
                <p className={`text-2xl font-bold ${card.color}`}>{card.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Additional Info */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Distribution Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Last Distribution</p>
            <p className="text-lg font-medium text-gray-900">
              {formatDate(data.last_distribution_date)}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Distribution Status</p>
            <p className="text-lg font-medium text-gray-900">
              {data.total_distributions > 0 ? 'Active' : 'No distributions yet'}
            </p>
          </div>
        </div>
      </div>

      {/* Revenue Breakdown */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue Breakdown</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Creator Share</span>
            <span className="text-sm font-medium text-gray-900">
              {data.total_revenue > 0 
                ? `${((data.total_creator_royalties / data.total_revenue) * 100).toFixed(1)}%`
                : '0%'
              }
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Investor Share</span>
            <span className="text-sm font-medium text-gray-900">
              {data.total_revenue > 0 
                ? `${((data.total_investor_royalties / data.total_revenue) * 100).toFixed(1)}%`
                : '0%'
              }
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Platform Share</span>
            <span className="text-sm font-medium text-gray-900">
              {data.total_revenue > 0 
                ? `${((data.total_platform_fees / data.total_revenue) * 100).toFixed(1)}%`
                : '0%'
              }
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RevenueSummary;
