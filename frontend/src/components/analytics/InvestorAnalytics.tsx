import React, { useState, useEffect } from 'react';
import { useAppSelector } from '../../store/hooks';
import {
  ChartBarIcon,
  CurrencyDollarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
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

interface PortfolioData {
  total_invested: number;
  total_earned: number;
  claimable_royalties: number;
  claimed_royalties: number;
  overall_roi: number;
  investment_count: number;
  investments: Investment[];
  royalty_trends: {
  labels: string[];
    royalty_data: number[];
    cumulative_data: number[];
  };
  monthly_earnings: Array<{
    month: string;
    earnings: number;
    investments: number;
  }>;
  campaign_performance: Array<{
    campaign_id: number;
  title: string;
    roi_percentage: number;
    total_earned: number;
  status: string;
  }>;
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

const InvestorAnalytics: React.FC = () => {
  const { user } = useAppSelector((state) => state.auth);
  const [portfolioData, setPortfolioData] = useState<PortfolioData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('30');

  useEffect(() => {
    fetchPortfolioData();
  }, [selectedPeriod]);

  const fetchPortfolioData = async () => {
    try {
      setLoading(true);
      
      // Fetch investor portfolio data
      const response = await fetch(`/api/analytics/investor/portfolio/?period=${selectedPeriod}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setPortfolioData(data);
      } else {
        console.error('Failed to fetch portfolio data:', response.statusText);
      }
    } catch (error) {
      console.error('Error fetching portfolio data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClaimRoyalty = async (royaltyId: number) => {
    try {
      const response = await fetch(`/api/revenue/royalties/${royaltyId}/claim/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (response.ok) {
        alert('Royalty claimed successfully!');
        fetchPortfolioData(); // Refresh data
      } else {
        alert('Failed to claim royalty');
      }
    } catch (error) {
      console.error('Error claiming royalty:', error);
      alert('Error claiming royalty');
    }
  };

  const royaltyChartData = portfolioData?.royalty_trends ? {
    labels: portfolioData.royalty_trends.labels,
    datasets: [
      {
        label: 'Daily Royalties',
        data: portfolioData.royalty_trends.royalty_data,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.1,
      },
      {
        label: 'Cumulative Royalties',
        data: portfolioData.royalty_trends.cumulative_data,
        borderColor: 'rgb(16, 185, 129)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        tension: 0.1,
      },
    ],
  } : null;

  const monthlyEarningsData = portfolioData?.monthly_earnings ? {
    labels: portfolioData.monthly_earnings.map(item => item.month),
    datasets: [
      {
        label: 'Monthly Earnings',
        data: portfolioData.monthly_earnings.map(item => item.earnings),
        backgroundColor: 'rgba(99, 102, 241, 0.8)',
        borderColor: 'rgb(99, 102, 241)',
        borderWidth: 1,
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

  if (!portfolioData) {
    return (
      <div className="text-center py-12">
        <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">No portfolio data</h3>
        <p className="mt-1 text-sm text-gray-500">
          Start investing in campaigns to see your portfolio analytics.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Investor Portfolio</h1>
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
              <CurrencyDollarIcon className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Invested</p>
              <p className="text-2xl font-semibold text-gray-900">
                ${portfolioData.total_invested.toLocaleString()}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ArrowTrendingUpIcon className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Earned</p>
              <p className="text-2xl font-semibold text-gray-900">
                ${portfolioData.total_earned.toLocaleString()}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Overall ROI</p>
              <p className="text-2xl font-semibold text-gray-900">
                {portfolioData.overall_roi.toFixed(1)}%
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CurrencyDollarIcon className="h-8 w-8 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Claimable</p>
              <p className="text-2xl font-semibold text-gray-900">
                ${portfolioData.claimable_royalties.toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Royalty Trends Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Royalty Trends</h3>
          {royaltyChartData ? (
            <Line
              data={royaltyChartData}
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
              No royalty data available
            </div>
          )}
        </div>

        {/* Monthly Earnings Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Monthly Earnings</h3>
          {monthlyEarningsData ? (
            <Bar
              data={monthlyEarningsData}
              options={{
                responsive: true,
                plugins: {
                  legend: {
                    position: 'top' as const,
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
              No earnings data available
            </div>
          )}
        </div>
      </div>

      {/* Investment Portfolio Table */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Investment Portfolio</h3>
        </div>
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
                  Invested
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Earned
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ROI
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
              {portfolioData.investments.map((investment) => (
                <tr key={`${investment.campaign_id}-${investment.nft_id}`}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {investment.campaign_title}
                    </div>
                    <div className="text-sm text-gray-500">
                      {new Date(investment.investment_date).toLocaleDateString()}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    #{investment.nft_id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${investment.contribution_amount.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${investment.royalty_earned.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      investment.royalty_earned > investment.contribution_amount 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {((investment.royalty_earned / investment.contribution_amount) * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      investment.status === 'claimable' 
                        ? 'bg-green-100 text-green-800'
                        : investment.status === 'claimed'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {investment.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    {investment.status === 'claimable' && investment.royalty_claimable > 0 && (
                      <button
                        onClick={() => handleClaimRoyalty(investment.campaign_id)}
                        className="text-primary-600 hover:text-primary-900"
                      >
                        Claim ${investment.royalty_claimable.toLocaleString()}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Performance Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Best Performing Campaign</h3>
          <div className="flex items-center">
            <ArrowTrendingUpIcon className="h-8 w-8 text-green-600 mr-4" />
            <div>
              <p className="text-sm font-medium text-gray-900">
                {portfolioData.best_performing_campaign.title}
              </p>
              <p className="text-2xl font-semibold text-green-600">
                {portfolioData.best_performing_campaign.roi_percentage.toFixed(1)}% ROI
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Worst Performing Campaign</h3>
          <div className="flex items-center">
            <ArrowTrendingDownIcon className="h-8 w-8 text-red-600 mr-4" />
            <div>
              <p className="text-sm font-medium text-gray-900">
                {portfolioData.worst_performing_campaign.title}
              </p>
              <p className="text-2xl font-semibold text-red-600">
                {portfolioData.worst_performing_campaign.roi_percentage.toFixed(1)}% ROI
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InvestorAnalytics;