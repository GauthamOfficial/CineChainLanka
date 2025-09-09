import React, { useEffect, useState } from 'react';
import { useAppSelector } from '../../store/hooks';
import api from '../../utils/api';
import { 
  MagnifyingGlassIcon,
  FunnelIcon,
  CurrencyDollarIcon,
  ClockIcon,
  UserIcon,
  EyeIcon,
  HeartIcon,
  ShareIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  FireIcon,
  StarIcon
} from '@heroicons/react/24/outline';

interface NFTListing {
  id: number;
  nft_id: number;
  campaign_id: number;
  campaign: {
    id: number;
    title: string;
  };
  owner: {
    id: number;
    username: string;
    avatar?: string;
  };
  price: number;
  currency: string;
  royalty_percentage: number;
  description: string;
  image_url: string;
  metadata: {
    title: string;
    description: string;
    attributes: Array<{
      trait_type: string;
      value: string;
    }>;
  };
  listing_type: 'fixed' | 'auction';
  status: 'active' | 'sold' | 'cancelled';
  created_at: string;
  expires_at?: string;
  bid_count?: number;
  highest_bid?: number;
  view_count: number;
  like_count: number;
  is_liked: boolean;
}

interface FilterOptions {
  price_min: number;
  price_max: number;
  campaign_id: number | null;
  listing_type: 'all' | 'fixed' | 'auction';
  sort_by: 'price_asc' | 'price_desc' | 'newest' | 'oldest' | 'popularity';
  royalty_min: number;
  royalty_max: number;
}

const NFTMarketplace: React.FC = () => {
  const { user } = useAppSelector((state) => state.auth);
  const [listings, setListings] = useState<NFTListing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<FilterOptions>({
    price_min: 0,
    price_max: 10000,
    campaign_id: null,
    listing_type: 'all',
    sort_by: 'newest',
    royalty_min: 0,
    royalty_max: 100
  });
  const [selectedListing, setSelectedListing] = useState<NFTListing | null>(null);
  const [bidAmount, setBidAmount] = useState('');
  const [placingBid, setPlacingBid] = useState(false);

  useEffect(() => {
    fetchListings();
  }, [filters, searchQuery]);

  const fetchListings = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();
      if (searchQuery) params.append('search', searchQuery);
      if (filters.price_min > 0) params.append('price_min', filters.price_min.toString());
      if (filters.price_max < 10000) params.append('price_max', filters.price_max.toString());
      if (filters.campaign_id) params.append('campaign_id', filters.campaign_id.toString());
      if (filters.listing_type !== 'all') params.append('listing_type', filters.listing_type);
      if (filters.sort_by) params.append('sort_by', filters.sort_by);
      if (filters.royalty_min > 0) params.append('royalty_min', filters.royalty_min.toString());
      if (filters.royalty_max < 100) params.append('royalty_max', filters.royalty_max.toString());

      const response = await api.get(`/api/marketplace/nfts/?${params.toString()}`);
      setListings(response.data.results || response.data);

    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const placeBid = async (listingId: number) => {
    if (!bidAmount || parseFloat(bidAmount) <= 0) return;

    try {
      setPlacingBid(true);
      
      await api.post(`/api/marketplace/nfts/${listingId}/bid/`, {
        amount: parseFloat(bidAmount),
        currency: 'USDT'
      });

      // Refresh listings after successful bid
      await fetchListings();
      setBidAmount('');
      setSelectedListing(null);
      
    } catch (err) {
      console.error('Error placing bid:', err);
      // You might want to show a toast notification here
    } finally {
      setPlacingBid(false);
    }
  };

  const buyNow = async (listingId: number) => {
    try {
      await api.post(`/api/marketplace/nfts/${listingId}/buy/`);

      // Refresh listings after successful purchase
      await fetchListings();
      
    } catch (err) {
      console.error('Error buying NFT:', err);
      // You might want to show a toast notification here
    }
  };

  const toggleLike = async (listingId: number) => {
    try {
      await api.post(`/api/marketplace/nfts/${listingId}/like/`);

      // Refresh listings after successful like
      await fetchListings();
      
    } catch (err) {
      console.error('Error toggling like:', err);
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

  const getTimeRemaining = (expiresAt?: string) => {
    if (!expiresAt) return null;
    
    const now = new Date().getTime();
    const expiry = new Date(expiresAt).getTime();
    const diff = expiry - now;
    
    if (diff <= 0) return 'Expired';
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (days > 0) return `${days}d ${hours}h`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  const getListingTypeColor = (type: string) => {
    switch (type) {
      case 'fixed': return 'text-green-600 bg-green-100';
      case 'auction': return 'text-purple-600 bg-purple-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="h-96 bg-gray-200 rounded"></div>
              ))}
            </div>
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
                <MagnifyingGlassIcon className="h-5 w-5 text-red-400" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error loading marketplace</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
                <button
                  onClick={fetchListings}
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
              <h1 className="text-3xl font-bold text-gray-900">NFT Marketplace</h1>
              <p className="text-gray-600 mt-2">
                Discover, buy, and sell campaign NFTs
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                <FunnelIcon className="h-4 w-4 mr-2" />
                Filters
              </button>
            </div>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search NFTs, campaigns, or creators..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Filters Panel */}
          {showFilters && (
            <div className="mt-4 bg-white p-6 rounded-lg shadow-sm border">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Filters</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Price Range</label>
                  <div className="flex space-x-2">
                    <input
                      type="number"
                      placeholder="Min"
                      value={filters.price_min}
                      onChange={(e) => setFilters({...filters, price_min: parseFloat(e.target.value) || 0})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    />
                    <input
                      type="number"
                      placeholder="Max"
                      value={filters.price_max}
                      onChange={(e) => setFilters({...filters, price_max: parseFloat(e.target.value) || 10000})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Listing Type</label>
                  <select
                    value={filters.listing_type}
                    onChange={(e) => setFilters({...filters, listing_type: e.target.value as any})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  >
                    <option value="all">All Types</option>
                    <option value="fixed">Fixed Price</option>
                    <option value="auction">Auction</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Royalty Range</label>
                  <div className="flex space-x-2">
                    <input
                      type="number"
                      placeholder="Min %"
                      value={filters.royalty_min}
                      onChange={(e) => setFilters({...filters, royalty_min: parseFloat(e.target.value) || 0})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    />
                    <input
                      type="number"
                      placeholder="Max %"
                      value={filters.royalty_max}
                      onChange={(e) => setFilters({...filters, royalty_max: parseFloat(e.target.value) || 100})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
                  <select
                    value={filters.sort_by}
                    onChange={(e) => setFilters({...filters, sort_by: e.target.value as any})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  >
                    <option value="newest">Newest First</option>
                    <option value="oldest">Oldest First</option>
                    <option value="price_asc">Price: Low to High</option>
                    <option value="price_desc">Price: High to Low</option>
                    <option value="popularity">Most Popular</option>
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Results Count */}
        <div className="mb-6">
          <p className="text-sm text-gray-600">
            Showing {listings.length} NFT{listings.length !== 1 ? 's' : ''}
          </p>
        </div>

        {/* NFT Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {listings.map((listing) => (
            <div key={listing.id} className="bg-white rounded-lg shadow-sm border overflow-hidden hover:shadow-md transition-shadow">
              {/* NFT Image */}
              <div className="relative">
                <img
                  src={listing.image_url || '/placeholder-nft.png'}
                  alt={listing.metadata.title}
                  className="w-full h-48 object-cover"
                />
                <div className="absolute top-2 left-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getListingTypeColor(listing.listing_type)}`}>
                    {listing.listing_type}
                  </span>
                </div>
                <div className="absolute top-2 right-2 flex space-x-1">
                  <button
                    onClick={() => toggleLike(listing.id)}
                    className="p-1 bg-white/80 rounded-full hover:bg-white transition-colors"
                  >
                    <HeartIcon className={`h-4 w-4 ${listing.is_liked ? 'text-red-500 fill-current' : 'text-gray-500'}`} />
                  </button>
                  <button className="p-1 bg-white/80 rounded-full hover:bg-white transition-colors">
                    <ShareIcon className="h-4 w-4 text-gray-500" />
                  </button>
                </div>
                {listing.expires_at && (
                  <div className="absolute bottom-2 left-2 right-2">
                    <div className="bg-black/80 text-white px-2 py-1 rounded text-xs text-center">
                      <ClockIcon className="h-3 w-3 inline mr-1" />
                      {getTimeRemaining(listing.expires_at)}
                    </div>
                  </div>
                )}
              </div>

              {/* NFT Details */}
              <div className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h3 className="text-sm font-medium text-gray-900 truncate">
                      {listing.metadata.title}
                    </h3>
                    <p className="text-xs text-gray-500 truncate">
                      {listing.campaign.title}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-gray-900">
                      {formatCurrency(listing.price)}
                    </p>
                    <p className="text-xs text-gray-500">
                      {listing.royalty_percentage}% royalty
                    </p>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                  <div className="flex items-center">
                    <UserIcon className="h-3 w-3 mr-1" />
                    {listing.owner.username}
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="flex items-center">
                      <EyeIcon className="h-3 w-3 mr-1" />
                      {formatNumber(listing.view_count)}
                    </div>
                    <div className="flex items-center">
                      <HeartIcon className="h-3 w-3 mr-1" />
                      {formatNumber(listing.like_count)}
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-2">
                  {listing.listing_type === 'fixed' ? (
                    <button
                      onClick={() => buyNow(listing.id)}
                      className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded text-sm font-medium transition-colors"
                    >
                      Buy Now
                    </button>
                  ) : (
                    <button
                      onClick={() => setSelectedListing(listing)}
                      className="flex-1 bg-purple-600 hover:bg-purple-700 text-white px-3 py-2 rounded text-sm font-medium transition-colors"
                    >
                      Place Bid
                    </button>
                  )}
                  <button
                    onClick={() => setSelectedListing(listing)}
                    className="px-3 py-2 border border-gray-300 rounded text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    View
                  </button>
                </div>

                {listing.bid_count && listing.bid_count > 0 && (
                  <div className="mt-2 text-xs text-gray-500 text-center">
                    {listing.bid_count} bid{listing.bid_count !== 1 ? 's' : ''}
                    {listing.highest_bid && (
                      <span className="ml-1">
                        • Highest: {formatCurrency(listing.highest_bid)}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {listings.length === 0 && !loading && (
          <div className="text-center py-12">
            <MagnifyingGlassIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No NFTs found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Try adjusting your search criteria or check back later for new listings.
            </p>
          </div>
        )}

        {/* Bid Modal */}
        {selectedListing && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-md w-full p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                {selectedListing.listing_type === 'auction' ? 'Place Bid' : 'NFT Details'}
              </h3>
              
              <div className="mb-4">
                <img
                  src={selectedListing.image_url || '/placeholder-nft.png'}
                  alt={selectedListing.metadata.title}
                  className="w-full h-48 object-cover rounded-lg mb-4"
                />
                <h4 className="text-sm font-medium text-gray-900">{selectedListing.metadata.title}</h4>
                <p className="text-sm text-gray-500">{selectedListing.campaign.title}</p>
                <p className="text-sm text-gray-700 mt-2">{selectedListing.description}</p>
              </div>

              {selectedListing.listing_type === 'auction' ? (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Bid Amount (USDT)
                    </label>
                    <input
                      type="number"
                      value={bidAmount}
                      onChange={(e) => setBidAmount(e.target.value)}
                      placeholder="Enter bid amount"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    />
                  </div>
                  <div className="text-sm text-gray-500">
                    Current price: {formatCurrency(selectedListing.price)}
                    {selectedListing.highest_bid && (
                      <span className="ml-2">
                        • Highest bid: {formatCurrency(selectedListing.highest_bid)}
                      </span>
                    )}
                  </div>
                  <div className="flex space-x-3">
                    <button
                      onClick={() => placeBid(selectedListing.id)}
                      disabled={placingBid || !bidAmount || parseFloat(bidAmount) <= 0}
                      className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white px-4 py-2 rounded text-sm font-medium transition-colors"
                    >
                      {placingBid ? 'Placing Bid...' : 'Place Bid'}
                    </button>
                    <button
                      onClick={() => setSelectedListing(null)}
                      className="px-4 py-2 border border-gray-300 rounded text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-gray-900">
                      {formatCurrency(selectedListing.price)}
                    </p>
                    <p className="text-sm text-gray-500">
                      {selectedListing.royalty_percentage}% royalty included
                    </p>
                  </div>
                  <div className="flex space-x-3">
                    <button
                      onClick={() => buyNow(selectedListing.id)}
                      className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm font-medium transition-colors"
                    >
                      Buy Now
                    </button>
                    <button
                      onClick={() => setSelectedListing(null)}
                      className="px-4 py-2 border border-gray-300 rounded text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                    >
                      Close
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default NFTMarketplace;
