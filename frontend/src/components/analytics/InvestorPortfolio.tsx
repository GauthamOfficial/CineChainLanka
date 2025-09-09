import React from 'react';
import { 
  CurrencyDollarIcon,
  ArrowTrendingUpIcon,
  ClockIcon,
  CheckCircleIcon,
  FilmIcon,
  WalletIcon
} from '@heroicons/react/24/outline';

interface InvestorPortfolioProps {
  data: {
    total_invested: number;
    total_royalties_earned: number;
    total_royalties_claimable: number;
    total_royalties_claimed: number;
    roi_percentage: number;
    active_campaigns: number;
    completed_campaigns: number;
    total_nfts: number;
  };
  onClaimRoyalties?: () => void;
}

const InvestorPortfolio: React.FC<InvestorPortfolioProps> = ({ 
  data, 
  onClaimRoyalties 
}) => {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  const formatPercentage = (percentage: number) => {
    return `${percentage.toFixed(2)}%`;
  };

  const getROIColor = (roi: number) => {
    if (roi > 0) return 'text-green-600';
    if (roi < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const portfolioCards = [
    {
      title: 'Total Invested',
      value: formatCurrency(data.total_invested),
      icon: CurrencyDollarIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-600',
    },
    {
      title: 'Total Earned',
      value: formatCurrency(data.total_royalties_earned),
      icon: ArrowTrendingUpIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      iconColor: 'text-green-600',
    },
    {
      title: 'Claimable Now',
      value: formatCurrency(data.total_royalties_claimable),
      icon: ClockIcon,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      iconColor: 'text-orange-600',
    },
    {
      title: 'Already Claimed',
      value: formatCurrency(data.total_royalties_claimed),
      icon: CheckCircleIcon,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      iconColor: 'text-purple-600',
    },
    {
      title: 'Active Campaigns',
      value: data.active_campaigns.toString(),
      icon: FilmIcon,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
      iconColor: 'text-indigo-600',
    },
    {
      title: 'Total NFTs',
      value: data.total_nfts.toString(),
      icon: WalletIcon,
      color: 'text-pink-600',
      bgColor: 'bg-pink-50',
      iconColor: 'text-pink-600',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Portfolio Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {portfolioCards.map((card, index) => (
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

      {/* ROI and Performance */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p className="text-sm text-gray-600">Return on Investment (ROI)</p>
            <p className={`text-3xl font-bold ${getROIColor(data.roi_percentage)}`}>
              {formatPercentage(data.roi_percentage)}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              {data.roi_percentage > 0 ? 'Profitable' : data.roi_percentage < 0 ? 'Loss' : 'Break-even'}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Campaign Portfolio</p>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Active</span>
                <span className="text-sm font-medium text-gray-900">{data.active_campaigns}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Completed</span>
                <span className="text-sm font-medium text-gray-900">{data.completed_campaigns}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Total NFTs</span>
                <span className="text-sm font-medium text-gray-900">{data.total_nfts}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Claim Royalties Section */}
      {data.total_royalties_claimable > 0 && (
        <div className="bg-gradient-to-r from-orange-50 to-yellow-50 p-6 rounded-lg border border-orange-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-orange-900">Claimable Royalties Available</h3>
              <p className="text-orange-700 mt-1">
                You have {formatCurrency(data.total_royalties_claimable)} in royalties ready to claim
              </p>
            </div>
            <button
              onClick={onClaimRoyalties}
              className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              Claim Royalties
            </button>
          </div>
        </div>
      )}

      {/* Investment Breakdown */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Investment Breakdown</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Total Invested</span>
            <span className="text-sm font-medium text-gray-900">
              {formatCurrency(data.total_invested)}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Total Returns</span>
            <span className="text-sm font-medium text-gray-900">
              {formatCurrency(data.total_royalties_earned)}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Net Profit/Loss</span>
            <span className={`text-sm font-medium ${getROIColor(data.roi_percentage)}`}>
              {formatCurrency(data.total_royalties_earned - data.total_invested)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InvestorPortfolio;
