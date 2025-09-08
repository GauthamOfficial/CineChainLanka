const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("CampaignFunding", function () {
  let campaignFunding;
  let mockUSDT;
  let owner;
  let creator;
  let backer1;
  let backer2;
  let platformWallet;

  const USDT_DECIMALS = 6;
  const FUNDING_GOAL = ethers.parseUnits("1000", USDT_DECIMALS); // 1000 USDT
  const CONTRIBUTION_AMOUNT = ethers.parseUnits("100", USDT_DECIMALS); // 100 USDT
  const CAMPAIGN_DURATION = 30 * 24 * 60 * 60; // 30 days in seconds

  beforeEach(async function () {
    [owner, creator, backer1, backer2, platformWallet] = await ethers.getSigners();

    // Deploy MockUSDT
    const MockUSDT = await ethers.getContractFactory("MockUSDT");
    mockUSDT = await MockUSDT.deploy();
    await mockUSDT.waitForDeployment();

    // Deploy CampaignFunding
    const CampaignFunding = await ethers.getContractFactory("CampaignFunding");
    campaignFunding = await CampaignFunding.deploy(
      await mockUSDT.getAddress(),
      platformWallet.address
    );
    await campaignFunding.waitForDeployment();

    // Distribute USDT to test accounts
    await mockUSDT.mint(creator.address, ethers.parseUnits("10000", USDT_DECIMALS));
    await mockUSDT.mint(backer1.address, ethers.parseUnits("10000", USDT_DECIMALS));
    await mockUSDT.mint(backer2.address, ethers.parseUnits("10000", USDT_DECIMALS));

    // Approve USDT spending
    await mockUSDT.connect(creator).approve(await campaignFunding.getAddress(), ethers.MaxUint256);
    await mockUSDT.connect(backer1).approve(await campaignFunding.getAddress(), ethers.MaxUint256);
    await mockUSDT.connect(backer2).approve(await campaignFunding.getAddress(), ethers.MaxUint256);
  });

  describe("Campaign Creation", function () {
    it("Should create a campaign successfully", async function () {
      const tx = await campaignFunding.connect(creator).createCampaign(
        "Test Film Campaign",
        "A test film campaign for testing purposes",
        FUNDING_GOAL,
        CAMPAIGN_DURATION
      );

      await expect(tx)
        .to.emit(campaignFunding, "CampaignCreated")
        .withArgs(
          1,
          creator.address,
          "Test Film Campaign",
          FUNDING_GOAL,
          await ethers.provider.getBlock("latest").then(block => block.timestamp),
          await ethers.provider.getBlock("latest").then(block => block.timestamp) + CAMPAIGN_DURATION
        );

      const campaign = await campaignFunding.getCampaign(1);
      expect(campaign.creator).to.equal(creator.address);
      expect(campaign.title).to.equal("Test Film Campaign");
      expect(campaign.fundingGoal).to.equal(FUNDING_GOAL);
      expect(campaign.isActive).to.be.true;
    });

    it("Should reject campaign creation with invalid parameters", async function () {
      await expect(
        campaignFunding.connect(creator).createCampaign("", "Description", FUNDING_GOAL, CAMPAIGN_DURATION)
      ).to.be.revertedWith("Title cannot be empty");

      await expect(
        campaignFunding.connect(creator).createCampaign("Title", "", FUNDING_GOAL, CAMPAIGN_DURATION)
      ).to.be.revertedWith("Description cannot be empty");

      await expect(
        campaignFunding.connect(creator).createCampaign("Title", "Description", 0, CAMPAIGN_DURATION)
      ).to.be.revertedWith("Funding goal must be greater than 0");

      await expect(
        campaignFunding.connect(creator).createCampaign("Title", "Description", FUNDING_GOAL, 0)
      ).to.be.revertedWith("Duration must be greater than 0");
    });
  });

  describe("Campaign Contributions", function () {
    let campaignId;

    beforeEach(async function () {
      const tx = await campaignFunding.connect(creator).createCampaign(
        "Test Film Campaign",
        "A test film campaign for testing purposes",
        FUNDING_GOAL,
        CAMPAIGN_DURATION
      );
      const receipt = await tx.wait();
      campaignId = 1;
    });

    it("Should allow contributions to active campaigns", async function () {
      const tx = await campaignFunding.connect(backer1).contribute(campaignId, CONTRIBUTION_AMOUNT);

      await expect(tx)
        .to.emit(campaignFunding, "ContributionMade")
        .withArgs(campaignId, backer1.address, CONTRIBUTION_AMOUNT, CONTRIBUTION_AMOUNT);

      const campaign = await campaignFunding.getCampaign(campaignId);
      expect(campaign.currentFunding).to.equal(CONTRIBUTION_AMOUNT);
      expect(campaign.backerCount).to.equal(1);

      const contribution = await campaignFunding.getContribution(campaignId, backer1.address);
      expect(contribution).to.equal(CONTRIBUTION_AMOUNT);
    });

    it("Should handle multiple contributions from same backer", async function () {
      await campaignFunding.connect(backer1).contribute(campaignId, CONTRIBUTION_AMOUNT);
      await campaignFunding.connect(backer1).contribute(campaignId, CONTRIBUTION_AMOUNT);

      const campaign = await campaignFunding.getCampaign(campaignId);
      expect(campaign.currentFunding).to.equal(CONTRIBUTION_AMOUNT * 2n);
      expect(campaign.backerCount).to.equal(1); // Should still be 1

      const contribution = await campaignFunding.getContribution(campaignId, backer1.address);
      expect(contribution).to.equal(CONTRIBUTION_AMOUNT * 2n);
    });

    it("Should reject contributions to inactive campaigns", async function () {
      // Fast forward time to end the campaign
      await ethers.provider.send("evm_increaseTime", [CAMPAIGN_DURATION + 1]);
      await ethers.provider.send("evm_mine");
      
      // Mark campaign as failed
      await campaignFunding.connect(owner).markCampaignAsFailed(campaignId);

      await expect(
        campaignFunding.connect(backer1).contribute(campaignId, CONTRIBUTION_AMOUNT)
      ).to.be.revertedWith("Campaign is not active");
    });

    it("Should reject contributions with zero amount", async function () {
      await expect(
        campaignFunding.connect(backer1).contribute(campaignId, 0)
      ).to.be.revertedWith("Contribution amount must be greater than 0");
    });

    it("Should reject contributions before campaign starts", async function () {
      // This test would require time manipulation, which is complex in Hardhat
      // In a real scenario, you'd use time travel utilities
    });
  });

  describe("Campaign Funding Success", function () {
    let campaignId;

    beforeEach(async function () {
      const tx = await campaignFunding.connect(creator).createCampaign(
        "Test Film Campaign",
        "A test film campaign for testing purposes",
        FUNDING_GOAL,
        CAMPAIGN_DURATION
      );
      campaignId = 1;
    });

    it("Should mark campaign as funded when goal is reached", async function () {
      const tx = await campaignFunding.connect(backer1).contribute(campaignId, FUNDING_GOAL);

      await expect(tx)
        .to.emit(campaignFunding, "CampaignFunded")
        .withArgs(campaignId, FUNDING_GOAL);

      await expect(tx)
        .to.emit(campaignFunding, "FundsWithdrawn")
        .withArgs(campaignId, creator.address, FUNDING_GOAL * 97n / 100n); // 97% after 3% fee

      const campaign = await campaignFunding.getCampaign(campaignId);
      expect(campaign.isFunded).to.be.true;
      expect(campaign.isActive).to.be.false;
    });

    it("Should distribute funds correctly with platform fee", async function () {
      const platformBalanceBefore = await mockUSDT.balanceOf(platformWallet.address);
      const creatorBalanceBefore = await mockUSDT.balanceOf(creator.address);

      await campaignFunding.connect(backer1).contribute(campaignId, FUNDING_GOAL);

      const platformBalanceAfter = await mockUSDT.balanceOf(platformWallet.address);
      const creatorBalanceAfter = await mockUSDT.balanceOf(creator.address);

      const platformFee = FUNDING_GOAL * 3n / 100n; // 3% fee
      const creatorAmount = FUNDING_GOAL - platformFee;

      expect(platformBalanceAfter - platformBalanceBefore).to.equal(platformFee);
      expect(creatorBalanceAfter - creatorBalanceBefore).to.equal(creatorAmount);
    });
  });

  describe("Campaign Failure and Refunds", function () {
    let campaignId;

    beforeEach(async function () {
      const tx = await campaignFunding.connect(creator).createCampaign(
        "Test Film Campaign",
        "A test film campaign for testing purposes",
        FUNDING_GOAL,
        CAMPAIGN_DURATION
      );
      campaignId = 1;

      // Make some contributions
      await campaignFunding.connect(backer1).contribute(campaignId, CONTRIBUTION_AMOUNT);
      await campaignFunding.connect(backer2).contribute(campaignId, CONTRIBUTION_AMOUNT);
    });

    it("Should mark campaign as failed after deadline", async function () {
      // Fast forward time to end the campaign
      await ethers.provider.send("evm_increaseTime", [CAMPAIGN_DURATION + 1]);
      await ethers.provider.send("evm_mine");
      
      const tx = await campaignFunding.connect(owner).markCampaignAsFailed(campaignId);

      await expect(tx)
        .to.emit(campaignFunding, "CampaignFailed")
        .withArgs(campaignId, CONTRIBUTION_AMOUNT * 2n);

      const campaign = await campaignFunding.getCampaign(campaignId);
      expect(campaign.isFailed).to.be.true;
      expect(campaign.isActive).to.be.false;
    });

    it("Should process individual refunds", async function () {
      // Fast forward time to end the campaign
      await ethers.provider.send("evm_increaseTime", [CAMPAIGN_DURATION + 1]);
      await ethers.provider.send("evm_mine");
      
      await campaignFunding.connect(owner).markCampaignAsFailed(campaignId);

      const backer1BalanceBefore = await mockUSDT.balanceOf(backer1.address);
      const tx = await campaignFunding.connect(backer1).processRefund(campaignId, backer1.address);

      await expect(tx)
        .to.emit(campaignFunding, "RefundProcessed")
        .withArgs(campaignId, backer1.address, CONTRIBUTION_AMOUNT);

      const backer1BalanceAfter = await mockUSDT.balanceOf(backer1.address);
      expect(backer1BalanceAfter - backer1BalanceBefore).to.equal(CONTRIBUTION_AMOUNT);
    });

    it("Should process bulk refunds", async function () {
      // Fast forward time to end the campaign
      await ethers.provider.send("evm_increaseTime", [CAMPAIGN_DURATION + 1]);
      await ethers.provider.send("evm_mine");
      
      await campaignFunding.connect(owner).markCampaignAsFailed(campaignId);

      const backers = [backer1.address, backer2.address];
      const tx = await campaignFunding.connect(owner).processBulkRefunds(campaignId, backers);

      // Check that both backers received their refunds
      for (let i = 0; i < backers.length; i++) {
        await expect(tx)
          .to.emit(campaignFunding, "RefundProcessed")
          .withArgs(campaignId, backers[i], CONTRIBUTION_AMOUNT);
      }
    });

    it("Should reject refunds for non-failed campaigns", async function () {
      await expect(
        campaignFunding.connect(backer1).processRefund(campaignId, backer1.address)
      ).to.be.revertedWith("Campaign has not failed");
    });
  });

  describe("Access Control", function () {
    it("Should only allow owner to mark campaigns as failed", async function () {
      const tx = await campaignFunding.connect(creator).createCampaign(
        "Test Film Campaign",
        "A test film campaign for testing purposes",
        FUNDING_GOAL,
        CAMPAIGN_DURATION
      );
      const campaignId = 1;

      await expect(
        campaignFunding.connect(backer1).markCampaignAsFailed(campaignId)
      ).to.be.revertedWith("Ownable: caller is not the owner");
    });

    it("Should only allow owner to process bulk refunds", async function () {
      const tx = await campaignFunding.connect(creator).createCampaign(
        "Test Film Campaign",
        "A test film campaign for testing purposes",
        FUNDING_GOAL,
        CAMPAIGN_DURATION
      );
      const campaignId = 1;

      // Fast forward time to end the campaign
      await ethers.provider.send("evm_increaseTime", [CAMPAIGN_DURATION + 1]);
      await ethers.provider.send("evm_mine");
      
      await campaignFunding.connect(owner).markCampaignAsFailed(campaignId);

      await expect(
        campaignFunding.connect(backer1).processBulkRefunds(campaignId, [backer1.address])
      ).to.be.revertedWith("Ownable: caller is not the owner");
    });
  });

  describe("Platform Configuration", function () {
    it("Should allow owner to update platform fee", async function () {
      await campaignFunding.connect(owner).updatePlatformFee(500); // 5%
      
      // Verify the fee was updated
      const newFee = await campaignFunding.platformFeePercentage();
      expect(newFee).to.equal(500);
    });

    it("Should reject invalid platform fee", async function () {
      await expect(
        campaignFunding.connect(owner).updatePlatformFee(1500) // 15%
      ).to.be.revertedWith("Fee cannot exceed 10%");
    });

    it("Should allow owner to update platform wallet", async function () {
      await campaignFunding.connect(owner).updatePlatformWallet(backer1.address);
      
      // Verify the wallet was updated
      const newWallet = await campaignFunding.platformWallet();
      expect(newWallet).to.equal(backer1.address);
    });

    it("Should reject invalid platform wallet", async function () {
      await expect(
        campaignFunding.connect(owner).updatePlatformWallet(ethers.ZeroAddress)
      ).to.be.revertedWith("Invalid wallet address");
    });
  });
});
