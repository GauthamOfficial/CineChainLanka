const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("Starting CineChainLanka contracts deployment...");

  // Get the deployer account
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with the account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());

  // Deploy USDT mock token for testing (only on testnets)
  const network = await ethers.provider.getNetwork();
  let usdtTokenAddress;
  
  if (network.chainId === 1337 || network.chainId === 80001 || network.chainId === 5) {
    // Deploy mock USDT for local/testnet
    console.log("Deploying MockUSDT...");
    const MockUSDT = await ethers.getContractFactory("MockUSDT");
    const mockUSDT = await MockUSDT.deploy();
    await mockUSDT.deployed();
    usdtTokenAddress = mockUSDT.address;
    console.log("MockUSDT deployed to:", usdtTokenAddress);
  } else {
    // Use real USDT address for mainnet
    usdtTokenAddress = "0xdAC17F958D2ee523a2206206994597C13D831ec7"; // USDT on Ethereum
    console.log("Using existing USDT address:", usdtTokenAddress);
  }

  // Deploy CampaignFunding contract
  console.log("Deploying CampaignFunding...");
  const CampaignFunding = await ethers.getContractFactory("CampaignFunding");
  const campaignFunding = await CampaignFunding.deploy(
    usdtTokenAddress,
    deployer.address // Platform wallet
  );
  await campaignFunding.deployed();
  console.log("CampaignFunding deployed to:", campaignFunding.address);

  // Deploy CineChainNFT contract
  console.log("Deploying CineChainNFT...");
  const CineChainNFT = await ethers.getContractFactory("CineChainNFT");
  const cineChainNFT = await CineChainNFT.deploy(
    "CineChainLanka NFTs",
    "CCLN",
    campaignFunding.address,
    deployer.address // Platform wallet
  );
  await cineChainNFT.deployed();
  console.log("CineChainNFT deployed to:", cineChainNFT.address);

  // Verify contracts on block explorer (if not local)
  if (network.chainId !== 1337) {
    console.log("Waiting for block confirmations...");
    await campaignFunding.deployTransaction.wait(6);
    await cineChainNFT.deployTransaction.wait(6);

    try {
      console.log("Verifying CampaignFunding...");
      await hre.run("verify:verify", {
        address: campaignFunding.address,
        constructorArguments: [usdtTokenAddress, deployer.address],
      });
    } catch (error) {
      console.log("CampaignFunding verification failed:", error.message);
    }

    try {
      console.log("Verifying CineChainNFT...");
      await hre.run("verify:verify", {
        address: cineChainNFT.address,
        constructorArguments: [
          "CineChainLanka NFTs",
          "CCLN",
          campaignFunding.address,
          deployer.address,
        ],
      });
    } catch (error) {
      console.log("CineChainNFT verification failed:", error.message);
    }
  }

  // Save deployment info
  const deploymentInfo = {
    network: network.name,
    chainId: network.chainId,
    deployer: deployer.address,
    contracts: {
      CampaignFunding: {
        address: campaignFunding.address,
        transactionHash: campaignFunding.deployTransaction.hash,
      },
      CineChainNFT: {
        address: cineChainNFT.address,
        transactionHash: cineChainNFT.deployTransaction.hash,
      },
      USDT: {
        address: usdtTokenAddress,
        isMock: network.chainId === 1337 || network.chainId === 80001 || network.chainId === 5,
      },
    },
    timestamp: new Date().toISOString(),
  };

  const deploymentsDir = path.join(__dirname, "..", "deployments");
  
  if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir, { recursive: true });
  }

  const deploymentFile = path.join(
    deploymentsDir,
    `${network.name}-${network.chainId}.json`
  );
  
  fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));
  console.log("Deployment info saved to:", deploymentFile);

  console.log("\n=== Deployment Summary ===");
  console.log("Network:", network.name, `(${network.chainId})`);
  console.log("CampaignFunding:", campaignFunding.address);
  console.log("CineChainNFT:", cineChainNFT.address);
  console.log("USDT Token:", usdtTokenAddress);
  console.log("Platform Wallet:", deployer.address);
  console.log("\nDeployment completed successfully!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
