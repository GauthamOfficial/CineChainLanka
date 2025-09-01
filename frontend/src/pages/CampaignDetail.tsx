import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { fetchCampaignById, clearError } from '../store/slices/campaignSlice';
import { 
  ArrowLeftIcon,
  HeartIcon,
  ShareIcon,
  UserIcon,
  CalendarIcon,
  CurrencyDollarIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

const CampaignDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { currentCampaign, isLoading, error } = useAppSelector((state) => state.campaigns);
  const { user } = useAppSelector((state) => state.auth);

  const [selectedReward, setSelectedReward] = useState<number | null>(null);
  const [contributionAmount, setContributionAmount] = useState('');
  const [showContributionModal, setShowContributionModal] = useState(false);

  useEffect(() => {
    if (id) {
      dispatch(fetchCampaignById(parseInt(id)));
    }
    return () => {
      dispatch(clearError());
    };
  }, [dispatch, id]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading campaign...</p>
        </div>
      </div>
    );
  }

  if (error || !currentCampaign) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Campaign Not Found</h2>
          <p className="text-gray-600 mb-4">{error || 'The campaign you are looking for does not exist.'}</p>
          <button
            onClick={() => navigate('/campaigns')}
            className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
          >
            Back to Campaigns
          </button>
        </div>
      </div>
    );
  }

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

  const getDaysLeft = (endDate: string) => {
    const endDateObj = new Date(endDate);
    const today = new Date();
    const diffTime = endDateObj.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 0 ? diffDays : 0;
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
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const handleContribute = () => {
    if (!user) {
      navigate('/login');
      return;
    }
    setShowContributionModal(true);
  };

  const handleContributionSubmit = () => {
    // TODO: Implement contribution logic
    console.log('Contributing:', { amount: contributionAmount, reward: selectedReward });
    setShowContributionModal(false);
    setContributionAmount('');
    setSelectedReward(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Back Button */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <button
            onClick={() => navigate('/campaigns')}
            className="flex items-center py-4 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeftIcon className="h-5 w-5 mr-2" />
            Back to Campaigns
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Campaign Header */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="relative">
                <img
                  src={currentCampaign.cover_image || '/placeholder-campaign.jpg'}
                  alt={currentCampaign.title}
                  className="w-full h-64 object-cover"
                />
                <div className="absolute top-4 left-4">
                  <span className={`px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(currentCampaign.status)}`}>
                    {currentCampaign.status.charAt(0).toUpperCase() + currentCampaign.status.slice(1)}
                  </span>
                </div>
                <div className="absolute top-4 right-4 flex space-x-2">
                  <button className="p-2 bg-white rounded-full shadow hover:bg-gray-50">
                    <HeartIcon className="h-5 w-5 text-gray-400" />
                  </button>
                  <button className="p-2 bg-white rounded-full shadow hover:bg-gray-50">
                    <ShareIcon className="h-5 w-5 text-gray-400" />
                  </button>
                </div>
              </div>

              <div className="p-6">
                <div className="flex items-center mb-4">
                  <span className="text-sm text-gray-500 mr-4">
                    {currentCampaign.category.icon} {currentCampaign.category.name}
                  </span>
                  <div className="flex items-center text-sm text-gray-500">
                    <UserIcon className="h-4 w-4 mr-1" />
                    by {currentCampaign.creator.first_name} {currentCampaign.creator.last_name}
                    {currentCampaign.creator.creator_verified && (
                      <span className="ml-2 text-blue-600 text-xs">✓ Verified</span>
                    )}
                  </div>
                </div>

                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                  {currentCampaign.title}
                </h1>

                {currentCampaign.subtitle && (
                  <p className="text-xl text-gray-600 mb-6">
                    {currentCampaign.subtitle}
                  </p>
                )}

                <p className="text-gray-700 leading-relaxed">
                  {currentCampaign.description}
                </p>
              </div>
            </div>

            {/* Campaign Updates */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Campaign Updates</h2>
              <div className="text-center py-8 text-gray-500">
                <p>No updates yet. Check back soon!</p>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Funding Progress */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="mb-4">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">
                    {formatCurrency(currentCampaign.current_funding)} raised
                  </span>
                  <span className="text-gray-600">
                    {Math.round(calculateProgress(currentCampaign.current_funding, currentCampaign.funding_goal))}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-primary-600 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${calculateProgress(currentCampaign.current_funding, currentCampaign.funding_goal)}%` }}
                  ></div>
                </div>
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Goal: {formatCurrency(currentCampaign.funding_goal)}</span>
                                           <span>{getDaysLeft(currentCampaign.end_date)} days left</span>
                </div>
              </div>

              {currentCampaign.status === 'active' && (
                <button
                  onClick={handleContribute}
                  className="w-full bg-primary-600 text-white py-3 px-4 rounded-md hover:bg-primary-700 transition-colors font-medium"
                >
                  Support This Project
                </button>
              )}

              {currentCampaign.status === 'funded' && (
                <div className="text-center py-2">
                  <CheckCircleIcon className="h-8 w-8 text-green-600 mx-auto mb-2" />
                  <p className="text-green-600 font-medium">Campaign Funded!</p>
                </div>
              )}

              {currentCampaign.status === 'failed' && (
                <div className="text-center py-2">
                  <ExclamationTriangleIcon className="h-8 w-8 text-red-600 mx-auto mb-2" />
                  <p className="text-red-600 font-medium">Campaign Failed</p>
                </div>
              )}
            </div>

            {/* Campaign Stats */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Campaign Stats</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Funding Goal</span>
                  <span className="font-medium">{formatCurrency(currentCampaign.funding_goal)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Current Funding</span>
                  <span className="font-medium">{formatCurrency(currentCampaign.current_funding)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Days Left</span>
                                     <span className="font-medium">{getDaysLeft(currentCampaign.end_date)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Created</span>
                  <span className="font-medium">
                    {new Date(currentCampaign.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>

            {/* Creator Info */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">About the Creator</h3>
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center mr-3">
                  <UserIcon className="h-6 w-6 text-gray-400" />
                </div>
                <div>
                  <p className="font-medium">
                    {currentCampaign.creator.first_name} {currentCampaign.creator.last_name}
                  </p>
                  <p className="text-sm text-gray-600">@{currentCampaign.creator.username}</p>
                </div>
              </div>
              {currentCampaign.creator.creator_verified && (
                <div className="flex items-center text-sm text-blue-600 mb-4">
                  <CheckCircleIcon className="h-4 w-4 mr-1" />
                  Verified Creator
                </div>
              )}
              <button className="w-full border border-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-50 transition-colors">
                View Creator Profile
              </button>
            </div>
          </div>
        </div>

        {/* Rewards Section */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Rewards</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {currentCampaign.rewards?.map((reward, index) => (
              <div key={index} className="bg-white rounded-lg shadow p-6 border-2 border-gray-200 hover:border-primary-300 transition-colors">
                <div className="mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{reward.title}</h3>
                  <p className="text-2xl font-bold text-primary-600 mb-2">
                    {formatCurrency(reward.amount)}
                  </p>
                  <p className="text-sm text-gray-600 mb-4">{reward.description}</p>
                </div>

                {reward.max_backers && reward.max_backers > 0 && (
                  <div className="mb-4">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Available</span>
                      <span className="text-gray-600">{reward.max_backers - reward.current_backers} left</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-600 h-2 rounded-full"
                        style={{ width: `${((reward.max_backers - reward.current_backers) / reward.max_backers) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                )}

                {currentCampaign.status === 'active' && (
                  <button
                    onClick={() => {
                      setSelectedReward(index);
                      setContributionAmount(reward.amount.toString());
                      setShowContributionModal(true);
                    }}
                    className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 transition-colors"
                  >
                    Select Reward
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Contribution Modal */}
      {showContributionModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Support This Campaign</h3>
            
            {selectedReward !== null && currentCampaign.rewards?.[selectedReward] && (
              <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900">{currentCampaign.rewards[selectedReward].title}</h4>
                <p className="text-sm text-gray-600">{currentCampaign.rewards[selectedReward].description}</p>
                <p className="text-lg font-bold text-primary-600 mt-2">
                  {formatCurrency(currentCampaign.rewards[selectedReward].amount)}
                </p>
              </div>
            )}

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Contribution Amount (LKR)
              </label>
              <input
                type="number"
                value={contributionAmount}
                onChange={(e) => setContributionAmount(e.target.value)}
                min={selectedReward !== null ? currentCampaign.rewards?.[selectedReward]?.amount : 1}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                placeholder="Enter amount"
              />
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => setShowContributionModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleContributionSubmit}
                className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
              >
                Continue to Payment
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CampaignDetail;

