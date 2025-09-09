// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title CampaignFunding
 * @dev Smart contract for managing film campaign funding with escrow functionality
 * @author CineChainLanka
 */
contract CampaignFunding is ReentrancyGuard, Ownable {
    using SafeMath for uint256;

    // Campaign structure
    struct Campaign {
        uint256 id;
        address creator;
        string title;
        string description;
        uint256 fundingGoal;
        uint256 currentFunding;
        uint256 startTime;
        uint256 endTime;
        bool isActive;
        bool isFunded;
        bool isFailed;
        uint256 backerCount;
        mapping(address => uint256) contributions;
        mapping(address => bool) hasContributed;
    }

    // Events
    event CampaignCreated(
        uint256 indexed campaignId,
        address indexed creator,
        string title,
        uint256 fundingGoal,
        uint256 startTime,
        uint256 endTime
    );
    
    event ContributionMade(
        uint256 indexed campaignId,
        address indexed backer,
        uint256 amount,
        uint256 totalFunding
    );
    
    event CampaignFunded(uint256 indexed campaignId, uint256 totalFunding);
    event CampaignFailed(uint256 indexed campaignId, uint256 totalFunding);
    event RefundProcessed(uint256 indexed campaignId, address indexed backer, uint256 amount);
    event FundsWithdrawn(uint256 indexed campaignId, address indexed creator, uint256 amount);

    // State variables
    mapping(uint256 => Campaign) public campaigns;
    uint256 public campaignCount;
    uint256 public platformFeePercentage = 300; // 3% in basis points
    address public platformWallet;
    IERC20 public usdtToken;
    
    // Campaign status constants
    uint256 public constant CAMPAIGN_ACTIVE = 1;
    uint256 public constant CAMPAIGN_FUNDED = 2;
    uint256 public constant CAMPAIGN_FAILED = 3;

    constructor(address _usdtToken, address _platformWallet) {
        usdtToken = IERC20(_usdtToken);
        platformWallet = _platformWallet;
    }

    /**
     * @dev Create a new campaign
     * @param _title Campaign title
     * @param _description Campaign description
     * @param _fundingGoal Funding goal in USDT (with 6 decimals)
     * @param _duration Campaign duration in seconds
     */
    function createCampaign(
        string memory _title,
        string memory _description,
        uint256 _fundingGoal,
        uint256 _duration
    ) external returns (uint256) {
        require(_fundingGoal > 0, "Funding goal must be greater than 0");
        require(_duration > 0, "Duration must be greater than 0");
        require(bytes(_title).length > 0, "Title cannot be empty");
        require(bytes(_description).length > 0, "Description cannot be empty");

        campaignCount++;
        uint256 campaignId = campaignCount;
        
        Campaign storage campaign = campaigns[campaignId];
        campaign.id = campaignId;
        campaign.creator = msg.sender;
        campaign.title = _title;
        campaign.description = _description;
        campaign.fundingGoal = _fundingGoal;
        campaign.currentFunding = 0;
        campaign.startTime = block.timestamp;
        campaign.endTime = block.timestamp.add(_duration);
        campaign.isActive = true;
        campaign.isFunded = false;
        campaign.isFailed = false;
        campaign.backerCount = 0;

        emit CampaignCreated(
            campaignId,
            msg.sender,
            _title,
            _fundingGoal,
            block.timestamp,
            campaign.endTime
        );

        return campaignId;
    }

    /**
     * @dev Contribute to a campaign
     * @param _campaignId Campaign ID
     * @param _amount Contribution amount in USDT
     */
    function contribute(uint256 _campaignId, uint256 _amount) external nonReentrant {
        require(_campaignId > 0 && _campaignId <= campaignCount, "Invalid campaign ID");
        require(_amount > 0, "Contribution amount must be greater than 0");
        
        Campaign storage campaign = campaigns[_campaignId];
        require(campaign.isActive, "Campaign is not active");
        require(block.timestamp >= campaign.startTime, "Campaign has not started");
        require(block.timestamp <= campaign.endTime, "Campaign has ended");
        require(!campaign.isFunded, "Campaign is already funded");
        require(!campaign.isFailed, "Campaign has failed");

        // Transfer USDT from backer to contract
        require(
            usdtToken.transferFrom(msg.sender, address(this), _amount),
            "USDT transfer failed"
        );

        // Update campaign state
        if (!campaign.hasContributed[msg.sender]) {
            campaign.backerCount = campaign.backerCount.add(1);
            campaign.hasContributed[msg.sender] = true;
        }
        
        campaign.contributions[msg.sender] = campaign.contributions[msg.sender].add(_amount);
        campaign.currentFunding = campaign.currentFunding.add(_amount);

        emit ContributionMade(_campaignId, msg.sender, _amount, campaign.currentFunding);

        // Check if campaign is fully funded
        if (campaign.currentFunding >= campaign.fundingGoal) {
            _markCampaignAsFunded(_campaignId);
        }
    }

    /**
     * @dev Mark campaign as funded and transfer funds to creator
     */
    function _markCampaignAsFunded(uint256 _campaignId) internal {
        Campaign storage campaign = campaigns[_campaignId];
        campaign.isActive = false;
        campaign.isFunded = true;

        // Calculate platform fee
        uint256 platformFee = campaign.currentFunding.mul(platformFeePercentage).div(10000);
        uint256 creatorAmount = campaign.currentFunding.sub(platformFee);

        // Transfer funds
        if (platformFee > 0) {
            usdtToken.transfer(platformWallet, platformFee);
        }
        usdtToken.transfer(campaign.creator, creatorAmount);

        emit CampaignFunded(_campaignId, campaign.currentFunding);
        emit FundsWithdrawn(_campaignId, campaign.creator, creatorAmount);
    }

    /**
     * @dev Mark campaign as failed and enable refunds
     */
    function markCampaignAsFailed(uint256 _campaignId) external onlyOwner {
        require(_campaignId > 0 && _campaignId <= campaignCount, "Invalid campaign ID");
        
        Campaign storage campaign = campaigns[_campaignId];
        require(campaign.isActive, "Campaign is not active");
        require(block.timestamp > campaign.endTime, "Campaign has not ended yet");
        require(!campaign.isFunded, "Campaign is already funded");

        campaign.isActive = false;
        campaign.isFailed = true;

        emit CampaignFailed(_campaignId, campaign.currentFunding);
    }

    /**
     * @dev Process refund for a specific backer
     * @param _campaignId Campaign ID
     * @param _backer Backer address
     */
    function processRefund(uint256 _campaignId, address _backer) external nonReentrant {
        require(_campaignId > 0 && _campaignId <= campaignCount, "Invalid campaign ID");
        
        Campaign storage campaign = campaigns[_campaignId];
        require(campaign.isFailed, "Campaign has not failed");
        require(campaign.contributions[_backer] > 0, "No contribution found");
        require(!campaign.hasContributed[_backer] || campaign.contributions[_backer] > 0, "Already refunded");

        uint256 refundAmount = campaign.contributions[_backer];
        campaign.contributions[_backer] = 0;

        require(usdtToken.transfer(_backer, refundAmount), "Refund transfer failed");

        emit RefundProcessed(_campaignId, _backer, refundAmount);
    }

    /**
     * @dev Process all refunds for a failed campaign
     * @param _campaignId Campaign ID
     * @param _backers Array of backer addresses
     */
    function processBulkRefunds(uint256 _campaignId, address[] memory _backers) external onlyOwner {
        require(_campaignId > 0 && _campaignId <= campaignCount, "Invalid campaign ID");
        
        Campaign storage campaign = campaigns[_campaignId];
        require(campaign.isFailed, "Campaign has not failed");

        for (uint256 i = 0; i < _backers.length; i++) {
            address backer = _backers[i];
            if (campaign.contributions[backer] > 0) {
                uint256 refundAmount = campaign.contributions[backer];
                campaign.contributions[backer] = 0;
                usdtToken.transfer(backer, refundAmount);
                emit RefundProcessed(_campaignId, backer, refundAmount);
            }
        }
    }

    /**
     * @dev Get campaign details
     * @param _campaignId Campaign ID
     */
    function getCampaign(uint256 _campaignId) external view returns (
        uint256 id,
        address creator,
        string memory title,
        string memory description,
        uint256 fundingGoal,
        uint256 currentFunding,
        uint256 startTime,
        uint256 endTime,
        bool isActive,
        bool isFunded,
        bool isFailed,
        uint256 backerCount
    ) {
        require(_campaignId > 0 && _campaignId <= campaignCount, "Invalid campaign ID");
        
        Campaign storage campaign = campaigns[_campaignId];
        return (
            campaign.id,
            campaign.creator,
            campaign.title,
            campaign.description,
            campaign.fundingGoal,
            campaign.currentFunding,
            campaign.startTime,
            campaign.endTime,
            campaign.isActive,
            campaign.isFunded,
            campaign.isFailed,
            campaign.backerCount
        );
    }

    /**
     * @dev Get backer's contribution amount
     * @param _campaignId Campaign ID
     * @param _backer Backer address
     */
    function getContribution(uint256 _campaignId, address _backer) external view returns (uint256) {
        require(_campaignId > 0 && _campaignId <= campaignCount, "Invalid campaign ID");
        return campaigns[_campaignId].contributions[_backer];
    }

    /**
     * @dev Check if backer has contributed to campaign
     * @param _campaignId Campaign ID
     * @param _backer Backer address
     */
    function hasContributed(uint256 _campaignId, address _backer) external view returns (bool) {
        require(_campaignId > 0 && _campaignId <= campaignCount, "Invalid campaign ID");
        return campaigns[_campaignId].hasContributed[_backer];
    }

    /**
     * @dev Update platform fee percentage (only owner)
     * @param _feePercentage New fee percentage in basis points
     */
    function updatePlatformFee(uint256 _feePercentage) external onlyOwner {
        require(_feePercentage <= 1000, "Fee cannot exceed 10%");
        platformFeePercentage = _feePercentage;
    }

    /**
     * @dev Update platform wallet address (only owner)
     * @param _newWallet New platform wallet address
     */
    function updatePlatformWallet(address _newWallet) external onlyOwner {
        require(_newWallet != address(0), "Invalid wallet address");
        platformWallet = _newWallet;
    }

    /**
     * @dev Get campaign creator address
     * @param _campaignId Campaign ID
     * @return Creator address
     */
    function getCampaignCreator(uint256 _campaignId) external view returns (address) {
        require(_campaignId > 0 && _campaignId <= campaignCount, "Invalid campaign ID");
        return campaigns[_campaignId].creator;
    }

    /**
     * @dev Emergency withdrawal function (only owner)
     */
    function emergencyWithdraw() external onlyOwner {
        uint256 balance = usdtToken.balanceOf(address(this));
        require(balance > 0, "No tokens to withdraw");
        usdtToken.transfer(owner(), balance);
    }
}
