// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

/**
 * @title RoyaltyDistribution
 * @dev Smart contract for automated royalty distribution to creators and investors
 * @author CineChainLanka
 */
contract RoyaltyDistribution is ReentrancyGuard, Ownable, Pausable {
    using SafeMath for uint256;

    // Revenue source structure
    struct RevenueSource {
        uint256 id;
        string name;
        address tokenAddress; // USDT or other stablecoin
        bool isActive;
        uint256 totalRevenue;
        uint256 platformFeePercentage; // Platform fee in basis points
        uint256 creatorFeePercentage;  // Creator fee in basis points
        uint256 investorFeePercentage; // Investor fee in basis points
    }

    // Revenue entry structure
    struct RevenueEntry {
        uint256 id;
        uint256 campaignId;
        uint256 sourceId;
        uint256 amount;
        uint256 timestamp;
        string description;
        bool isProcessed;
    }

    // Royalty distribution structure
    struct RoyaltyDistribution {
        uint256 id;
        uint256 campaignId;
        uint256 revenueEntryId;
        address creator;
        uint256 creatorAmount;
        uint256 platformAmount;
        uint256 totalInvestorAmount;
        uint256 timestamp;
        bool isProcessed;
    }

    // Investor share structure
    struct InvestorShare {
        address investor;
        uint256 nftId;
        uint256 contributionAmount;
        uint256 sharePercentage;
        uint256 royaltyAmount;
        bool isClaimed;
    }

    // Events
    event RevenueSourceAdded(
        uint256 indexed sourceId,
        string name,
        address tokenAddress,
        uint256 platformFee,
        uint256 creatorFee,
        uint256 investorFee
    );
    
    event RevenueRecorded(
        uint256 indexed entryId,
        uint256 indexed campaignId,
        uint256 sourceId,
        uint256 amount,
        string description
    );
    
    event RoyaltyDistributed(
        uint256 indexed distributionId,
        uint256 indexed campaignId,
        address indexed creator,
        uint256 creatorAmount,
        uint256 platformAmount,
        uint256 totalInvestorAmount
    );
    
    event InvestorRoyaltyClaimed(
        uint256 indexed distributionId,
        address indexed investor,
        uint256 nftId,
        uint256 amount
    );

    // State variables
    mapping(uint256 => RevenueSource) public revenueSources;
    mapping(uint256 => RevenueEntry) public revenueEntries;
    mapping(uint256 => RoyaltyDistribution) public royaltyDistributions;
    mapping(uint256 => mapping(uint256 => InvestorShare)) public campaignInvestors; // campaignId => nftId => InvestorShare
    mapping(uint256 => uint256[]) public campaignNFTs; // campaignId => nftIds[]
    mapping(address => uint256[]) public investorDistributions; // investor => distributionIds[]
    
    uint256 public revenueSourceCount;
    uint256 public revenueEntryCount;
    uint256 public distributionCount;
    
    address public platformWallet;
    address public nftContract;
    address public campaignContract;
    
    // Fee percentages (in basis points, 10000 = 100%)
    uint256 public defaultPlatformFee = 500; // 5%
    uint256 public defaultCreatorFee = 3000; // 30%
    uint256 public defaultInvestorFee = 6500; // 65%

    constructor(
        address _platformWallet,
        address _nftContract,
        address _campaignContract
    ) {
        platformWallet = _platformWallet;
        nftContract = _nftContract;
        campaignContract = _campaignContract;
    }

    /**
     * @dev Add a new revenue source
     */
    function addRevenueSource(
        string memory _name,
        address _tokenAddress,
        uint256 _platformFee,
        uint256 _creatorFee,
        uint256 _investorFee
    ) external onlyOwner {
        require(bytes(_name).length > 0, "Name cannot be empty");
        require(_tokenAddress != address(0), "Invalid token address");
        require(_platformFee.add(_creatorFee).add(_investorFee) == 10000, "Fees must equal 100%");
        
        revenueSourceCount++;
        uint256 sourceId = revenueSourceCount;
        
        revenueSources[sourceId] = RevenueSource({
            id: sourceId,
            name: _name,
            tokenAddress: _tokenAddress,
            isActive: true,
            totalRevenue: 0,
            platformFeePercentage: _platformFee,
            creatorFeePercentage: _creatorFee,
            investorFeePercentage: _investorFee
        });
        
        emit RevenueSourceAdded(sourceId, _name, _tokenAddress, _platformFee, _creatorFee, _investorFee);
    }

    /**
     * @dev Record revenue for a campaign
     */
    function recordRevenue(
        uint256 _campaignId,
        uint256 _sourceId,
        uint256 _amount,
        string memory _description
    ) external onlyOwner nonReentrant {
        require(_campaignId > 0, "Invalid campaign ID");
        require(_sourceId > 0 && _sourceId <= revenueSourceCount, "Invalid source ID");
        require(_amount > 0, "Amount must be greater than 0");
        require(bytes(_description).length > 0, "Description cannot be empty");
        
        RevenueSource storage source = revenueSources[_sourceId];
        require(source.isActive, "Revenue source is not active");
        
        revenueEntryCount++;
        uint256 entryId = revenueEntryCount;
        
        revenueEntries[entryId] = RevenueEntry({
            id: entryId,
            campaignId: _campaignId,
            sourceId: _sourceId,
            amount: _amount,
            timestamp: block.timestamp,
            description: _description,
            isProcessed: false
        });
        
        source.totalRevenue = source.totalRevenue.add(_amount);
        
        emit RevenueRecorded(entryId, _campaignId, _sourceId, _amount, _description);
    }

    /**
     * @dev Process royalty distribution for a campaign
     */
    function processRoyaltyDistribution(
        uint256 _campaignId,
        uint256 _revenueEntryId
    ) external onlyOwner nonReentrant whenNotPaused {
        require(_revenueEntryId > 0 && _revenueEntryId <= revenueEntryCount, "Invalid revenue entry ID");
        
        RevenueEntry storage entry = revenueEntries[_revenueEntryId];
        require(entry.campaignId == _campaignId, "Campaign ID mismatch");
        require(!entry.isProcessed, "Revenue entry already processed");
        
        RevenueSource storage source = revenueSources[entry.sourceId];
        require(source.isActive, "Revenue source is not active");
        
        // Get campaign creator (this would need to be passed or retrieved from campaign contract)
        address creator = _getCampaignCreator(_campaignId);
        require(creator != address(0), "Creator not found");
        
        // Calculate distribution amounts
        uint256 platformAmount = entry.amount.mul(source.platformFeePercentage).div(10000);
        uint256 creatorAmount = entry.amount.mul(source.creatorFeePercentage).div(10000);
        uint256 investorAmount = entry.amount.mul(source.investorFeePercentage).div(10000);
        
        // Create distribution record
        distributionCount++;
        uint256 distributionId = distributionCount;
        
        royaltyDistributions[distributionId] = RoyaltyDistribution({
            id: distributionId,
            campaignId: _campaignId,
            revenueEntryId: _revenueEntryId,
            creator: creator,
            creatorAmount: creatorAmount,
            platformAmount: platformAmount,
            totalInvestorAmount: investorAmount,
            timestamp: block.timestamp,
            isProcessed: false
        });
        
        // Transfer platform fee
        if (platformAmount > 0) {
            IERC20(source.tokenAddress).transfer(platformWallet, platformAmount);
        }
        
        // Transfer creator fee
        if (creatorAmount > 0) {
            IERC20(source.tokenAddress).transfer(creator, creatorAmount);
        }
        
        // Process investor distributions
        _processInvestorDistributions(distributionId, _campaignId, source.tokenAddress, investorAmount);
        
        // Mark as processed
        entry.isProcessed = true;
        royaltyDistributions[distributionId].isProcessed = true;
        
        emit RoyaltyDistributed(
            distributionId,
            _campaignId,
            creator,
            creatorAmount,
            platformAmount,
            investorAmount
        );
    }

    /**
     * @dev Process investor distributions based on their NFT holdings
     */
    function _processInvestorDistributions(
        uint256 _distributionId,
        uint256 _campaignId,
        address _tokenAddress,
        uint256 _totalInvestorAmount
    ) internal {
        uint256[] memory nftIds = campaignNFTs[_campaignId];
        uint256 totalContributions = 0;
        
        // Calculate total contributions for this campaign
        for (uint256 i = 0; i < nftIds.length; i++) {
            uint256 nftId = nftIds[i];
            if (campaignInvestors[_campaignId][nftId].investor != address(0)) {
                totalContributions = totalContributions.add(campaignInvestors[_campaignId][nftId].contributionAmount);
            }
        }
        
        // Distribute to each investor based on their contribution percentage
        for (uint256 i = 0; i < nftIds.length; i++) {
            uint256 nftId = nftIds[i];
            InvestorShare storage investor = campaignInvestors[_campaignId][nftId];
            
            if (investor.investor != address(0) && totalContributions > 0) {
                uint256 sharePercentage = investor.contributionAmount.mul(10000).div(totalContributions);
                uint256 royaltyAmount = _totalInvestorAmount.mul(sharePercentage).div(10000);
                
                investor.sharePercentage = sharePercentage;
                investor.royaltyAmount = royaltyAmount;
                investor.isClaimed = false;
                
                // Add to investor's distribution list
                investorDistributions[investor.investor].push(_distributionId);
            }
        }
    }

    /**
     * @dev Claim royalty for an investor
     */
    function claimInvestorRoyalty(
        uint256 _distributionId,
        uint256 _nftId
    ) external nonReentrant {
        require(_distributionId > 0 && _distributionId <= distributionCount, "Invalid distribution ID");
        
        RoyaltyDistribution storage distribution = royaltyDistributions[_distributionId];
        require(distribution.isProcessed, "Distribution not processed yet");
        
        InvestorShare storage investor = campaignInvestors[distribution.campaignId][_nftId];
        require(investor.investor == msg.sender, "Not authorized to claim");
        require(!investor.isClaimed, "Already claimed");
        require(investor.royaltyAmount > 0, "No royalty to claim");
        
        // Get revenue source to determine token address
        RevenueEntry storage entry = revenueEntries[distribution.revenueEntryId];
        RevenueSource storage source = revenueSources[entry.sourceId];
        
        // Transfer royalty to investor
        IERC20(source.tokenAddress).transfer(msg.sender, investor.royaltyAmount);
        
        investor.isClaimed = true;
        
        emit InvestorRoyaltyClaimed(_distributionId, msg.sender, _nftId, investor.royaltyAmount);
    }

    /**
     * @dev Register investor for a campaign (called when NFT is minted)
     */
    function registerInvestor(
        uint256 _campaignId,
        uint256 _nftId,
        address _investor,
        uint256 _contributionAmount
    ) external {
        require(msg.sender == nftContract, "Only NFT contract can register investors");
        require(_campaignId > 0, "Invalid campaign ID");
        require(_nftId > 0, "Invalid NFT ID");
        require(_investor != address(0), "Invalid investor address");
        require(_contributionAmount > 0, "Invalid contribution amount");
        
        campaignInvestors[_campaignId][_nftId] = InvestorShare({
            investor: _investor,
            nftId: _nftId,
            contributionAmount: _contributionAmount,
            sharePercentage: 0,
            royaltyAmount: 0,
            isClaimed: false
        });
        
        // Add to campaign NFTs list
        campaignNFTs[_campaignId].push(_nftId);
    }

    /**
     * @dev Get campaign creator from campaign contract
     */
    function _getCampaignCreator(uint256 _campaignId) internal view returns (address) {
        // Call the campaign contract to get creator address
        (bool success, bytes memory data) = campaignContract.staticcall(
            abi.encodeWithSignature("getCampaignCreator(uint256)", _campaignId)
        );
        
        if (success && data.length >= 32) {
            address creator = abi.decode(data, (address));
            return creator;
        }
        
        // Fallback: return zero address if call fails
        return address(0);
    }

    /**
     * @dev Get investor's claimable royalties
     */
    function getClaimableRoyalties(address _investor) external view returns (uint256) {
        uint256 totalClaimable = 0;
        uint256[] memory distributions = investorDistributions[_investor];
        
        for (uint256 i = 0; i < distributions.length; i++) {
            uint256 distributionId = distributions[i];
            RoyaltyDistribution storage distribution = royaltyDistributions[distributionId];
            
            if (distribution.isProcessed) {
                uint256[] memory nftIds = campaignNFTs[distribution.campaignId];
                for (uint256 j = 0; j < nftIds.length; j++) {
                    uint256 nftId = nftIds[j];
                    InvestorShare storage investor = campaignInvestors[distribution.campaignId][nftId];
                    if (investor.investor == _investor && !investor.isClaimed) {
                        totalClaimable = totalClaimable.add(investor.royaltyAmount);
                    }
                }
            }
        }
        
        return totalClaimable;
    }

    /**
     * @dev Get distribution details for an investor
     */
    function getInvestorDistributions(address _investor) external view returns (uint256[] memory) {
        return investorDistributions[_investor];
    }

    /**
     * @dev Get investor share details for a specific distribution
     */
    function getInvestorShare(
        uint256 _campaignId,
        uint256 _nftId
    ) external view returns (InvestorShare memory) {
        return campaignInvestors[_campaignId][_nftId];
    }

    /**
     * @dev Update fee percentages (only owner)
     */
    function updateFeePercentages(
        uint256 _platformFee,
        uint256 _creatorFee,
        uint256 _investorFee
    ) external onlyOwner {
        require(_platformFee.add(_creatorFee).add(_investorFee) == 10000, "Fees must equal 100%");
        defaultPlatformFee = _platformFee;
        defaultCreatorFee = _creatorFee;
        defaultInvestorFee = _investorFee;
    }

    /**
     * @dev Pause contract (only owner)
     */
    function pause() external onlyOwner {
        _pause();
    }

    /**
     * @dev Unpause contract (only owner)
     */
    function unpause() external onlyOwner {
        _unpause();
    }

    /**
     * @dev Emergency withdrawal (only owner)
     */
    function emergencyWithdraw(address _tokenAddress) external onlyOwner {
        uint256 balance = IERC20(_tokenAddress).balanceOf(address(this));
        require(balance > 0, "No tokens to withdraw");
        IERC20(_tokenAddress).transfer(owner(), balance);
    }
}
