// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

contract RoyaltyDistribution is Ownable, ReentrancyGuard {
    using SafeMath for uint256;

    struct Campaign {
        address creator;
        uint256 totalRaised;
        uint256 creatorPercentage;
        uint256 platformPercentage;
        bool isActive;
        uint256 totalRevenue;
        uint256 totalDistributed;
    }

    struct InvestorShare {
        address investor;
        uint256 nftId;
        uint256 contributionAmount;
        uint256 sharePercentage;
        uint256 totalRoyalties;
        bool isActive;
    }

    mapping(uint256 => Campaign) public campaigns;
    mapping(uint256 => mapping(uint256 => InvestorShare)) public investorShares;
    mapping(address => uint256) public platformFees;
    mapping(address => uint256) public creatorRoyalties;
    mapping(address => uint256) public investorRoyalties;
    
    uint256 public nextCampaignId = 1;
    uint256 public constant FEE_DENOMINATOR = 10000;
    address public immutable USDT_TOKEN;
    address public platformWallet;

    event RevenueReceived(uint256 indexed campaignId, uint256 amount, uint256 timestamp);
    event RoyaltyDistributed(uint256 indexed campaignId, address indexed investor, uint256 amount, uint256 timestamp);

    constructor(address _usdtToken, address _platformWallet) {
        USDT_TOKEN = _usdtToken;
        platformWallet = _platformWallet;
    }

    function createCampaign(
        address creator,
        uint256 totalRaised,
        uint256 creatorPercentage,
        uint256 platformPercentage
    ) external onlyOwner returns (uint256) {
        uint256 campaignId = nextCampaignId++;
        campaigns[campaignId] = Campaign({
            creator: creator,
            totalRaised: totalRaised,
            creatorPercentage: creatorPercentage,
            platformPercentage: platformPercentage,
            isActive: true,
            totalRevenue: 0,
            totalDistributed: 0
        });
        return campaignId;
    }

    function addInvestorShare(
        uint256 campaignId,
        uint256 nftId,
        address investor,
        uint256 contributionAmount
    ) external onlyOwner {
        uint256 sharePercentage = contributionAmount.mul(FEE_DENOMINATOR).div(campaigns[campaignId].totalRaised);
        investorShares[campaignId][nftId] = InvestorShare({
            investor: investor,
            nftId: nftId,
            contributionAmount: contributionAmount,
            sharePercentage: sharePercentage,
            totalRoyalties: 0,
            isActive: true
        });
    }

    function receiveRevenue(uint256 campaignId, uint256 amount) external nonReentrant {
        IERC20(USDT_TOKEN).transferFrom(msg.sender, address(this), amount);
        campaigns[campaignId].totalRevenue = campaigns[campaignId].totalRevenue.add(amount);
        emit RevenueReceived(campaignId, amount, block.timestamp);
    }

    function distributeRoyalties(uint256 campaignId) external nonReentrant {
        Campaign storage campaign = campaigns[campaignId];
        uint256 availableRevenue = campaign.totalRevenue.sub(campaign.totalDistributed);
        
        uint256 platformFee = availableRevenue.mul(campaign.platformPercentage).div(FEE_DENOMINATOR);
        uint256 creatorRoyalty = availableRevenue.mul(campaign.creatorPercentage).div(FEE_DENOMINATOR);
        uint256 investorRevenue = availableRevenue.sub(platformFee).sub(creatorRoyalty);
        
        platformFees[USDT_TOKEN] = platformFees[USDT_TOKEN].add(platformFee);
        creatorRoyalties[campaign.creator] = creatorRoyalties[campaign.creator].add(creatorRoyalty);
        
        // Distribute investor royalties based on their share percentages
        for (uint256 i = 0; i < 1000; i++) { // Assuming max 1000 investors per campaign
            InvestorShare storage share = investorShares[campaignId][i];
            if (share.isActive && share.sharePercentage > 0) {
                uint256 investorAmount = investorRevenue.mul(share.sharePercentage).div(FEE_DENOMINATOR);
                investorRoyalties[share.investor] = investorRoyalties[share.investor].add(investorAmount);
                share.totalRoyalties = share.totalRoyalties.add(investorAmount);
                emit RoyaltyDistributed(campaignId, share.investor, investorAmount, block.timestamp);
            }
        }
        
        campaign.totalDistributed = campaign.totalDistributed.add(availableRevenue);
    }

    function claimCreatorRoyalties() external nonReentrant {
        uint256 amount = creatorRoyalties[msg.sender];
        creatorRoyalties[msg.sender] = 0;
        IERC20(USDT_TOKEN).transfer(msg.sender, amount);
    }

    function claimInvestorRoyalties() external nonReentrant {
        uint256 amount = investorRoyalties[msg.sender];
        investorRoyalties[msg.sender] = 0;
        IERC20(USDT_TOKEN).transfer(msg.sender, amount);
    }
}