import React, { useEffect, useState } from 'react';
import { useAppSelector } from '../../store/hooks';
import api from '../../utils/api';
import RevenueChart from './RevenueChart';
import { 
  ChartBarIcon,
  CurrencyDollarIcon,
  UserGroupIcon,
  BanknotesIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  EyeIcon
} from '@heroicons/react/24/outline';

interface Investment {
  campaign_id: number;
  campaign_title: string;
  nft_id: number;
  contribution_amount: number;
  share_percentage: number;
  royalty_earned: number;
  royalty_claimable: number;
  royalty_claimed: number;
  status: string;
  investment_date: string;
  last_royalty_date?: string;
}

interface PortfolioSummary {
  total_invested: number;
  total_royalties_earned: number;
  total_royalties_claimable: number;
  total_royalties_claimed: number;
  roi_percentage: number;
  active_investments: number;
  completed_investments: number;
  total_nfts: number;
  avg_roi_per_campaign: number;
  best_performing_campaign: {
    campaign_id: number;
    title: string;
    roi_percentage: number;
  };
  worst_performing_campaign: {
    campaign_id: number;
    title: string;
    roi_percentage: number;
  };
}

interface InvestorDashboardData {
  portfolio_summary: PortfolioSummary;
  investments: Investment[];
  royalty_trends: {
    labels: string[];
    royalty_data: number[];
    cumulative_data: number[];
  };
  monthly_earnings: {
    month: string;
    earnings: number;
    investments: number;
  }[];
  campaign_performance: {
    campaign_id: number;
    title: string;
    roi_percentage: number;
    total_earned: number;
    status: string;
  }[];
}

const InvestorDashboard: React.FC = () => {
  const { user } = useAppSelector((state) => state.auth);
  const [dashboardData, setDashboardData] = useState<InvestorDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState<'7d' | '30d' | '90d' | '1y'>('30d');
  const [claimingRoyalty, setClaimingRoyalty] = useState<number | null>(null);

  useEffect(() => {
    fetchInvestorDashboard();
  }, [selectedPeriod]);

  const fetchInvestorDashboard = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await api.get('/api/analytics/investor/portfolio/');
      setDashboardData(response.data);

    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const claimRoyalty = async (investmentId: number) => {
    try {
      setClaimingRoyalty(investmentId);
      
      await api.post(`/api/revenue/royalties/${investmentId}/claim/`);

      // Refresh data after successful claim
      await fetchInvestorDashboard();
      
    } catch (err) {
      console.error('Error claiming royalty:', err);
      // You might want to show a toast notification here
    } finally {
      setClaimingRoyalty(null);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  const getROIColor = (roi: number) => {
    if (roi > 0) return 'text-green-600';
    if (roi < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active': return 'text-green-600 bg-green-100';
      case 'completed': return 'text-blue-600 bg-blue-100';
      case 'claimable': return 'text-yellow-600 bg-yellow-100';
      case 'claimed': return 'text-purple-600 bg-purple-100';
      case 'expired': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="h-32 bg-gray-200 rounded"></div>
              ))}
            </div>
            <div className="h-96 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-5 w-5 text-red-400" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error loading dashboard</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
                <button
                  onClick={fetchInvestorDashboard}
                  className="mt-2 text-sm text-red-600 hover:text-red-500 underline"
                >
                  Try again
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No investment data</h3>
            <p className="mt-1 text-sm text-gray-500">
              Your investment portfolio will appear here once you start investing in campaigns.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const { portfolio_summary, investments, royalty_trends, monthly_earnings, campaign_performance } = dashboardData;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Investment Portfolio</h1>
              <p className="text-gray-600 mt-2">
                Track your investments, royalties, and portfolio performance
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <select
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value as any)}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
                <option value="90d">Last 90 days</option>
                <option value="1y">Last year</option>
              </select>
              <button
                onClick={fetchInvestorDashboard}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                Refresh
              </button>
            </div>
          </div>
        </div>

        {/* Portfolio Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className="p-3 rounded-lg bg-blue-50">
                <CurrencyDollarIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Invested</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatCurrency(portfolio_summary.total_invested)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className="p-3 rounded-lg bg-green-50">
                <BanknotesIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Earned</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatCurrency(portfolio_summary.total_royalties_earned)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className="p-3 rounded-lg bg-yellow-50">
                <ClockIcon className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Claimable</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatCurrency(portfolio_summary.total_royalties_claimable)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className="p-3 rounded-lg bg-purple-50">
                <ArrowTrendingUpIcon className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">ROI</p>
                <p className={`text-2xl font-bold ${getROIColor(portfolio_summary.roi_percentage)}`}>
                  {portfolio_summary.roi_percentage.toFixed(2)}%
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Investment Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Investments</p>
                <p className="text-3xl font-bold text-green-600">{portfolio_summary.active_investments}</p>
              </div>
              <div className="p-3 rounded-lg bg-green-50">
                <ClockIcon className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Completed</p>
                <p className="text-3xl font-bold text-blue-600">{portfolio_summary.completed_investments}</p>
              </div>
              <div className="p-3 rounded-lg bg-blue-50">
                <CheckCircleIcon className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total NFTs</p>
                <p className="text-3xl font-bold text-purple-600">{portfolio_summary.total_nfts}</p>
              </div>
              <div className="p-3 rounded-lg bg-purple-50">
                <UserGroupIcon className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Performance Highlights */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Best Performing Campaign</h3>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">{portfolio_summary.best_performing_campaign.title}</p>
                <p className="text-sm text-gray-500">Campaign #{portfolio_summary.best_performing_campaign.campaign_id}</p>
              </div>
              <div className="text-right">
                <p className={`text-2xl font-bold ${getROIColor(portfolio_summary.best_performing_campaign.roi_percentage)}`}>
                  +{portfolio_summary.best_performing_campaign.roi_percentage.toFixed(1)}%
                </p>
                <p className="text-sm text-gray-500">ROI</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Worst Performing Campaign</h3>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">{portfolio_summary.worst_performing_campaign.title}</p>
                <p className="text-sm text-gray-500">Campaign #{portfolio_summary.worst_performing_campaign.campaign_id}</p>
              </div>
              <div className="text-right">
                <p className={`text-2xl font-bold ${getROIColor(portfolio_summary.worst_performing_campaign.roi_percentage)}`}>
                  {portfolio_summary.worst_performing_campaign.roi_percentage.toFixed(1)}%
                </p>
                <p className="text-sm text-gray-500">ROI</p>
              </div>
            </div>
          </div>
        </div>

        {/* Royalty Trends Chart */}
        <div className="bg-white p-6 rounded-lg shadow-sm border mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Royalty Earnings Trend</h3>
          <RevenueChart
            data={{
              labels: royalty_trends.labels,
              revenue_data: royalty_trends.royalty_data,
              creator_royalties_data: royalty_trends.cumulative_data,
              investor_royalties_data: royalty_trends.royalty_data,
              platform_fees_data: []
            }}
            type="line"
            title="Royalty Earnings Over Time"
            height={300}
          />
        </div>

        {/* Monthly Earnings */}
        <div className="bg-white p-6 rounded-lg shadow-sm border mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Monthly Earnings</h3>
          <div className="space-y-4">
            {monthly_earnings.map((month, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-gray-900">{month.month}</p>
                  <p className="text-sm text-gray-500">
                    {formatNumber(month.investments)} investments
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-gray-900">
                    {formatCurrency(month.earnings)}
                  </p>
                  <p className="text-sm text-gray-500">earned</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Investment Portfolio Table */}
        <div className="bg-white p-6 rounded-lg shadow-sm border mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Investment Portfolio</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Campaign
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    NFT ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Investment
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Share %
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Earned
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Claimable
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {investments.map((investment) => (
                  <tr key={`${investment.campaign_id}-${investment.nft_id}`}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{investment.campaign_title}</div>
                        <div className="text-sm text-gray-500">
                          Invested {new Date(investment.investment_date).toLocaleDateString()}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      #{investment.nft_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(investment.contribution_amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {investment.share_percentage.toFixed(2)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(investment.royalty_earned)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(investment.royalty_claimable)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(investment.status)}`}>
                        {investment.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {investment.royalty_claimable > 0 && investment.status === 'claimable' && (
                        <button
                          onClick={() => claimRoyalty(investment.nft_id)}
                          disabled={claimingRoyalty === investment.nft_id}
                          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-3 py-1 rounded text-xs font-medium transition-colors"
                        >
                          {claimingRoyalty === investment.nft_id ? 'Claiming...' : 'Claim'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Campaign Performance */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Campaign Performance</h3>
          <div className="space-y-4">
            {campaign_performance.map((campaign) => (
              <div key={campaign.campaign_id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <h4 className="text-sm font-medium text-gray-900">{campaign.title}</h4>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(campaign.status)}`}>
                      {campaign.status}
                    </span>
                  </div>
                  <div className="mt-2 text-sm text-gray-500">
                    Campaign #{campaign.campaign_id}
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-lg font-bold ${getROIColor(campaign.roi_percentage)}`}>
                    {campaign.roi_percentage.toFixed(1)}% ROI
                  </div>
                  <div className="text-sm text-gray-500">
                    {formatCurrency(campaign.total_earned)} earned
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default InvestorDashboard;
