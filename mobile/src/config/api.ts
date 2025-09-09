// API Configuration
export const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000/api' 
  : 'https://api.cinechainlanka.com/api';

export const API_ENDPOINTS = {
  // Auth
  LOGIN: '/auth/login/',
  REGISTER: '/auth/register/',
  REFRESH_TOKEN: '/auth/token/refresh/',
  USER_PROFILE: '/auth/user/',
  LOGOUT: '/auth/logout/',
  
  // Campaigns
  CAMPAIGNS: '/campaigns/',
  CAMPAIGN_DETAIL: (id: number) => `/campaigns/${id}/`,
  CREATE_CAMPAIGN: '/campaigns/',
  UPDATE_CAMPAIGN: (id: number) => `/campaigns/${id}/`,
  DELETE_CAMPAIGN: (id: number) => `/campaigns/${id}/`,
  
  // Payments
  CONTRIBUTE: '/payments/contribute/',
  TRANSACTIONS: '/payments/transactions/',
  PAYMENT_METHODS: '/payments/methods/',
  
  // Analytics
  CREATOR_ANALYTICS: '/revenue/analytics/creator/',
  INVESTOR_PORTFOLIO: '/revenue/portfolio/',
  REVENUE_TRENDS: '/revenue/analytics/trends/',
  
  // Marketplace
  NFT_LISTINGS: '/marketplace/listings/',
  NFT_DETAIL: (id: number) => `/marketplace/listings/${id}/`,
  CREATE_LISTING: '/marketplace/listings/',
  PLACE_BID: '/marketplace/bids/',
  
  // Web3
  WALLET_CONNECT: '/blockchain/wallets/connect/',
  WALLET_BALANCE: (id: number) => `/blockchain/wallets/${id}/balance/`,
  NFT_MINT: '/blockchain/nfts/create_nft/',
  NFT_TRANSFER: (id: number) => `/blockchain/nfts/${id}/transfer/`,
  
  // KYC
  KYC_SUBMIT: '/kyc/requests/',
  KYC_STATUS: '/kyc/requests/',
  
  // Notifications
  NOTIFICATIONS: '/notifications/',
  MARK_READ: (id: number) => `/notifications/${id}/mark_read/`,
};

export const API_TIMEOUT = 10000; // 10 seconds

export const API_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
};
