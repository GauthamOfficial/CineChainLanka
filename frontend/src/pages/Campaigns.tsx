import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { fetchCampaigns, setFilters, clearFilters } from '../store/slices/campaignSlice';
import { 
  MagnifyingGlassIcon, 
  FunnelIcon,
  EyeIcon,
  HeartIcon,
  CurrencyDollarIcon,
  CalendarIcon,
  UserIcon,
  PlusCircleIcon
} from '@heroicons/react/24/outline';

const Campaigns: React.FC = () => {
  const dispatch = useAppDispatch();
  const { campaigns, isLoading, error, filters, pagination } = useAppSelector((state) => state.campaigns);
  
  const [searchTerm, setSearchTerm] = useState(filters.search);
  const [showFilters, setShowFilters] = useState(false);

  // Ensure campaigns is always an array
  const safeCampaigns = Array.isArray(campaigns) ? campaigns : [];

  const categories = [
    { id: 1, name: 'Film', icon: '🎬' },
    { id: 2, name: 'Documentary', icon: '📹' },
    { id: 3, name: 'Web Series', icon: '📺' },
    { id: 4, name: 'Short Film', icon: '🎥' },
    { id: 5, name: 'Animation', icon: '🎨' },
    { id: 6, name: 'Music Video', icon: '🎵' },
  ];

  const statusOptions = [
    { value: 'active', label: 'Active', color: 'text-green-600' },
    { value: 'funded', label: 'Funded', color: 'text-blue-600' },
    { value: 'completed', label: 'Completed', color: 'text-purple-600' },
  ];

  useEffect(() => {
    dispatch(fetchCampaigns({ page: 1 }));
  }, [dispatch]);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (searchTerm !== filters.search) {
        dispatch(setFilters({ search: searchTerm }));
        dispatch(fetchCampaigns({ page: 1, search: searchTerm }));
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [searchTerm, dispatch, filters.search]);

  const handleFilterChange = (filterType: string, value: string) => {
    dispatch(setFilters({ [filterType]: value }));
    dispatch(fetchCampaigns({ page: 1, [filterType]: value }));
  };

  const handleClearFilters = () => {
    dispatch(clearFilters());
    setSearchTerm('');
    dispatch(fetchCampaigns({ page: 1 }));
  };

  const handlePageChange = (page: number) => {
    dispatch(fetchCampaigns({ page }));
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

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Campaigns</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => dispatch(fetchCampaigns({ page: 1 }))}
            className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Discover Campaigns</h1>
            <p className="text-gray-600 mt-2">
              Support creative projects and be part of amazing stories
            </p>
          </div>
          <div className="mt-4 sm:mt-0">
            <Link
              to="/create-campaign"
              className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
            >
              <PlusCircleIcon className="h-5 w-5 mr-2" />
              Create Campaign
            </Link>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
            {/* Search */}
            <div className="flex-1 max-w-md">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search campaigns..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>

            {/* Filter Toggle */}
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                <FunnelIcon className="h-5 w-5 mr-2" />
                Filters
              </button>
              
              {(filters.category || filters.status) && (
                <button
                  onClick={handleClearFilters}
                  className="text-sm text-primary-600 hover:text-primary-700"
                >
                  Clear Filters
                </button>
              )}
            </div>
          </div>

          {/* Filter Options */}
          {showFilters && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Category Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Category
                  </label>
                  <select
                    value={filters.category}
                    onChange={(e) => handleFilterChange('category', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="">All Categories</option>
                    {categories.map((category) => (
                      <option key={category.id} value={category.id}>
                        {category.icon} {category.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Status Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Status
                  </label>
                  <select
                    value={filters.status}
                    onChange={(e) => handleFilterChange('status', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="">All Status</option>
                    {statusOptions.map((status) => (
                      <option key={status.value} value={status.value}>
                        {status.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Campaigns Grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, index) => (
              <div key={index} className="bg-white rounded-lg shadow animate-pulse">
                <div className="h-48 bg-gray-200 rounded-t-lg"></div>
                <div className="p-6">
                  <div className="h-4 bg-gray-200 rounded mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded mb-4"></div>
                  <div className="h-2 bg-gray-200 rounded mb-2"></div>
                  <div className="h-2 bg-gray-200 rounded w-3/4"></div>
                </div>
              </div>
            ))}
          </div>
        ) : safeCampaigns.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 text-6xl mb-4">🔍</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No campaigns found</h3>
            <p className="text-gray-600">
              Try adjusting your search or filters to find what you're looking for.
            </p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {safeCampaigns.map((campaign) => (
                <div key={campaign.id} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow">
                  {/* Campaign Image */}
                  <div className="relative">
                    <img
                      src={campaign.cover_image || '/placeholder-campaign.jpg'}
                      alt={campaign.title}
                      className="w-full h-48 object-cover rounded-t-lg"
                    />
                    <div className="absolute top-3 left-3">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(campaign.status)}`}>
                        {campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1)}
                      </span>
                    </div>
                    <div className="absolute top-3 right-3">
                      <button className="p-2 bg-white rounded-full shadow hover:bg-gray-50">
                        <HeartIcon className="h-5 w-5 text-gray-400" />
                      </button>
                    </div>
                  </div>

                  {/* Campaign Content */}
                  <div className="p-6">
                    <div className="flex items-center mb-2">
                      <span className="text-sm text-gray-500 mr-2">
                        {campaign.category.icon} {campaign.category.name}
                      </span>
                    </div>

                    <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                      {campaign.title}
                    </h3>

                    {campaign.subtitle && (
                      <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                        {campaign.subtitle}
                      </p>
                    )}

                    <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                      {campaign.short_description}
                    </p>

                    {/* Creator Info */}
                    <div className="flex items-center mb-4">
                      <UserIcon className="h-4 w-4 text-gray-400 mr-2" />
                      <span className="text-sm text-gray-600">
                        by {campaign.creator.first_name} {campaign.creator.last_name}
                      </span>
                      {campaign.creator.creator_verified && (
                        <span className="ml-2 text-blue-600 text-xs">✓ Verified</span>
                      )}
                    </div>

                    {/* Funding Progress */}
                    <div className="mb-4">
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600">
                          {formatCurrency(campaign.current_funding)} raised
                        </span>
                        <span className="text-gray-600">
                          {Math.round(calculateProgress(campaign.current_funding, campaign.funding_goal))}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${calculateProgress(campaign.current_funding, campaign.funding_goal)}%` }}
                        ></div>
                      </div>
                      <div className="flex justify-between text-xs text-gray-500 mt-1">
                        <span>Goal: {formatCurrency(campaign.funding_goal)}</span>
                                                 <span>{getDaysLeft(campaign.end_date)} days left</span>
                      </div>
                    </div>

                    {/* Action Button */}
                    <Link
                      to={`/campaigns/${campaign.id}`}
                      className="w-full flex items-center justify-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
                    >
                      <EyeIcon className="h-4 w-4 mr-2" />
                      View Campaign
                    </Link>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {pagination.total > pagination.pageSize && (
              <div className="flex justify-center">
                <nav className="flex items-center space-x-2">
                  <button
                    onClick={() => handlePageChange(pagination.page - 1)}
                    disabled={pagination.page === 1}
                    className="px-3 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  
                  {[...Array(Math.ceil(pagination.total / pagination.pageSize))].map((_, index) => {
                    const page = index + 1;
                    const isCurrentPage = page === pagination.page;
                    const isNearCurrent = Math.abs(page - pagination.page) <= 2;
                    
                    if (isCurrentPage || isNearCurrent || page === 1 || page === Math.ceil(pagination.total / pagination.pageSize)) {
                      return (
                        <button
                          key={page}
                          onClick={() => handlePageChange(page)}
                          className={`px-3 py-2 border rounded-md ${
                            isCurrentPage
                              ? 'bg-primary-600 text-white border-primary-600'
                              : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                          }`}
                        >
                          {page}
                        </button>
                      );
                    } else if (page === 2 || page === Math.ceil(pagination.total / pagination.pageSize) - 1) {
                      return <span key={page} className="px-2 py-2 text-gray-500">...</span>;
                    }
                    return null;
                  })}
                  
                  <button
                    onClick={() => handlePageChange(pagination.page + 1)}
                    disabled={pagination.page >= Math.ceil(pagination.total / pagination.pageSize)}
                    className="px-3 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </nav>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Campaigns;

