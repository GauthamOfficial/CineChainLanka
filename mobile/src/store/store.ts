import { configureStore } from '@reduxjs/toolkit';
import authSlice from './slices/authSlice';
import campaignSlice from './slices/campaignSlice';
import userSlice from './slices/userSlice';
import paymentSlice from './slices/paymentSlice';
import web3Slice from './slices/web3Slice';
import analyticsSlice from './slices/analyticsSlice';

export const store = configureStore({
  reducer: {
    auth: authSlice,
    campaigns: campaignSlice,
    user: userSlice,
    payments: paymentSlice,
    web3: web3Slice,
    analytics: analyticsSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
