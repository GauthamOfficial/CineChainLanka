import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import Web3 from 'web3';

interface Web3ContextType {
  account: string | null;
  chainId: number | null;
  web3: Web3 | null;
  connect: () => Promise<void>;
  disconnect: () => void;
  switchNetwork: (chainId: number) => Promise<void>;
  isConnected: boolean;
  isLoading: boolean;
  error: string | null;
}

const Web3Context = createContext<Web3ContextType | undefined>(undefined);

interface Web3ProviderProps {
  children: ReactNode;
}

export const Web3Provider: React.FC<Web3ProviderProps> = ({ children }) => {
  const [account, setAccount] = useState<string | null>(null);
  const [chainId, setChainId] = useState<number | null>(null);
  const [web3, setWeb3] = useState<Web3 | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isConnected = !!account && !!web3;

  // Check if MetaMask is installed
  const isMetaMaskInstalled = () => {
    if (typeof window === 'undefined') {
      return false;
    }
    
    // Check for MetaMask specifically
    if (window.ethereum?.isMetaMask) {
      return true;
    }
    
    // Check for MetaMask in the provider name
    if (window.ethereum?.providerMap) {
      const providers = window.ethereum.providerMap;
      if (providers.MetaMask) {
        return true;
      }
    }
    
    // Fallback check for any ethereum provider
    if (window.ethereum) {
      return true;
    }
    
    return false;
  };

  // Get the web3 instance
  const getWeb3 = () => {
    if (typeof window !== 'undefined' && window.ethereum) {
      return new Web3(window.ethereum);
    }
    return null;
  };

  // Connect to MetaMask
  const connect = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Wait for provider to be available with timeout
      const waitForProvider = (timeout = 5000) => {
        return new Promise((resolve, reject) => {
          const startTime = Date.now();
          
          const checkProvider = () => {
            if (isMetaMaskInstalled()) {
              resolve(true);
            } else if (Date.now() - startTime > timeout) {
              reject(new Error('MetaMask is not installed. Please install MetaMask browser extension to continue. Visit https://metamask.io to download and install MetaMask.'));
            } else {
              setTimeout(checkProvider, 100);
            }
          };
          
          checkProvider();
        });
      };

      await waitForProvider();

      const web3Instance = getWeb3();
      if (!web3Instance) {
        throw new Error('Web3 not available');
      }

      // Request account access
      const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
      
      if (accounts.length === 0) {
        throw new Error('No accounts found');
      }

      // Get chain ID
      const chainId = await window.ethereum.request({ method: 'eth_chainId' });

      setWeb3(web3Instance);
      setAccount(accounts[0]);
      setChainId(parseInt(chainId, 16));

      // Store connection state
      localStorage.setItem('web3_connected', 'true');
      localStorage.setItem('web3_account', accounts[0]);

    } catch (err: any) {
      setError(err.message || 'Failed to connect to MetaMask');
      console.error('Web3 connection error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Disconnect
  const disconnect = () => {
    setAccount(null);
    setChainId(null);
    setWeb3(null);
    setError(null);
    
    // Clear stored state
    localStorage.removeItem('web3_connected');
    localStorage.removeItem('web3_account');
  };

  // Switch network
  const switchNetwork = async (targetChainId: number) => {
    if (!window.ethereum) {
      throw new Error('Provider not available');
    }

    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: `0x${targetChainId.toString(16)}` }]
      });
    } catch (err: any) {
      // If the chain doesn't exist, add it
      if (err.code === 4902) {
        const chainConfig = getChainConfig(targetChainId);
        if (chainConfig) {
          await window.ethereum.request({
            method: 'wallet_addEthereumChain',
            params: [chainConfig]
          });
        } else {
          throw new Error(`Chain ${targetChainId} not supported`);
        }
      } else {
        throw err;
      }
    }
  };

  // Get chain configuration
  const getChainConfig = (chainId: number) => {
    const chainConfigs: { [key: number]: any } = {
      1: {
        chainId: '0x1',
        chainName: 'Ethereum Mainnet',
        nativeCurrency: {
          name: 'Ether',
          symbol: 'ETH',
          decimals: 18,
        },
        rpcUrls: ['https://mainnet.infura.io/v3/YOUR_PROJECT_ID'],
        blockExplorerUrls: ['https://etherscan.io'],
      },
      137: {
        chainId: '0x89',
        chainName: 'Polygon Mainnet',
        nativeCurrency: {
          name: 'MATIC',
          symbol: 'MATIC',
          decimals: 18,
        },
        rpcUrls: ['https://polygon-rpc.com'],
        blockExplorerUrls: ['https://polygonscan.com'],
      },
      80001: {
        chainId: '0x13881',
        chainName: 'Polygon Mumbai Testnet',
        nativeCurrency: {
          name: 'MATIC',
          symbol: 'MATIC',
          decimals: 18,
        },
        rpcUrls: ['https://rpc-mumbai.maticvigil.com'],
        blockExplorerUrls: ['https://mumbai.polygonscan.com'],
      },
    };

    return chainConfigs[chainId];
  };

  // Check connection on mount
  useEffect(() => {
    const checkConnection = async () => {
      // Wait a bit for the provider to be available
      const checkProvider = () => {
        if (isMetaMaskInstalled() && localStorage.getItem('web3_connected') === 'true') {
          try {
            const web3Instance = getWeb3();
            if (web3Instance) {
              return web3Instance;
            }
          } catch (err) {
            console.error('Error getting web3 instance:', err);
          }
        }
        return null;
      };

      // Try immediately
      let web3Instance = checkProvider();
      
      // If not available, try again after a short delay
      if (!web3Instance) {
        setTimeout(async () => {
          web3Instance = checkProvider();
          if (web3Instance) {
            try {
              const accounts = await window.ethereum.request({ method: 'eth_accounts' });
              if (accounts.length > 0) {
                const chainId = await window.ethereum.request({ method: 'eth_chainId' });
                
                setWeb3(web3Instance);
                setAccount(accounts[0]);
                setChainId(parseInt(chainId, 16));
              }
            } catch (err) {
              console.error('Error checking connection:', err);
              disconnect();
            }
          }
        }, 1000);
      } else {
        try {
          const accounts = await window.ethereum.request({ method: 'eth_accounts' });
          if (accounts.length > 0) {
            const chainId = await window.ethereum.request({ method: 'eth_chainId' });
            
            setWeb3(web3Instance);
            setAccount(accounts[0]);
            setChainId(parseInt(chainId, 16));
          }
        } catch (err) {
          console.error('Error checking connection:', err);
          disconnect();
        }
      }
    };

    checkConnection();
  }, []);

  // Listen for account changes
  useEffect(() => {
    if (window.ethereum) {
      const handleAccountsChanged = (accounts: string[]) => {
        if (accounts.length === 0) {
          disconnect();
        } else {
          setAccount(accounts[0]);
        }
      };

      const handleChainChanged = (chainId: string) => {
        setChainId(parseInt(chainId, 16));
      };

      window.ethereum.on('accountsChanged', handleAccountsChanged);
      window.ethereum.on('chainChanged', handleChainChanged);

      return () => {
        if (window.ethereum.removeListener) {
          window.ethereum.removeListener('accountsChanged', handleAccountsChanged);
          window.ethereum.removeListener('chainChanged', handleChainChanged);
        }
      };
    }
  }, []);

  const value: Web3ContextType = {
    account,
    chainId,
    web3,
    connect,
    disconnect,
    switchNetwork,
    isConnected,
    isLoading,
    error,
  };

  return (
    <Web3Context.Provider value={value}>
      {children}
    </Web3Context.Provider>
  );
};

export const useWeb3 = (): Web3ContextType => {
  const context = useContext(Web3Context);
  if (context === undefined) {
    throw new Error('useWeb3 must be used within a Web3Provider');
  }
  return context;
};

// Extend Window interface for TypeScript
declare global {
  interface Window {
    ethereum?: any;
  }
}
