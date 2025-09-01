import React from 'react';
import { Link } from 'react-router-dom';
import { useAppSelector } from '../store/hooks';
import { 
  EyeIcon, 
  PencilIcon, 
  TrashIcon,
  PlusCircleIcon,
  CalendarIcon,
  CurrencyDollarIcon
} from '@heroicons/react/24/outline';

const CampaignManagement: React.FC = () => {
  const { campaigns } = useAppSelector((state) => state.campaigns);
  const { user } = useAppSelector((state) => state.auth);

  // Ensure campaigns array is always defined
  const campaignsArray = Array.isArray(campaigns) ? campaigns : [];
  const userCampaigns = campaignsArray.filter(c => c.creator.id === user?.id);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-LK', {
      style: 'currency',
      currency: 'LKR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const calculateProgress = (current: number, goal: number) => {
    return Math.min((current / goal) * 100, 100);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'funded':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-purple-100 text-purple-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'draft':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getDaysLeft = (endDate: string) => {
    const endDateObj = new Date(endDate);
    const today = new Date();
    const diffTime = endDateObj.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 0 ? diffDays : 0;
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
        <h2 className="text-lg font-medium text-gray-900">My Campaigns</h2>
        <Link
          to="/create-campaign"
          className="inline-flex items-center px-3 py-2 bg-primary-600 text-white text-sm rounded-md hover:bg-primary-700 transition-colors"
        >
          <PlusCircleIcon className="h-4 w-4 mr-1" />
          Create New
        </Link>
      </div>

      <div className="p-6">
        {userCampaigns.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-gray-400 text-4xl mb-4">🎬</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No campaigns yet</h3>
            <p className="text-gray-600 mb-4">
              Start your creative journey by creating your first campaign
            </p>
            <Link
              to="/create-campaign"
              className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
            >
              <PlusCircleIcon className="h-4 w-4 mr-2" />
              Create Your First Campaign
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {userCampaigns.map((campaign) => (
              <div key={campaign.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 mr-3">
                        {campaign.title}
                      </h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(campaign.status)}`}>
                        {campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1)}
                      </span>
                    </div>

                    {campaign.subtitle && (
                      <p className="text-gray-600 mb-3">{campaign.subtitle}</p>
                    )}

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div className="flex items-center text-sm text-gray-600">
                        <CurrencyDollarIcon className="h-4 w-4 mr-2" />
                        <span>
                          {formatCurrency(campaign.current_funding)} / {formatCurrency(campaign.funding_goal)}
                        </span>
                      </div>
                      <div className="flex items-center text-sm text-gray-600">
                        <CalendarIcon className="h-4 w-4 mr-2" />
                                                 <span>{getDaysLeft(campaign.end_date)} days left</span>
                      </div>
                      <div className="text-sm text-gray-600">
                        <span>{Math.round(calculateProgress(campaign.current_funding, campaign.funding_goal))}% funded</span>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
                      <div
                        className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${calculateProgress(campaign.current_funding, campaign.funding_goal)}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 ml-4">
                    <Link
                      to={`/campaigns/${campaign.id}`}
                      className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                      title="View Campaign"
                    >
                      <EyeIcon className="h-5 w-5" />
                    </Link>
                    {campaign.status === 'draft' && (
                      <Link
                        to={`/campaigns/${campaign.id}/edit`}
                        className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                        title="Edit Campaign"
                      >
                        <PencilIcon className="h-5 w-5" />
                      </Link>
                    )}
                    {campaign.status === 'draft' && (
                      <button
                        className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                        title="Delete Campaign"
                      >
                        <TrashIcon className="h-5 w-5" />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default CampaignManagement;
