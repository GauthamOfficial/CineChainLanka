const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("RoyaltyDistribution", function () {
  let royaltyDistribution;
  let mockUSDT;
  let owner;
  let creator;
  let investor1;
  let investor2;
  let platformWallet;

  beforeEach(async function () {
    [owner, creator, investor1, investor2, platformWallet] = await ethers.getSigners();

    // Deploy MockUSDT
    const MockUSDT = await ethers.getContractFactory("MockUSDT");
    mockUSDT = await MockUSDT.deploy();
    await mockUSDT.deployed();

    // Deploy RoyaltyDistribution
    const RoyaltyDistribution = await ethers.getContractFactory("RoyaltyDistribution");
    royaltyDistribution = await RoyaltyDistribution.deploy(mockUSDT.address, platformWallet.address);
    await royaltyDistribution.deployed();

    // Mint USDT to test accounts
    await mockUSDT.mint(creator.address, ethers.utils.parseEther("1000"));
    await mockUSDT.mint(investor1.address, ethers.utils.parseEther("1000"));
    await mockUSDT.mint(investor2.address, ethers.utils.parseEther("1000"));
    await mockUSDT.mint(owner.address, ethers.utils.parseEther("1000"));

    // Approve USDT spending
    await mockUSDT.connect(creator).approve(royaltyDistribution.address, ethers.utils.parseEther("1000"));
    await mockUSDT.connect(investor1).approve(royaltyDistribution.address, ethers.utils.parseEther("1000"));
    await mockUSDT.connect(investor2).approve(royaltyDistribution.address, ethers.utils.parseEther("1000"));
    await mockUSDT.connect(owner).approve(royaltyDistribution.address, ethers.utils.parseEther("1000"));
  });

  describe("Campaign Creation", function () {
    it("Should create a campaign successfully", async function () {
      const totalRaised = ethers.utils.parseEther("100");
      const creatorPercentage = 2000; // 20%
      const platformPercentage = 500; // 5%

      const tx = await royaltyDistribution.createCampaign(
        creator.address,
        totalRaised,
        creatorPercentage,
        platformPercentage
      );

      const campaignId = await royaltyDistribution.nextCampaignId() - 1;
      const campaign = await royaltyDistribution.getCampaign(campaignId);

      expect(campaign.creator).to.equal(creator.address);
      expect(campaign.totalRaised).to.equal(totalRaised);
      expect(campaign.creatorPercentage).to.equal(creatorPercentage);
      expect(campaign.platformPercentage).to.equal(platformPercentage);
      expect(campaign.isActive).to.be.true;
    });

    it("Should fail to create campaign with invalid parameters", async function () {
      await expect(
        royaltyDistribution.createCampaign(
          ethers.constants.AddressZero,
          ethers.utils.parseEther("100"),
          2000,
          500
        )
      ).to.be.revertedWith("Invalid creator address");

      await expect(
        royaltyDistribution.createCampaign(
          creator.address,
          0,
          2000,
          500
        )
      ).to.be.revertedWith("Invalid total raised amount");
    });
  });

  describe("Investor Share Management", function () {
    let campaignId;

    beforeEach(async function () {
      const totalRaised = ethers.utils.parseEther("100");
      const creatorPercentage = 2000; // 20%
      const platformPercentage = 500; // 5%

      await royaltyDistribution.createCampaign(
        creator.address,
        totalRaised,
        creatorPercentage,
        platformPercentage
      );

      campaignId = await royaltyDistribution.nextCampaignId() - 1;
    });

    it("Should add investor shares successfully", async function () {
      const contribution1 = ethers.utils.parseEther("30");
      const contribution2 = ethers.utils.parseEther("20");

      await royaltyDistribution.addInvestorShare(campaignId, 1, investor1.address, contribution1);
      await royaltyDistribution.addInvestorShare(campaignId, 2, investor2.address, contribution2);

      const share1 = await royaltyDistribution.getInvestorShare(campaignId, 1);
      const share2 = await royaltyDistribution.getInvestorShare(campaignId, 2);

      expect(share1.investor).to.equal(investor1.address);
      expect(share1.contributionAmount).to.equal(contribution1);
      expect(share1.sharePercentage).to.equal(3000); // 30%

      expect(share2.investor).to.equal(investor2.address);
      expect(share2.contributionAmount).to.equal(contribution2);
      expect(share2.sharePercentage).to.equal(2000); // 20%
    });
  });

  describe("Revenue Distribution", function () {
    let campaignId;

    beforeEach(async function () {
      const totalRaised = ethers.utils.parseEther("100");
      const creatorPercentage = 2000; // 20%
      const platformPercentage = 500; // 5%

      await royaltyDistribution.createCampaign(
        creator.address,
        totalRaised,
        creatorPercentage,
        platformPercentage
      );

      campaignId = await royaltyDistribution.nextCampaignId() - 1;

      // Add investor shares
      await royaltyDistribution.addInvestorShare(campaignId, 1, investor1.address, ethers.utils.parseEther("30"));
      await royaltyDistribution.addInvestorShare(campaignId, 2, investor2.address, ethers.utils.parseEther("20"));
    });

    it("Should receive and distribute revenue correctly", async function () {
      const revenueAmount = ethers.utils.parseEther("50");

      // Receive revenue
      await royaltyDistribution.connect(owner).receiveRevenue(campaignId, revenueAmount);

      // Check campaign revenue
      const campaign = await royaltyDistribution.getCampaign(campaignId);
      expect(campaign.totalRevenue).to.equal(revenueAmount);

      // Distribute royalties
      await royaltyDistribution.distributeRoyalties(campaignId);

      // Check creator royalties
      const creatorRoyalty = await royaltyDistribution.creatorRoyalties(creator.address);
      expect(creatorRoyalty).to.equal(ethers.utils.parseEther("10")); // 20% of 50

      // Check platform fees
      const platformFee = await royaltyDistribution.platformFees(mockUSDT.address);
      expect(platformFee).to.equal(ethers.utils.parseEther("2.5")); // 5% of 50
    });

    it("Should allow creators to claim royalties", async function () {
      const revenueAmount = ethers.utils.parseEther("50");
      
      await royaltyDistribution.connect(owner).receiveRevenue(campaignId, revenueAmount);
      await royaltyDistribution.distributeRoyalties(campaignId);

      const creatorBalanceBefore = await mockUSDT.balanceOf(creator.address);
      await royaltyDistribution.connect(creator).claimCreatorRoyalties();
      const creatorBalanceAfter = await mockUSDT.balanceOf(creator.address);

      expect(creatorBalanceAfter.sub(creatorBalanceBefore)).to.equal(ethers.utils.parseEther("10"));
    });

    it("Should allow investors to claim royalties", async function () {
      const revenueAmount = ethers.utils.parseEther("50");
      
      await royaltyDistribution.connect(owner).receiveRevenue(campaignId, revenueAmount);
      await royaltyDistribution.distributeRoyalties(campaignId);

      const investor1BalanceBefore = await mockUSDT.balanceOf(investor1.address);
      await royaltyDistribution.connect(investor1).claimInvestorRoyalties();
      const investor1BalanceAfter = await mockUSDT.balanceOf(investor1.address);

      // Investor 1 should get 30% of remaining 37.5 USDT (after platform and creator fees)
      const expectedRoyalty = ethers.utils.parseEther("37.5").mul(3000).div(5000); // 30% of investor share
      expect(investor1BalanceAfter.sub(investor1BalanceBefore)).to.equal(expectedRoyalty);
    });
  });

  describe("Access Control", function () {
    it("Should only allow owner to create campaigns", async function () {
      await expect(
        royaltyDistribution.connect(creator).createCampaign(
          creator.address,
          ethers.utils.parseEther("100"),
          2000,
          500
        )
      ).to.be.revertedWith("Ownable: caller is not the owner");
    });

    it("Should only allow owner to add investor shares", async function () {
      const totalRaised = ethers.utils.parseEther("100");
      await royaltyDistribution.createCampaign(creator.address, totalRaised, 2000, 500);
      const campaignId = await royaltyDistribution.nextCampaignId() - 1;

      await expect(
        royaltyDistribution.connect(creator).addInvestorShare(
          campaignId,
          1,
          investor1.address,
          ethers.utils.parseEther("30")
        )
      ).to.be.revertedWith("Ownable: caller is not the owner");
    });
  });
});
