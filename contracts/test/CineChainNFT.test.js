const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("CineChainNFT", function () {
  let cineChainNFT;
  let campaignFunding;
  let mockUSDT;
  let owner;
  let creator;
  let backer1;
  let backer2;
  let platformWallet;

  const USDT_DECIMALS = 6;
  const CONTRIBUTION_AMOUNT = ethers.parseUnits("100", USDT_DECIMALS);
  const ROYALTY_PERCENTAGE = 500; // 5% in basis points
  const CAMPAIGN_ID = 1;

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

    // Deploy CineChainNFT
    const CineChainNFT = await ethers.getContractFactory("CineChainNFT");
    cineChainNFT = await CineChainNFT.deploy(
      "CineChainLanka NFTs",
      "CCLN",
      await campaignFunding.getAddress(),
      platformWallet.address
    );
    await cineChainNFT.waitForDeployment();

    // Distribute USDT to test accounts
    await mockUSDT.mint(creator.address, ethers.parseUnits("10000", USDT_DECIMALS));
    await mockUSDT.mint(backer1.address, ethers.parseUnits("10000", USDT_DECIMALS));
    await mockUSDT.mint(backer2.address, ethers.parseUnits("10000", USDT_DECIMALS));

    // Approve USDT spending
    await mockUSDT.connect(creator).approve(await campaignFunding.getAddress(), ethers.MaxUint256);
    await mockUSDT.connect(backer1).approve(await campaignFunding.getAddress(), ethers.MaxUint256);
    await mockUSDT.connect(backer2).approve(await campaignFunding.getAddress(), ethers.MaxUint256);
  });

  describe("NFT Minting", function () {
    it("Should mint NFT successfully", async function () {
      const metadataURI = "https://ipfs.io/ipfs/QmTest123";
      
      const tx = await cineChainNFT.connect(owner).mintNFT(
        backer1.address,
        CAMPAIGN_ID,
        CONTRIBUTION_AMOUNT,
        metadataURI,
        ROYALTY_PERCENTAGE
      );

      await expect(tx)
        .to.emit(cineChainNFT, "NFTCreated")
        .withArgs(1, CAMPAIGN_ID, backer1.address, backer1.address, CONTRIBUTION_AMOUNT, metadataURI);

      // Check NFT data
      const nftData = await cineChainNFT.getNFTData(1);
      expect(nftData.campaignId).to.equal(CAMPAIGN_ID);
      expect(nftData.creator).to.equal(backer1.address);
      expect(nftData.owner).to.equal(backer1.address);
      expect(nftData.contributionAmount).to.equal(CONTRIBUTION_AMOUNT);
      expect(nftData.royaltyPercentage).to.equal(ROYALTY_PERCENTAGE);
      expect(nftData.metadataURI).to.equal(metadataURI);
      expect(nftData.isTransferable).to.be.true;

      // Check ownership
      expect(await cineChainNFT.ownerOf(1)).to.equal(backer1.address);
      expect(await cineChainNFT.balanceOf(backer1.address)).to.equal(1);
    });

    it("Should reject minting with invalid parameters", async function () {
      const metadataURI = "https://ipfs.io/ipfs/QmTest123";

      await expect(
        cineChainNFT.connect(owner).mintNFT(
          ethers.ZeroAddress,
          CAMPAIGN_ID,
          CONTRIBUTION_AMOUNT,
          metadataURI,
          ROYALTY_PERCENTAGE
        )
      ).to.be.revertedWith("Invalid recipient address");

      await expect(
        cineChainNFT.connect(owner).mintNFT(
          backer1.address,
          CAMPAIGN_ID,
          0,
          metadataURI,
          ROYALTY_PERCENTAGE
        )
      ).to.be.revertedWith("Contribution amount must be greater than 0");

      await expect(
        cineChainNFT.connect(owner).mintNFT(
          backer1.address,
          CAMPAIGN_ID,
          CONTRIBUTION_AMOUNT,
          "",
          ROYALTY_PERCENTAGE
        )
      ).to.be.revertedWith("Metadata URI cannot be empty");

      await expect(
        cineChainNFT.connect(owner).mintNFT(
          backer1.address,
          CAMPAIGN_ID,
          CONTRIBUTION_AMOUNT,
          metadataURI,
          1500 // 15%
        )
      ).to.be.revertedWith("Royalty cannot exceed 10%");
    });

    it("Should only allow owner to mint NFTs", async function () {
      const metadataURI = "https://ipfs.io/ipfs/QmTest123";

      await expect(
        cineChainNFT.connect(backer1).mintNFT(
          backer1.address,
          CAMPAIGN_ID,
          CONTRIBUTION_AMOUNT,
          metadataURI,
          ROYALTY_PERCENTAGE
        )
      ).to.be.revertedWith("Ownable: caller is not the owner");
    });
  });

  describe("Batch Minting", function () {
    it("Should batch mint NFTs successfully", async function () {
      const metadataURIs = [
        "https://ipfs.io/ipfs/QmTest1",
        "https://ipfs.io/ipfs/QmTest2",
        "https://ipfs.io/ipfs/QmTest3"
      ];
      const contributionAmounts = [
        CONTRIBUTION_AMOUNT,
        CONTRIBUTION_AMOUNT * 2n,
        CONTRIBUTION_AMOUNT * 3n
      ];
      const royaltyPercentages = [500, 600, 700];

      const tx = await cineChainNFT.connect(owner).batchMintNFTs(
        backer1.address,
        CAMPAIGN_ID,
        contributionAmounts,
        metadataURIs,
        royaltyPercentages
      );

      await expect(tx)
        .to.emit(cineChainNFT, "BatchMinted")
        .withArgs(backer1.address, [1, 2, 3], CAMPAIGN_ID);

      // Check that all NFTs were minted
      expect(await cineChainNFT.balanceOf(backer1.address)).to.equal(3);
      expect(await cineChainNFT.totalSupply()).to.equal(3);

      // Check individual NFT data
      for (let i = 0; i < 3; i++) {
        const nftData = await cineChainNFT.getNFTData(i + 1);
        expect(nftData.campaignId).to.equal(CAMPAIGN_ID);
        expect(nftData.contributionAmount).to.equal(contributionAmounts[i]);
        expect(nftData.royaltyPercentage).to.equal(royaltyPercentages[i]);
        expect(nftData.metadataURI).to.equal(metadataURIs[i]);
      }
    });

    it("Should reject batch minting with mismatched array lengths", async function () {
      const metadataURIs = ["https://ipfs.io/ipfs/QmTest1", "https://ipfs.io/ipfs/QmTest2"];
      const contributionAmounts = [CONTRIBUTION_AMOUNT];
      const royaltyPercentages = [500, 600];

      await expect(
        cineChainNFT.connect(owner).batchMintNFTs(
          backer1.address,
          CAMPAIGN_ID,
          contributionAmounts,
          metadataURIs,
          royaltyPercentages
        )
      ).to.be.revertedWith("Array lengths must match");
    });
  });

  describe("NFT Transfers", function () {
    let tokenId;

    beforeEach(async function () {
      const metadataURI = "https://ipfs.io/ipfs/QmTest123";
      
      await cineChainNFT.connect(owner).mintNFT(
        backer1.address,
        CAMPAIGN_ID,
        CONTRIBUTION_AMOUNT,
        metadataURI,
        ROYALTY_PERCENTAGE
      );
      tokenId = 1;
    });

    it("Should transfer NFT when transferable", async function () {
      await cineChainNFT.connect(backer1).transferFrom(backer1.address, backer2.address, tokenId);

      expect(await cineChainNFT.ownerOf(tokenId)).to.equal(backer2.address);
      expect(await cineChainNFT.balanceOf(backer1.address)).to.equal(0);
      expect(await cineChainNFT.balanceOf(backer2.address)).to.equal(1);

      // Check that NFT data was updated
      const nftData = await cineChainNFT.getNFTData(tokenId);
      expect(nftData.owner).to.equal(backer2.address);
    });

    it("Should reject transfer when not transferable", async function () {
      // Make NFT non-transferable
      await cineChainNFT.connect(backer1).updateTransferability(tokenId, false);

      await expect(
        cineChainNFT.connect(backer1).transferFrom(backer1.address, backer2.address, tokenId)
      ).to.be.revertedWith("NFT is not transferable");
    });

    it("Should allow owner to transfer non-transferable NFT", async function () {
      // Make NFT non-transferable
      await cineChainNFT.connect(backer1).updateTransferability(tokenId, false);

      // Owner should still be able to transfer (using safeTransferFrom)
      await cineChainNFT.connect(owner).safeTransferFrom(backer1.address, backer2.address, tokenId);
      expect(await cineChainNFT.ownerOf(tokenId)).to.equal(backer2.address);
    });
  });

  describe("Royalty Management", function () {
    let tokenId;

    beforeEach(async function () {
      const metadataURI = "https://ipfs.io/ipfs/QmTest123";
      
      await cineChainNFT.connect(owner).mintNFT(
        backer1.address,
        CAMPAIGN_ID,
        CONTRIBUTION_AMOUNT,
        metadataURI,
        ROYALTY_PERCENTAGE
      );
      tokenId = 1;
    });

    it("Should update royalty percentage", async function () {
      const newRoyaltyPercentage = 800; // 8%

      const tx = await cineChainNFT.connect(backer1).updateRoyalty(tokenId, newRoyaltyPercentage);

      await expect(tx)
        .to.emit(cineChainNFT, "RoyaltyUpdated")
        .withArgs(tokenId, newRoyaltyPercentage);

      const nftData = await cineChainNFT.getNFTData(tokenId);
      expect(nftData.royaltyPercentage).to.equal(newRoyaltyPercentage);
    });

    it("Should reject invalid royalty percentage", async function () {
      await expect(
        cineChainNFT.connect(backer1).updateRoyalty(tokenId, 1500) // 15%
      ).to.be.revertedWith("Royalty cannot exceed 10%");
    });

    it("Should only allow owner or NFT owner to update royalty", async function () {
      await expect(
        cineChainNFT.connect(backer2).updateRoyalty(tokenId, 600)
      ).to.be.revertedWith("Not authorized to update royalty");
    });
  });

  describe("Transferability Management", function () {
    let tokenId;

    beforeEach(async function () {
      const metadataURI = "https://ipfs.io/ipfs/QmTest123";
      
      await cineChainNFT.connect(owner).mintNFT(
        backer1.address,
        CAMPAIGN_ID,
        CONTRIBUTION_AMOUNT,
        metadataURI,
        ROYALTY_PERCENTAGE
      );
      tokenId = 1;
    });

    it("Should update transferability", async function () {
      const tx = await cineChainNFT.connect(backer1).updateTransferability(tokenId, false);

      await expect(tx)
        .to.emit(cineChainNFT, "TransferabilityUpdated")
        .withArgs(tokenId, false);

      const nftData = await cineChainNFT.getNFTData(tokenId);
      expect(nftData.isTransferable).to.be.false;
    });

    it("Should only allow owner or NFT owner to update transferability", async function () {
      await expect(
        cineChainNFT.connect(backer2).updateTransferability(tokenId, false)
      ).to.be.revertedWith("Not authorized to update transferability");
    });
  });

  describe("Query Functions", function () {
    beforeEach(async function () {
      // Mint NFTs for different campaigns and users
      const metadataURI1 = "https://ipfs.io/ipfs/QmTest1";
      const metadataURI2 = "https://ipfs.io/ipfs/QmTest2";
      const metadataURI3 = "https://ipfs.io/ipfs/QmTest3";

      await cineChainNFT.connect(owner).mintNFT(
        backer1.address,
        1, // Campaign 1
        CONTRIBUTION_AMOUNT,
        metadataURI1,
        ROYALTY_PERCENTAGE
      );

      await cineChainNFT.connect(owner).mintNFT(
        backer1.address,
        1, // Campaign 1
        CONTRIBUTION_AMOUNT * 2n,
        metadataURI2,
        ROYALTY_PERCENTAGE
      );

      await cineChainNFT.connect(owner).mintNFT(
        backer2.address,
        2, // Campaign 2
        CONTRIBUTION_AMOUNT,
        metadataURI3,
        ROYALTY_PERCENTAGE
      );
    });

    it("Should return user NFTs", async function () {
      const userNFTs = await cineChainNFT.getUserNFTs(backer1.address);
      expect(userNFTs.length).to.equal(2);
      expect(userNFTs[0]).to.equal(1);
      expect(userNFTs[1]).to.equal(2);
    });

    it("Should return campaign NFTs", async function () {
      const campaignNFTs = await cineChainNFT.getCampaignNFTs(1);
      expect(campaignNFTs.length).to.equal(2);
      expect(campaignNFTs[0]).to.equal(1);
      expect(campaignNFTs[1]).to.equal(2);
    });

    it("Should return campaign NFT count", async function () {
      const count1 = await cineChainNFT.getCampaignNFTCount(1);
      const count2 = await cineChainNFT.getCampaignNFTCount(2);
      const count3 = await cineChainNFT.getCampaignNFTCount(3);

      expect(count1).to.equal(2);
      expect(count2).to.equal(1);
      expect(count3).to.equal(0);
    });

    it("Should return total supply", async function () {
      expect(await cineChainNFT.totalSupply()).to.equal(3);
    });
  });

  describe("Access Control", function () {
    it("Should only allow owner to update contract addresses", async function () {
      await expect(
        cineChainNFT.connect(backer1).updateCampaignFundingContract(backer2.address)
      ).to.be.revertedWith("Ownable: caller is not the owner");

      await expect(
        cineChainNFT.connect(backer1).updatePlatformWallet(backer2.address)
      ).to.be.revertedWith("Ownable: caller is not the owner");

      await expect(
        cineChainNFT.connect(backer1).updateMaxSupply(2000000)
      ).to.be.revertedWith("Ownable: caller is not the owner");
    });

    it("Should allow owner to update contract addresses", async function () {
      await cineChainNFT.connect(owner).updateCampaignFundingContract(backer2.address);
      await cineChainNFT.connect(owner).updatePlatformWallet(backer2.address);
      await cineChainNFT.connect(owner).updateMaxSupply(2000000);

      // Verify updates
      expect(await cineChainNFT.campaignFundingContract()).to.equal(backer2.address);
      expect(await cineChainNFT.platformWallet()).to.equal(backer2.address);
      expect(await cineChainNFT.maxSupply()).to.equal(2000000);
    });

    it("Should reject invalid addresses", async function () {
      await expect(
        cineChainNFT.connect(owner).updateCampaignFundingContract(ethers.ZeroAddress)
      ).to.be.revertedWith("Invalid contract address");

      await expect(
        cineChainNFT.connect(owner).updatePlatformWallet(ethers.ZeroAddress)
      ).to.be.revertedWith("Invalid wallet address");
    });

    it("Should reject max supply less than current supply", async function () {
      // Mint one NFT first
      await cineChainNFT.connect(owner).mintNFT(
        backer1.address,
        CAMPAIGN_ID,
        CONTRIBUTION_AMOUNT,
        "https://ipfs.io/ipfs/QmTest",
        ROYALTY_PERCENTAGE
      );

      await expect(
        cineChainNFT.connect(owner).updateMaxSupply(0)
      ).to.be.revertedWith("Max supply must be greater than current supply");
    });
  });

  describe("ERC2981 Royalty Standard", function () {
    let tokenId;

    beforeEach(async function () {
      const metadataURI = "https://ipfs.io/ipfs/QmTest123";
      
      await cineChainNFT.connect(owner).mintNFT(
        backer1.address,
        CAMPAIGN_ID,
        CONTRIBUTION_AMOUNT,
        metadataURI,
        ROYALTY_PERCENTAGE
      );
      tokenId = 1;
    });

    it("Should support ERC2981 interface", async function () {
      expect(await cineChainNFT.supportsInterface("0x2a55205a")).to.be.true; // ERC2981
    });

    it("Should return correct royalty info", async function () {
      const salePrice = ethers.parseEther("1"); // 1 ETH
      const royaltyInfo = await cineChainNFT.royaltyInfo(tokenId, salePrice);

      const expectedRoyalty = salePrice * BigInt(ROYALTY_PERCENTAGE) / 10000n;
      expect(royaltyInfo[0]).to.equal(backer1.address); // recipient
      expect(royaltyInfo[1]).to.equal(expectedRoyalty); // royalty amount
    });
  });
});
