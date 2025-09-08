// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/token/common/ERC2981.sol";

/**
 * @title CineChainNFT
 * @dev NFT contract for film campaign contributions with royalty support
 * @author CineChainLanka
 */
contract CineChainNFT is ERC721, ERC721URIStorage, ERC721Enumerable, ERC2981, Ownable, ReentrancyGuard {
    using SafeMath for uint256;

    // NFT structure
    struct NFTData {
        uint256 tokenId;
        uint256 campaignId;
        address creator;
        address owner;
        uint256 contributionAmount;
        uint256 royaltyPercentage;
        string metadataURI;
        uint256 mintedAt;
        bool isTransferable;
    }

    // Events
    event NFTCreated(
        uint256 indexed tokenId,
        uint256 indexed campaignId,
        address indexed creator,
        address owner,
        uint256 contributionAmount,
        string metadataURI
    );
    
    event RoyaltyUpdated(uint256 indexed tokenId, uint256 newRoyaltyPercentage);
    event TransferabilityUpdated(uint256 indexed tokenId, bool isTransferable);
    event BatchMinted(address indexed to, uint256[] tokenIds, uint256 campaignId);

    // State variables
    mapping(uint256 => NFTData) public nftData;
    mapping(uint256 => uint256) public campaignNFTCount; // Track NFTs per campaign
    mapping(address => uint256[]) public userNFTs; // Track user's NFTs
    
    uint256 private _tokenIdCounter;
    uint256 public maxSupply = 1000000; // Maximum supply of NFTs
    uint256 public defaultRoyaltyPercentage = 500; // 5% default royalty in basis points
    address public campaignFundingContract;
    address public platformWallet;
    
    // Royalty recipient mapping
    mapping(uint256 => address) public royaltyRecipients;

    constructor(
        string memory name,
        string memory symbol,
        address _campaignFundingContract,
        address _platformWallet
    ) ERC721(name, symbol) {
        campaignFundingContract = _campaignFundingContract;
        platformWallet = _platformWallet;
        _tokenIdCounter = 1;
    }

    /**
     * @dev Mint NFT for campaign contribution
     * @param to Recipient address
     * @param campaignId Campaign ID
     * @param contributionAmount Contribution amount
     * @param metadataURI IPFS metadata URI
     * @param royaltyPercentage Royalty percentage in basis points
     */
    function mintNFT(
        address to,
        uint256 campaignId,
        uint256 contributionAmount,
        string memory metadataURI,
        uint256 royaltyPercentage
    ) external onlyOwner nonReentrant returns (uint256) {
        require(to != address(0), "Invalid recipient address");
        require(contributionAmount > 0, "Contribution amount must be greater than 0");
        require(bytes(metadataURI).length > 0, "Metadata URI cannot be empty");
        require(royaltyPercentage <= 1000, "Royalty cannot exceed 10%");
        require(_tokenIdCounter <= maxSupply, "Maximum supply reached");

        uint256 tokenId = _tokenIdCounter;
        _tokenIdCounter++;

        // Create NFT data
        nftData[tokenId] = NFTData({
            tokenId: tokenId,
            campaignId: campaignId,
            creator: to, // For now, contributor is the creator
            owner: to,
            contributionAmount: contributionAmount,
            royaltyPercentage: royaltyPercentage,
            metadataURI: metadataURI,
            mintedAt: block.timestamp,
            isTransferable: true
        });

        // Update counters
        campaignNFTCount[campaignId]++;
        userNFTs[to].push(tokenId);

        // Set royalty recipient
        royaltyRecipients[tokenId] = to;

        // Mint the NFT
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, metadataURI);
        _setTokenRoyalty(tokenId, to, uint96(royaltyPercentage));

        emit NFTCreated(tokenId, campaignId, to, to, contributionAmount, metadataURI);

        return tokenId;
    }

    /**
     * @dev Batch mint NFTs for multiple contributions
     * @param to Recipient address
     * @param campaignId Campaign ID
     * @param contributionAmounts Array of contribution amounts
     * @param metadataURIs Array of metadata URIs
     * @param royaltyPercentages Array of royalty percentages
     */
    function batchMintNFTs(
        address to,
        uint256 campaignId,
        uint256[] memory contributionAmounts,
        string[] memory metadataURIs,
        uint256[] memory royaltyPercentages
    ) external onlyOwner nonReentrant returns (uint256[] memory) {
        require(to != address(0), "Invalid recipient address");
        require(
            contributionAmounts.length == metadataURIs.length &&
            metadataURIs.length == royaltyPercentages.length,
            "Array lengths must match"
        );
        require(contributionAmounts.length > 0, "Must mint at least one NFT");
        require(_tokenIdCounter + contributionAmounts.length - 1 <= maxSupply, "Maximum supply exceeded");

        uint256[] memory tokenIds = new uint256[](contributionAmounts.length);

        for (uint256 i = 0; i < contributionAmounts.length; i++) {
            require(contributionAmounts[i] > 0, "Contribution amount must be greater than 0");
            require(bytes(metadataURIs[i]).length > 0, "Metadata URI cannot be empty");
            require(royaltyPercentages[i] <= 1000, "Royalty cannot exceed 10%");

            uint256 tokenId = _tokenIdCounter;
            _tokenIdCounter++;

            // Create NFT data
            nftData[tokenId] = NFTData({
                tokenId: tokenId,
                campaignId: campaignId,
                creator: to,
                owner: to,
                contributionAmount: contributionAmounts[i],
                royaltyPercentage: royaltyPercentages[i],
                metadataURI: metadataURIs[i],
                mintedAt: block.timestamp,
                isTransferable: true
            });

            // Update counters
            campaignNFTCount[campaignId]++;
            userNFTs[to].push(tokenId);

            // Set royalty recipient
            royaltyRecipients[tokenId] = to;

            // Mint the NFT
            _safeMint(to, tokenId);
            _setTokenURI(tokenId, metadataURIs[i]);
            _setTokenRoyalty(tokenId, to, uint96(royaltyPercentages[i]));

            tokenIds[i] = tokenId;

            emit NFTCreated(tokenId, campaignId, to, to, contributionAmounts[i], metadataURIs[i]);
        }

        emit BatchMinted(to, tokenIds, campaignId);

        return tokenIds;
    }

    /**
     * @dev Update NFT royalty percentage
     * @param tokenId Token ID
     * @param newRoyaltyPercentage New royalty percentage in basis points
     */
    function updateRoyalty(uint256 tokenId, uint256 newRoyaltyPercentage) external {
        require(_exists(tokenId), "Token does not exist");
        require(newRoyaltyPercentage <= 1000, "Royalty cannot exceed 10%");
        require(
            msg.sender == ownerOf(tokenId) || msg.sender == owner(),
            "Not authorized to update royalty"
        );

        nftData[tokenId].royaltyPercentage = newRoyaltyPercentage;
        _setTokenRoyalty(tokenId, royaltyRecipients[tokenId], uint96(newRoyaltyPercentage));

        emit RoyaltyUpdated(tokenId, newRoyaltyPercentage);
    }

    /**
     * @dev Update NFT transferability
     * @param tokenId Token ID
     * @param isTransferable Whether NFT is transferable
     */
    function updateTransferability(uint256 tokenId, bool isTransferable) external {
        require(_exists(tokenId), "Token does not exist");
        require(
            msg.sender == ownerOf(tokenId) || msg.sender == owner(),
            "Not authorized to update transferability"
        );

        nftData[tokenId].isTransferable = isTransferable;

        emit TransferabilityUpdated(tokenId, isTransferable);
    }

    /**
     * @dev Override _isApprovedOrOwner to allow owner to transfer any NFT
     */
    function _isApprovedOrOwner(address spender, uint256 tokenId) internal view override returns (bool) {
        address tokenOwner = ownerOf(tokenId);
        return (spender == tokenOwner || isApprovedForAll(tokenOwner, spender) || getApproved(tokenId) == spender || spender == owner());
    }

    /**
     * @dev Override transfer function to check transferability
     */
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 tokenId,
        uint256 batchSize
    ) internal override(ERC721, ERC721Enumerable) {
        if (from != address(0) && to != address(0)) {
            // Allow owner to transfer any NFT
            require(
                nftData[tokenId].isTransferable || msg.sender == owner(),
                "NFT is not transferable"
            );
        }
        super._beforeTokenTransfer(from, to, tokenId, batchSize);
    }

    /**
     * @dev Override _afterTokenTransfer to update NFT data
     */
    function _afterTokenTransfer(
        address from,
        address to,
        uint256 tokenId,
        uint256 batchSize
    ) internal override {
        if (from != address(0) && to != address(0)) {
            nftData[tokenId].owner = to;
            
            // Update user NFT tracking
            if (from != address(0)) {
                _removeFromUserNFTs(from, tokenId);
            }
            if (to != address(0)) {
                userNFTs[to].push(tokenId);
            }
        }
        super._afterTokenTransfer(from, to, tokenId, batchSize);
    }

    /**
     * @dev Remove token from user's NFT list
     * @param user User address
     * @param tokenId Token ID to remove
     */
    function _removeFromUserNFTs(address user, uint256 tokenId) internal {
        uint256[] storage userTokens = userNFTs[user];
        for (uint256 i = 0; i < userTokens.length; i++) {
            if (userTokens[i] == tokenId) {
                userTokens[i] = userTokens[userTokens.length - 1];
                userTokens.pop();
                break;
            }
        }
    }

    /**
     * @dev Get NFT data
     * @param tokenId Token ID
     */
    function getNFTData(uint256 tokenId) external view returns (NFTData memory) {
        require(_exists(tokenId), "Token does not exist");
        return nftData[tokenId];
    }

    /**
     * @dev Get user's NFTs
     * @param user User address
     */
    function getUserNFTs(address user) external view returns (uint256[] memory) {
        return userNFTs[user];
    }

    /**
     * @dev Get campaign NFTs
     * @param campaignId Campaign ID
     */
    function getCampaignNFTs(uint256 campaignId) external view returns (uint256[] memory) {
        uint256 count = campaignNFTCount[campaignId];
        uint256[] memory tokenIds = new uint256[](count);
        uint256 index = 0;

        for (uint256 i = 1; i < _tokenIdCounter; i++) {
            if (nftData[i].campaignId == campaignId) {
                tokenIds[index] = i;
                index++;
                if (index >= count) break;
            }
        }

        return tokenIds;
    }

    /**
     * @dev Get total NFTs minted for a campaign
     * @param campaignId Campaign ID
     */
    function getCampaignNFTCount(uint256 campaignId) external view returns (uint256) {
        return campaignNFTCount[campaignId];
    }

    /**
     * @dev Get total supply
     */
    function totalSupply() public view override(ERC721Enumerable) returns (uint256) {
        return _tokenIdCounter - 1;
    }

    /**
     * @dev Override supportsInterface
     */
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721Enumerable, ERC721URIStorage, ERC2981)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }

    /**
     * @dev Override tokenURI
     */
    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    /**
     * @dev Override _burn
     */
    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);
    }

    /**
     * @dev Update campaign funding contract address (only owner)
     * @param _newContract New contract address
     */
    function updateCampaignFundingContract(address _newContract) external onlyOwner {
        require(_newContract != address(0), "Invalid contract address");
        campaignFundingContract = _newContract;
    }

    /**
     * @dev Update platform wallet address (only owner)
     * @param _newWallet New wallet address
     */
    function updatePlatformWallet(address _newWallet) external onlyOwner {
        require(_newWallet != address(0), "Invalid wallet address");
        platformWallet = _newWallet;
    }

    /**
     * @dev Update maximum supply (only owner)
     * @param _newMaxSupply New maximum supply
     */
    function updateMaxSupply(uint256 _newMaxSupply) external onlyOwner {
        require(_newMaxSupply > _tokenIdCounter - 1, "Max supply must be greater than current supply");
        maxSupply = _newMaxSupply;
    }
}
