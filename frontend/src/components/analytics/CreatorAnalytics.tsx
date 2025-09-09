import React, { useState, useEffect } from 'react';
import { useAppSelector } from '../../store/hooks';
import {
  ChartBarIcon,
  CurrencyDollarIcon,
  UsersIcon,
  ArrowTrendingUpIcon,
  EyeIcon,
  HeartIcon,
  ShareIcon
} from '@heroicons/react/24/outline';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

interface CampaignMetrics {
  id: number;
  title: string;
  totalRaised: number;
  totalRevenue: number;
  backerCount: number;
  viewCount: number;
  likeCount: number;
  shareCount: number;
  roi: number;
  status: string;
}

interface RevenueData {
  labels: string[];
  revenue: number[];
  creatorRoyalties: number[];
  investorRoyalties: number[];
  platformFees: number[];
}

interface SourceBreakdown {
  source: string;
  amount: number;
  percentage: number;
}

const CreatorAnalytics: React.FC = () => {
  const { user } = useAppSelector((state) => state.auth);
  const [campaigns, setCampaigns] = useState<CampaignMetrics[]>([]);
  const [revenueData, setRevenueData] = useState<RevenueData | null>(null);
  const [sourceBreakdown, setSourceBreakdown] = useState<SourceBreakdown[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('30');

  useEffect(() => {
    fetchAnalyticsData();
  }, [selectedPeriod]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      
      // Fetch creator analytics data
      const response = await fetch(`/api/analytics/creator/creator_analytics/?period=${selectedPeriod}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setCampaigns(data.campaigns || []);
        setRevenueData(data.revenueChart || null);
        setSourceBreakdown(data.sourceBreakdown || []);
      } else {
        console.error('Failed to fetch analytics data:', response.statusText);
      }
    } catch (error) {
      console.error('Error fetching analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  const totalRevenue = campaigns.reduce((sum, campaign) => sum + campaign.totalRevenue, 0);
  const totalRaised = campaigns.reduce((sum, campaign) => sum + campaign.totalRaised, 0);
  const totalBackers = campaigns.reduce((sum, campaign) => sum + campaign.backerCount, 0);
  const averageROI = campaigns.length > 0 
    ? campaigns.reduce((sum, campaign) => sum + campaign.roi, 0) / campaigns.length 
    : 0;

  const revenueChartData = revenueData ? {
    labels: revenueData.labels,
    datasets: [
      {
        label: 'Total Revenue',
        data: revenueData.revenue,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.1,
      },
      {
        label: 'Creator Royalties',
        data: revenueData.creatorRoyalties,
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.1,
      },
    ],
  } : null;

  const sourceChartData = sourceBreakdown.length > 0 ? {
    labels: sourceBreakdown.map(item => item.source),
    datasets: [
      {
        data: sourceBreakdown.map(item => item.amount),
        backgroundColor: [
          '#3B82F6',
          '#10B981',
          '#F59E0B',
          '#EF4444',
          '#8B5CF6',
          '#06B6D4',
        ],
        borderWidth: 2,
        borderColor: '#ffffff',
      },
    ],
  } : null;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Creator Analytics</h1>
        <select
          value={selectedPeriod}
          onChange={(e) => setSelectedPeriod(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
          <option value="90">Last 90 days</option>
          <option value="365">Last year</option>
        </select>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CurrencyDollarIcon className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Revenue</p>
              <p className="text-2xl font-semibold text-gray-900">
                ${totalRevenue.toLocaleString()}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ArrowTrendingUpIcon className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Average ROI</p>
              <p className="text-2xl font-semibold text-gray-900">
                {averageROI.toFixed(1)}%
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <UsersIcon className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Backers</p>
              <p className="text-2xl font-semibold text-gray-900">
                {totalBackers.toLocaleString()}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-8 w-8 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Active Campaigns</p>
              <p className="text-2xl font-semibold text-gray-900">
                {campaigns.filter(c => c.status === 'active').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Trend Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Revenue Trend</h3>
          {revenueChartData ? (
            <Line
              data={revenueChartData}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: 'top' as const,
                  },
                  title: {
                    display: false,
                  },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    ticks: {
                      callback: function(value) {
                        return '$' + value.toLocaleString();
                      },
                    },
                  },
                },
              }}
            />
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500">
              No revenue data available
            </div>
          )}
        </div>

        {/* Revenue Source Breakdown */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Revenue Sources</h3>
          {sourceChartData ? (
            <Doughnut
              data={sourceChartData}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: 'bottom' as const,
                  },
                },
              }}
            />
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-500">
              No source data available
            </div>
          )}
        </div>
      </div>

      {/* Campaign Performance Table */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Campaign Performance</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Campaign
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Raised
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Revenue
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ROI
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Backers
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Engagement
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {campaigns.map((campaign) => (
                <tr key={campaign.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {campaign.title}
                    </div>
                    <div className="text-sm text-gray-500">
                      Status: {campaign.status}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${campaign.totalRaised.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${campaign.totalRevenue.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      campaign.roi > 0 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {campaign.roi.toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {campaign.backerCount}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="flex space-x-4">
                      <div className="flex items-center">
                        <EyeIcon className="h-4 w-4 mr-1" />
                        {campaign.viewCount}
                      </div>
                      <div className="flex items-center">
                        <HeartIcon className="h-4 w-4 mr-1" />
                        {campaign.likeCount}
                      </div>
                      <div className="flex items-center">
                        <ShareIcon className="h-4 w-4 mr-1" />
                        {campaign.shareCount}
                      </div>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default CreatorAnalytics;