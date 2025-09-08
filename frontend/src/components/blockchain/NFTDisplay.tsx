import React, { useState, useEffect } from 'react';
import { 
  PhotoIcon, 
  ArrowTopRightOnSquareIcon,
  ShareIcon,
  HeartIcon
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid';

interface NFTProps {
  tokenId: number;
  name: string;
  description?: string;
  imageUrl?: string;
  metadataUri?: string;
  openseaUrl?: string;
  isTransferable?: boolean;
  onTransfer?: (tokenId: number) => void;
  onLike?: (tokenId: number) => void;
  className?: string;
}

const NFTDisplay: React.FC<NFTProps> = ({
  tokenId,
  name,
  description,
  imageUrl,
  metadataUri,
  openseaUrl,
  isTransferable = true,
  onTransfer,
  onLike,
  className = ''
}) => {
  const [imageError, setImageError] = useState(false);
  const [isLiked, setIsLiked] = useState(false);
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [transferAddress, setTransferAddress] = useState('');

  useEffect(() => {
    // Check if NFT is liked (from localStorage or API)
    const likedNFTs = JSON.parse(localStorage.getItem('likedNFTs') || '[]');
    setIsLiked(likedNFTs.includes(tokenId));
  }, [tokenId]);

  const handleImageError = () => {
    setImageError(true);
  };

  const handleLike = () => {
    const newLikedState = !isLiked;
    setIsLiked(newLikedState);
    
    // Update localStorage
    const likedNFTs = JSON.parse(localStorage.getItem('likedNFTs') || '[]');
    if (newLikedState) {
      likedNFTs.push(tokenId);
    } else {
      const index = likedNFTs.indexOf(tokenId);
      if (index > -1) {
        likedNFTs.splice(index, 1);
      }
    }
    localStorage.setItem('likedNFTs', JSON.stringify(likedNFTs));
    
    if (onLike) {
      onLike(tokenId);
    }
  };

  const handleTransfer = () => {
    if (transferAddress.trim()) {
      if (onTransfer) {
        onTransfer(tokenId);
      }
      setShowTransferModal(false);
      setTransferAddress('');
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: name,
          text: description,
          url: window.location.href,
        });
      } catch (err) {
        console.error('Error sharing:', err);
      }
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(window.location.href);
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow ${className}`}>
      {/* NFT Image */}
      <div className="aspect-square bg-gray-100 relative">
        {imageUrl && !imageError ? (
          <img
            src={imageUrl}
            alt={name}
            className="w-full h-full object-cover"
            onError={handleImageError}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <PhotoIcon className="h-12 w-12 text-gray-400" />
          </div>
        )}
        
        {/* Overlay Actions */}
        <div className="absolute top-2 right-2 flex space-x-1">
          <button
            onClick={handleLike}
            className="p-2 bg-white/80 rounded-full hover:bg-white transition-colors"
          >
            {isLiked ? (
              <HeartSolidIcon className="h-5 w-5 text-red-500" />
            ) : (
              <HeartIcon className="h-5 w-5 text-gray-600" />
            )}
          </button>
          
          <button
            onClick={handleShare}
            className="p-2 bg-white/80 rounded-full hover:bg-white transition-colors"
          >
            <ShareIcon className="h-5 w-5 text-gray-600" />
          </button>
        </div>
      </div>

      {/* NFT Info */}
      <div className="p-4">
        <h3 className="font-semibold text-lg text-gray-900 mb-1">{name}</h3>
        {description && (
          <p className="text-gray-600 text-sm mb-3 line-clamp-2">{description}</p>
        )}
        
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-500">Token #{tokenId}</span>
          
          <div className="flex space-x-2">
            {openseaUrl && (
              <a
                href={openseaUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <ArrowTopRightOnSquareIcon className="h-4 w-4" />
              </a>
            )}
          </div>
        </div>

        {/* Transfer Button */}
        {isTransferable && onTransfer && (
          <button
            onClick={() => setShowTransferModal(true)}
            className="w-full mt-3 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
          >
            Transfer
          </button>
        )}
      </div>

      {/* Transfer Modal */}
      {showTransferModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold mb-4">Transfer NFT</h3>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Recipient Address
              </label>
              <input
                type="text"
                value={transferAddress}
                onChange={(e) => setTransferAddress(e.target.value)}
                placeholder="0x..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div className="flex space-x-3">
              <button
                onClick={() => setShowTransferModal(false)}
                className="flex-1 px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleTransfer}
                disabled={!transferAddress.trim()}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Transfer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NFTDisplay;
