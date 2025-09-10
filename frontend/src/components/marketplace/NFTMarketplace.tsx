import React, { useState, useEffect } from 'react';
import { useAppSelector } from '../../store/hooks';
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  HeartIcon,
  EyeIcon,
  CurrencyDollarIcon,
  ClockIcon,
  UserIcon,
  TagIcon
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid';
import { Line, Bar } from 'react-chartjs-2';
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
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface NFTListing {
  id: number;
  nft_id: number;
  campaign: {
    id: number;
    title: string;
    creator: {
      username: string;
      first_name: string;
      last_name: string;
    };
  };
  owner: {
    username: string;
    first_name: string;
    last_name: string;
  };
  price: number;
  currency: string;
  royalty_percentage: number;
  description: string;
  image_url: string;
  metadata: any;
  listing_type: 'fixed' | 'auction';
  status: 'active' | 'sold' | 'cancelled' | 'expired';
  view_count: number;
  like_count: number;
  created_at: string;
  expires_at?: string;
  highest_bid?: number;
  bid_count?: number;
}

interface FilterOptions {
  category: string;
  priceRange: [number, number];
  listingType: string;
  status: string;
  sortBy: string;
}

const NFTMarketplace: React.FC = () => {
  const { user } = useAppSelector((state) => state.auth);
  const [listings, setListings] = useState<NFTListing[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedListing, setSelectedListing] = useState<NFTListing | null>(null);
  const [showListingModal, setShowListingModal] = useState(false);
  const [filters, setFilters] = useState<FilterOptions>({
    category: '',
    priceRange: [0, 1000000],
    listingType: '',
    status: 'active',
    sortBy: 'newest'
  });

  useEffect(() => {
    fetchListings();
  }, [filters, searchQuery]);

  const fetchListings = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      
      if (searchQuery) params.append('search', searchQuery);
      if (filters.category) params.append('category', filters.category);
      if (filters.listingType) params.append('listing_type', filters.listingType);
      if (filters.status) params.append('status', filters.status);
      if (filters.sortBy) params.append('sort_by', filters.sortBy);
      params.append('price_min', filters.priceRange[0].toString());
      params.append('price_max', filters.priceRange[1].toString());

      const response = await fetch(`/api/marketplace/listings/?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setListings(data.results || data || []);
      } else {
        console.error('Failed to fetch listings:', response.statusText);
      }
    } catch (error) {
      console.error('Error fetching listings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async (listingId: number) => {
    try {
      const response = await fetch(`/api/marketplace/listings/${listingId}/like/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        // Update local state based on response
        setListings(prev => prev.map(listing => 
          listing.id === listingId 
            ? { ...listing, like_count: data.liked ? listing.like_count + 1 : Math.max(0, listing.like_count - 1) }
            : listing
        ));
      } else {
        console.error('Failed to like listing:', response.statusText);
      }
    } catch (error) {
      console.error('Error liking listing:', error);
    }
  };

  const handlePlaceBid = async (listingId: number, bidAmount: number) => {
    try {
      const response = await fetch(`/api/marketplace/listings/${listingId}/bid/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          amount: bidAmount,
          currency: 'USDT'
        }),
      });

      if (response.ok) {
        alert('Bid placed successfully!');
        fetchListings(); // Refresh listings
      } else {
        const errorData = await response.json();
        alert(`Failed to place bid: ${errorData.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error placing bid:', error);
      alert('Error placing bid');
    }
  };

  const handleBuyNow = async (listingId: number) => {
    try {
      const response = await fetch(`/api/marketplace/listings/${listingId}/buy/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          payment_method: 'usdt'
        }),
      });

      if (response.ok) {
        const data = await response.json();
        alert('Purchase successful!');
        fetchListings(); // Refresh listings
      } else {
        const errorData = await response.json();
        alert(`Failed to purchase: ${errorData.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error purchasing:', error);
      alert('Error purchasing NFT');
    }
  };

  const formatPrice = (price: number, currency: string = 'USDT') => {
    // Handle USDT and other non-standard currency codes
    if (currency === 'USDT') {
      return `$${price.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 })} USDT`;
    }
    
    // For valid ISO currency codes, use Intl.NumberFormat
    try {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 0,
      }).format(price);
    } catch (error) {
      // Fallback for invalid currency codes
      return `${price.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 })} ${currency}`;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getTimeRemaining = (expiresAt: string) => {
    const now = new Date();
    const expiry = new Date(expiresAt);
    const diff = expiry.getTime() - now.getTime();
    
    if (diff <= 0) return 'Expired';
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (days > 0) return `${days}d ${hours}h`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'sold':
        return 'bg-blue-100 text-blue-800';
      case 'cancelled':
        return 'bg-gray-100 text-gray-800';
      case 'expired':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">NFT Marketplace</h1>
          <p className="mt-2 text-gray-600">
            Discover, buy, and sell unique NFTs from film campaigns
          </p>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search NFTs, campaigns, or creators..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>

            {/* Filter Button */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <FunnelIcon className="h-5 w-5 mr-2" />
              Filters
            </button>
          </div>

          {/* Filter Panel */}
          {showFilters && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Category
                  </label>
                  <select
                    value={filters.category}
                    onChange={(e) => setFilters({...filters, category: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">All Categories</option>
                    <option value="drama">Drama</option>
                    <option value="action">Action</option>
                    <option value="comedy">Comedy</option>
                    <option value="horror">Horror</option>
                    <option value="documentary">Documentary</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Listing Type
                  </label>
                  <select
                    value={filters.listingType}
                    onChange={(e) => setFilters({...filters, listingType: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">All Types</option>
                    <option value="fixed">Fixed Price</option>
                    <option value="auction">Auction</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Status
                  </label>
                  <select
                    value={filters.status}
                    onChange={(e) => setFilters({...filters, status: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="active">Active</option>
                    <option value="sold">Sold</option>
                    <option value="expired">Expired</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Sort By
                  </label>
                  <select
                    value={filters.sortBy}
                    onChange={(e) => setFilters({...filters, sortBy: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="newest">Newest First</option>
                    <option value="oldest">Oldest First</option>
                    <option value="price_low">Price: Low to High</option>
                    <option value="price_high">Price: High to Low</option>
                    <option value="most_liked">Most Liked</option>
                    <option value="most_viewed">Most Viewed</option>
                  </select>
                </div>
              </div>

              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Price Range: {formatPrice(filters.priceRange[0])} - {formatPrice(filters.priceRange[1])}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1000000"
                  step="1000"
                  value={filters.priceRange[1]}
                  onChange={(e) => setFilters({
                    ...filters, 
                    priceRange: [filters.priceRange[0], parseInt(e.target.value)]
                  })}
                  className="w-full"
                />
              </div>
            </div>
          )}
        </div>

        {/* Results Count */}
        <div className="mb-6">
          <p className="text-gray-600">
            Showing {listings.length} NFT{listings.length !== 1 ? 's' : ''}
          </p>
        </div>

        {/* NFT Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {listings.map((listing) => (
            <div
              key={listing.id}
              className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => {
                setSelectedListing(listing);
                setShowListingModal(true);
              }}
            >
              {/* NFT Image */}
              <div className="relative">
                <img
                  src={listing.image_url || 'https://via.placeholder.com/300x300'}
                  alt={`NFT #${listing.nft_id}`}
                  className="w-full h-48 object-cover rounded-t-lg"
                />
                <div className="absolute top-2 right-2">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(listing.status)}`}>
                    {listing.status}
                  </span>
                </div>
                {listing.listing_type === 'auction' && (
                  <div className="absolute top-2 left-2">
                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800">
                      Auction
                    </span>
                  </div>
                )}
              </div>

              {/* NFT Details */}
              <div className="p-4">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-lg font-semibold text-gray-900 truncate">
                    {listing.campaign.title}
                  </h3>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleLike(listing.id);
                    }}
                    className="text-gray-400 hover:text-red-500"
                  >
                    <HeartIcon className="h-5 w-5" />
                  </button>
                </div>

                <p className="text-sm text-gray-600 mb-2">
                  by {listing.campaign.creator.first_name} {listing.campaign.creator.last_name}
                </p>

                <div className="flex items-center justify-between mb-3">
                  <div>
                    <p className="text-lg font-bold text-gray-900">
                      {formatPrice(listing.price, listing.currency)}
                    </p>
                    {listing.listing_type === 'auction' && listing.highest_bid && (
                      <p className="text-sm text-gray-500">
                        Highest: {formatPrice(listing.highest_bid, listing.currency)}
                      </p>
                    )}
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-500">
                      {listing.royalty_percentage}% royalty
                    </p>
                  </div>
                </div>

                <div className="flex items-center justify-between text-sm text-gray-500">
                  <div className="flex items-center">
                    <EyeIcon className="h-4 w-4 mr-1" />
                    {listing.view_count}
                  </div>
                  <div className="flex items-center">
                    <HeartIcon className="h-4 w-4 mr-1" />
                    {listing.like_count}
                  </div>
                  {listing.listing_type === 'auction' && listing.expires_at && (
                    <div className="flex items-center">
                      <ClockIcon className="h-4 w-4 mr-1" />
                      {getTimeRemaining(listing.expires_at)}
                    </div>
                  )}
                </div>

                <div className="mt-4">
                  {listing.listing_type === 'fixed' ? (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleBuyNow(listing.id);
                      }}
                      className="w-full bg-primary-600 text-white py-2 px-4 rounded-lg hover:bg-primary-700 transition-colors"
                    >
                      Buy Now
                    </button>
                  ) : (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedListing(listing);
                        setShowListingModal(true);
                      }}
                      className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors"
                    >
                      Place Bid
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {listings.length === 0 && !loading && (
          <div className="text-center py-12">
            <TagIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No NFTs found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Try adjusting your search or filter criteria.
            </p>
          </div>
        )}

        {/* Listing Modal */}
        {showListingModal && selectedListing && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <h2 className="text-2xl font-bold text-gray-900">
                    {selectedListing.campaign.title}
                  </h2>
                  <button
                    onClick={() => setShowListingModal(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <img
                      src={selectedListing.image_url || 'https://via.placeholder.com/400x400'}
                      alt={`NFT #${selectedListing.nft_id}`}
                      className="w-full h-64 object-cover rounded-lg"
                    />
                  </div>

                  <div>
                    <p className="text-gray-600 mb-4">
                      by {selectedListing.campaign.creator.first_name} {selectedListing.campaign.creator.last_name}
                    </p>

                    <p className="text-gray-700 mb-4">
                      {selectedListing.description}
                    </p>

                    <div className="space-y-2 mb-6">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Price:</span>
                        <span className="font-semibold">
                          {formatPrice(selectedListing.price, selectedListing.currency)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Royalty:</span>
                        <span className="font-semibold">
                          {selectedListing.royalty_percentage}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Views:</span>
                        <span className="font-semibold">
                          {selectedListing.view_count}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Likes:</span>
                        <span className="font-semibold">
                          {selectedListing.like_count}
                        </span>
                      </div>
                    </div>

                    {selectedListing.listing_type === 'fixed' ? (
                      <button
                        onClick={() => {
                          handleBuyNow(selectedListing.id);
                          setShowListingModal(false);
                        }}
                        className="w-full bg-primary-600 text-white py-3 px-4 rounded-lg hover:bg-primary-700 transition-colors"
                      >
                        Buy Now
                      </button>
                    ) : (
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-gray-600">Current Bid:</span>
                          <span className="font-semibold">
                            {formatPrice(selectedListing.highest_bid || 0, selectedListing.currency)}
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-gray-600">Bids:</span>
                          <span className="font-semibold">
                            {selectedListing.bid_count || 0}
                          </span>
                        </div>
                        <button
                          onClick={() => {
                            const bidAmount = prompt('Enter your bid amount:');
                            if (bidAmount && !isNaN(parseFloat(bidAmount))) {
                              handlePlaceBid(selectedListing.id, parseFloat(bidAmount));
                              setShowListingModal(false);
                            }
                          }}
                          className="w-full bg-purple-600 text-white py-3 px-4 rounded-lg hover:bg-purple-700 transition-colors"
                        >
                          Place Bid
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default NFTMarketplace;