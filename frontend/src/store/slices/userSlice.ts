import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import api from '../../utils/api';

interface UserProfile {
  // User model fields
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  user_type: 'creator' | 'investor' | 'admin';
  phone_number: string;
  bio: string;
  profile_picture: string;
  date_of_birth: string;
  address_line1: string;
  address_line2: string;
  city: string;
  state_province: string;
  postal_code: string;
  country: string;
  kyc_status: 'pending' | 'submitted' | 'verified' | 'rejected';
  creator_verified: boolean;
  investment_limit: number;
  created_at: string;
  updated_at: string;
  
  // UserProfile model fields
  profile_id?: number;
  website?: string;
  facebook?: string;
  twitter?: string;
  instagram?: string;
  linkedin?: string;
  occupation?: string;
  company?: string;
  experience_years?: number;
  portfolio_description?: string;
  awards?: string;
  annual_income_range?: string;
}

interface KYCRequest {
  id: number;
  user: number;
  document_type: 'national_id' | 'passport' | 'drivers_license' | 'utility_bill' | 'bank_statement';
  document_front: string;
  document_back: string;
  selfie_with_document: string;
  status: 'pending' | 'submitted' | 'verified' | 'rejected';
  rejection_reason: string;
  submitted_at: string;
  verified_at: string;
}

interface UserState {
  profile: UserProfile | null;
  kycRequests: KYCRequest[];
  isLoading: boolean;
  error: string | null;
}

const initialState: UserState = {
  profile: null,
  kycRequests: [],
  isLoading: false,
  error: null,
};

// Async thunks
export const fetchUserProfile = createAsyncThunk(
  'user/fetchUserProfile',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/api/users/profile/');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch user profile');
    }
  }
);

export const updateUserProfile = createAsyncThunk(
  'user/updateUserProfile',
  async (profileData: FormData, { rejectWithValue }) => {
    try {
      const response = await api.patch('/api/users/profile/', profileData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to update user profile');
    }
  }
);

export const fetchKYCRequests = createAsyncThunk(
  'user/fetchKYCRequests',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/api/kyc/requests/');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch KYC requests');
    }
  }
);

export const submitKYCRequest = createAsyncThunk(
  'user/submitKYCRequest',
  async (kycData: FormData, { rejectWithValue }) => {
    try {
      const response = await api.post('/api/kyc/requests/', kycData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to submit KYC request');
    }
  }
);

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setProfile: (state, action: PayloadAction<UserProfile>) => {
      state.profile = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch user profile
      .addCase(fetchUserProfile.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchUserProfile.fulfilled, (state, action) => {
        state.isLoading = false;
        state.profile = action.payload;
      })
      .addCase(fetchUserProfile.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Update user profile
      .addCase(updateUserProfile.fulfilled, (state, action) => {
        state.profile = action.payload;
      })
      // Fetch KYC requests
      .addCase(fetchKYCRequests.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchKYCRequests.fulfilled, (state, action) => {
        state.isLoading = false;
        state.kycRequests = action.payload;
      })
      .addCase(fetchKYCRequests.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Submit KYC request
      .addCase(submitKYCRequest.fulfilled, (state, action) => {
        state.kycRequests.unshift(action.payload);
      });
  },
});

export const { clearError, setProfile } = userSlice.actions;
export default userSlice.reducer;

