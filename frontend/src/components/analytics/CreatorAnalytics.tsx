import React, { useEffect, useState } from 'react';
import { useAppSelector } from '../../store/hooks';
import api from '../../utils/api';
import RevenueChart from './RevenueChart';
import RevenueSummary from './RevenueSummary';
import { 
  ChartBarIcon,
  CurrencyDollarIcon,
  UserGroupIcon,
  EyeIcon,
  HeartIcon,
  ShareIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

interface CampaignMetrics {
  campaign_id: number;
  title: string;
  status: string;
  total_funding: number;
  funding_goal: number;
  backer_count: number;
  view_count: number;
  like_count: number;
  share_count: number;
  created_at: string;
  end_date: string;
  funding_progress: number;
  days_remaining: number;
  avg_contribution: number;
  conversion_rate: number;
}

interface CreatorAnalyticsData {
  total_campaigns: number;
  active_campaigns: number;
  completed_campaigns: number;
  total_funding_raised: number;
  total_backers: number;
  avg_campaign_performance: number;
  top_performing_campaigns: CampaignMetrics[];
  recent_campaigns: CampaignMetrics[];
  funding_trends: {
    labels: string[];
    funding_data: number[];
    backer_data: number[];
  };
  revenue_forecast: {
    next_month: number;
    next_quarter: number;
    next_year: number;
  };
}

const CreatorAnalytics: React.FC = () => {
  const { user } = useAppSelector((state) => state.auth);
  const [analyticsData, setAnalyticsData] = useState<CreatorAnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState<'7d' | '30d' | '90d' | '1y'>('30d');

  useEffect(() => {
    fetchCreatorAnalytics();
  }, [selectedPeriod]);

  const fetchCreatorAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await api.get('/api/analytics/creator/creator_analytics/');
      setAnalyticsData(response.data);

    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active': return 'text-green-600 bg-green-100';
      case 'funded': return 'text-blue-600 bg-blue-100';
      case 'completed': return 'text-purple-600 bg-purple-100';
      case 'failed': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getPerformanceColor = (performance: number) => {
    if (performance >= 80) return 'text-green-600';
    if (performance >= 60) return 'text-yellow-600';
    return 'text-red-600';
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
                <h3 className="text-sm font-medium text-red-800">Error loading analytics</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
                <button
                  onClick={fetchCreatorAnalytics}
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

  if (!analyticsData) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No analytics data</h3>
            <p className="mt-1 text-sm text-gray-500">
              Analytics will appear here once you create campaigns.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Creator Analytics</h1>
              <p className="text-gray-600 mt-2">
                Track your campaign performance and revenue insights
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
                onClick={fetchCreatorAnalytics}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                Refresh
              </button>
            </div>
          </div>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className="p-3 rounded-lg bg-blue-50">
                <ChartBarIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Campaigns</p>
                <p className="text-2xl font-bold text-gray-900">{analyticsData.total_campaigns}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className="p-3 rounded-lg bg-green-50">
                <CurrencyDollarIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Funding</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatCurrency(analyticsData.total_funding_raised)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className="p-3 rounded-lg bg-yellow-50">
                <UserGroupIcon className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Backers</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatNumber(analyticsData.total_backers)}
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
                <p className="text-sm font-medium text-gray-600">Avg Performance</p>
                <p className={`text-2xl font-bold ${getPerformanceColor(analyticsData.avg_campaign_performance)}`}>
                  {analyticsData.avg_campaign_performance.toFixed(1)}%
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Campaign Status Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Campaigns</p>
                <p className="text-3xl font-bold text-green-600">{analyticsData.active_campaigns}</p>
              </div>
              <div className="p-3 rounded-lg bg-green-50">
                <ClockIcon className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Completed Campaigns</p>
                <p className="text-3xl font-bold text-blue-600">{analyticsData.completed_campaigns}</p>
              </div>
              <div className="p-3 rounded-lg bg-blue-50">
                <ChartBarIcon className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Success Rate</p>
                <p className="text-3xl font-bold text-purple-600">
                  {analyticsData.total_campaigns > 0 
                    ? ((analyticsData.completed_campaigns / analyticsData.total_campaigns) * 100).toFixed(1)
                    : 0}%
                </p>
              </div>
              <div className="p-3 rounded-lg bg-purple-50">
                <ArrowTrendingUpIcon className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Revenue Forecast */}
        <div className="bg-white p-6 rounded-lg shadow-sm border mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue Forecast</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">Next Month</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(analyticsData.revenue_forecast.next_month)}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600">Next Quarter</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(analyticsData.revenue_forecast.next_quarter)}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600">Next Year</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(analyticsData.revenue_forecast.next_year)}
              </p>
            </div>
          </div>
        </div>

        {/* Funding Trends Chart */}
        <div className="bg-white p-6 rounded-lg shadow-sm border mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Funding Trends</h3>
          <RevenueChart
            data={{
              labels: analyticsData.funding_trends.labels,
              revenue_data: analyticsData.funding_trends.funding_data,
              creator_royalties_data: analyticsData.funding_trends.funding_data,
              investor_royalties_data: [],
              platform_fees_data: []
            }}
            type="line"
            title="Funding Over Time"
            height={300}
          />
        </div>

        {/* Top Performing Campaigns */}
        <div className="bg-white p-6 rounded-lg shadow-sm border mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Performing Campaigns</h3>
          <div className="space-y-4">
            {analyticsData.top_performing_campaigns.map((campaign) => (
              <div key={campaign.campaign_id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <h4 className="text-sm font-medium text-gray-900">{campaign.title}</h4>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(campaign.status)}`}>
                      {campaign.status}
                    </span>
                  </div>
                  <div className="mt-2 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                    <div className="flex items-center">
                      <CurrencyDollarIcon className="h-4 w-4 mr-1" />
                      {formatCurrency(campaign.total_funding)}
                    </div>
                    <div className="flex items-center">
                      <UserGroupIcon className="h-4 w-4 mr-1" />
                      {campaign.backer_count} backers
                    </div>
                    <div className="flex items-center">
                      <EyeIcon className="h-4 w-4 mr-1" />
                      {formatNumber(campaign.view_count)} views
                    </div>
                    <div className="flex items-center">
                      <ArrowTrendingUpIcon className="h-4 w-4 mr-1" />
                      {campaign.conversion_rate.toFixed(1)}% conversion
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium text-gray-900">
                    {campaign.funding_progress.toFixed(1)}%
                  </div>
                  <div className="w-24 bg-gray-200 rounded-full h-2 mt-1">
                    <div 
                      className="bg-blue-600 h-2 rounded-full" 
                      style={{ width: `${Math.min(campaign.funding_progress, 100)}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Campaigns */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Campaigns</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Campaign
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Funding
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Backers
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Performance
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {analyticsData.recent_campaigns.map((campaign) => (
                  <tr key={campaign.campaign_id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{campaign.title}</div>
                        <div className="text-sm text-gray-500">
                          Created {new Date(campaign.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(campaign.status)}`}>
                        {campaign.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatCurrency(campaign.total_funding)} / {formatCurrency(campaign.funding_goal)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {campaign.backer_count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{ width: `${Math.min(campaign.funding_progress, 100)}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-900">
                          {campaign.funding_progress.toFixed(1)}%
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreatorAnalytics;
