import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../store/hooks';
import { fetchUserProfile } from '../store/slices/userSlice';
import { deleteCampaign } from '../store/slices/campaignSlice';
import { 
  EyeIcon, 
  PencilIcon, 
  TrashIcon,
  PlusCircleIcon,
  CalendarIcon,
  CurrencyDollarIcon
} from '@heroicons/react/24/outline';

const CampaignManagement: React.FC = () => {
  const dispatch = useAppDispatch();
  const { campaigns, isLoading } = useAppSelector((state) => state.campaigns);
  const { user } = useAppSelector((state) => state.auth);
  const { profile } = useAppSelector((state) => state.user);
  
  const [deleteConfirmation, setDeleteConfirmation] = useState<{
    isOpen: boolean;
    campaignId: number | null;
    campaignTitle: string;
  }>({
    isOpen: false,
    campaignId: null,
    campaignTitle: ''
  });

  // Ensure user profile is loaded
  useEffect(() => {
    if (user && !profile) {
      dispatch(fetchUserProfile());
    }
  }, [dispatch, user, profile]);

  // Ensure campaigns array is always defined
  const campaignsArray = Array.isArray(campaigns) ? campaigns : [];
  
  // Use either profile or user for current user info
  const currentUser = profile || user;
  
  // Filter campaigns with null safety checks
  const userCampaigns = campaignsArray.filter(c => {
    if (!c.creator || !currentUser) return false;
    return c.creator.id === currentUser.id;
  });

  // Debug logging (can be removed in production)
  if (process.env.NODE_ENV === 'development') {
    console.log('CampaignManagement Debug:', {
      totalCampaigns: campaignsArray.length,
      currentUserId: currentUser?.id,
      userCampaigns: userCampaigns.length,
      hasAuthUser: !!user,
      hasProfile: !!profile
    });
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

  const handleDeleteClick = (campaign: any) => {
    setDeleteConfirmation({
      isOpen: true,
      campaignId: campaign.id,
      campaignTitle: campaign.title
    });
  };

  const handleDeleteConfirm = async () => {
    if (deleteConfirmation.campaignId) {
      try {
        await dispatch(deleteCampaign(deleteConfirmation.campaignId)).unwrap();
        setDeleteConfirmation({
          isOpen: false,
          campaignId: null,
          campaignTitle: ''
        });
      } catch (error) {
        // Error is handled by the slice
      }
    }
  };

  const handleDeleteCancel = () => {
    setDeleteConfirmation({
      isOpen: false,
      campaignId: null,
      campaignTitle: ''
    });
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
                        onClick={() => handleDeleteClick(campaign)}
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

      {/* Delete Confirmation Modal */}
      {deleteConfirmation.isOpen && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3 text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                <TrashIcon className="h-6 w-6 text-red-600" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mt-4">Delete Campaign</h3>
              <div className="mt-2 px-7 py-3">
                <p className="text-sm text-gray-500">
                  Are you sure you want to delete "{deleteConfirmation.campaignTitle}"? 
                  This action cannot be undone.
                </p>
              </div>
              <div className="flex items-center justify-center gap-3 mt-4">
                <button
                  onClick={handleDeleteCancel}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeleteConfirm}
                  disabled={isLoading}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isLoading ? 'Deleting...' : 'Delete'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CampaignManagement;
