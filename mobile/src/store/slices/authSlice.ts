import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE_URL } from '../../config/api';

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  is_verified: boolean;
  kyc_status: string;
}

interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  error: string | null;
}

const initialState: AuthState = {
  isAuthenticated: false,
  isLoading: true,
  user: null,
  accessToken: null,
  refreshToken: null,
  error: null,
};

// Async thunks
export const login = createAsyncThunk(
  'auth/login',
  async (credentials: { email: string; password: string }, { rejectWithValue }) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        const errorData = await response.json();
        return rejectWithValue(errorData.detail || 'Login failed');
      }

      const data = await response.json();
      
      // Store tokens
      await AsyncStorage.setItem('access_token', data.access);
      await AsyncStorage.setItem('refresh_token', data.refresh);
      
      return data;
    } catch (error) {
      return rejectWithValue('Network error');
    }
  }
);

export const register = createAsyncThunk(
  'auth/register',
  async (userData: {
    username: string;
    email: string;
    password: string;
    first_name: string;
    last_name: string;
  }, { rejectWithValue }) => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        return rejectWithValue(errorData.detail || 'Registration failed');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      return rejectWithValue('Network error');
    }
  }
);

export const checkAuthStatus = createAsyncThunk(
  'auth/checkAuthStatus',
  async (_, { rejectWithValue }) => {
    try {
      const accessToken = await AsyncStorage.getItem('access_token');
      const refreshToken = await AsyncStorage.getItem('refresh_token');

      if (!accessToken || !refreshToken) {
        return rejectWithValue('No tokens found');
      }

      // Verify token with backend
      const response = await fetch(`${API_BASE_URL}/auth/user/`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        // Try to refresh token
        const refreshResponse = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ refresh: refreshToken }),
        });

        if (!refreshResponse.ok) {
          // Clear invalid tokens
          await AsyncStorage.removeItem('access_token');
          await AsyncStorage.removeItem('refresh_token');
          return rejectWithValue('Token refresh failed');
        }

        const refreshData = await refreshResponse.json();
        await AsyncStorage.setItem('access_token', refreshData.access);
        
        // Retry with new token
        const retryResponse = await fetch(`${API_BASE_URL}/auth/user/`, {
          headers: {
            'Authorization': `Bearer ${refreshData.access}`,
          },
        });

        if (!retryResponse.ok) {
          return rejectWithValue('Authentication failed');
        }

        const userData = await retryResponse.json();
        return { user: userData, accessToken: refreshData.access, refreshToken };
      }

      const userData = await response.json();
      return { user: userData, accessToken, refreshToken };
    } catch (error) {
      return rejectWithValue('Network error');
    }
  }
);

export const logout = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      // Clear tokens
      await AsyncStorage.removeItem('access_token');
      await AsyncStorage.removeItem('refresh_token');
      return true;
    } catch (error) {
      return rejectWithValue('Logout failed');
    }
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.accessToken = action.payload.access;
        state.refreshToken = action.payload.refresh;
        state.user = action.payload.user;
        state.error = null;
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = false;
        state.error = action.payload as string;
      })
      // Register
      .addCase(register.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state) => {
        state.isLoading = false;
        state.error = null;
      })
      .addCase(register.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Check Auth Status
      .addCase(checkAuthStatus.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(checkAuthStatus.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.accessToken = action.payload.accessToken;
        state.refreshToken = action.payload.refreshToken;
        state.error = null;
      })
      .addCase(checkAuthStatus.rejected, (state) => {
        state.isLoading = false;
        state.isAuthenticated = false;
        state.user = null;
        state.accessToken = null;
        state.refreshToken = null;
      })
      // Logout
      .addCase(logout.fulfilled, (state) => {
        state.isAuthenticated = false;
        state.user = null;
        state.accessToken = null;
        state.refreshToken = null;
        state.error = null;
      });
  },
});

export const { clearError } = authSlice.actions;
export default authSlice.reducer;
