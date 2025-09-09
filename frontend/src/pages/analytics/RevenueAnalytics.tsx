import React, { useEffect, useState } from 'react';
import { useAppSelector } from '../../store/hooks';
import api from '../../utils/api';
import RevenueSummary from '../../components/analytics/RevenueSummary';
import RevenueChart from '../../components/analytics/RevenueChart';
import { 
  ChartBarIcon,
  CurrencyDollarIcon,
  ArrowTrendingUpIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

interface RevenueData {
  total_revenue: number;
  total_creator_royalties: number;
  total_platform_fees: number;
  total_investor_royalties: number;
  total_distributions: number;
  pending_royalties: number;
  last_distribution_date?: string;
}

interface ChartData {
  labels: string[];
  revenue_data: number[];
  creator_royalties_data: number[];
  investor_royalties_data: number[];
  platform_fees_data: number[];
}

const RevenueAnalytics: React.FC = () => {
  const { user } = useAppSelector((state) => state.auth);
  const [revenueData, setRevenueData] = useState<RevenueData | null>(null);
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState<'7d' | '30d' | '90d' | '1y'>('30d');

  useEffect(() => {
    fetchRevenueData();
  }, [selectedPeriod]);

  const fetchRevenueData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch revenue summary
      const summaryResponse = await api.get('/api/revenue/analytics/summary/');
      setRevenueData(summaryResponse.data);

      // Fetch chart data
      const chartResponse = await api.get(`/api/revenue/analytics/chart_data/?days=${getDaysFromPeriod(selectedPeriod)}`);
      setChartData(chartResponse.data);

    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getDaysFromPeriod = (period: string): number => {
    switch (period) {
      case '7d': return 7;
      case '30d': return 30;
      case '90d': return 90;
      case '1y': return 365;
      default: return 30;
    }
  };

  const periodOptions = [
    { value: '7d', label: 'Last 7 days' },
    { value: '30d', label: 'Last 30 days' },
    { value: '90d', label: 'Last 90 days' },
    { value: '1y', label: 'Last year' },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {[...Array(6)].map((_, i) => (
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
                <ArrowTrendingUpIcon className="h-5 w-5 text-red-400" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error loading analytics</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
                <button
                  onClick={fetchRevenueData}
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

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Revenue Analytics</h1>
              <p className="text-gray-600 mt-2">
                Track your campaign revenue and royalty distributions
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <select
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value as any)}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {periodOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <button
                onClick={fetchRevenueData}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                Refresh
              </button>
            </div>
          </div>
        </div>

        {/* Revenue Summary */}
        {revenueData && (
          <div className="mb-8">
            <RevenueSummary data={revenueData} />
          </div>
        )}

        {/* Charts */}
        {chartData && (
          <div className="space-y-8">
            <RevenueChart
              data={chartData}
              type="line"
              title="Revenue Trends"
              height={400}
            />
            <RevenueChart
              data={chartData}
              type="bar"
              title="Revenue Breakdown"
              height={400}
            />
          </div>
        )}

        {/* Empty State */}
        {!revenueData && !chartData && (
          <div className="text-center py-12">
            <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No revenue data</h3>
            <p className="mt-1 text-sm text-gray-500">
              Revenue analytics will appear here once you have campaign revenue.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default RevenueAnalytics;
