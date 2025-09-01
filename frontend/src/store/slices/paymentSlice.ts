import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import api from '../../utils/api';

interface PaymentMethod {
  id: number;
  name: string;
  payment_type: string;
  description: string;
  processing_fee_percentage: number;
  processing_fee_fixed: number;
  minimum_amount: number;
  maximum_amount: number;
  is_active: boolean;
}

interface Transaction {
  id: number;
  campaign: {
    id: number;
    title: string;
    cover_image: string;
  };
  backer: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
  };
  amount: number;
  payment_method: PaymentMethod;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'refunded';
  transaction_id: string;
  created_at: string;
  updated_at: string;
}

interface PaymentState {
  paymentMethods: PaymentMethod[];
  transactions: Transaction[];
  currentTransaction: Transaction | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: PaymentState = {
  paymentMethods: [],
  transactions: [],
  currentTransaction: null,
  isLoading: false,
  error: null,
};

// Async thunks
export const fetchPaymentMethods = createAsyncThunk(
  'payments/fetchPaymentMethods',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/api/payments/methods/');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch payment methods');
    }
  }
);

export const fetchTransactions = createAsyncThunk(
  'payments/fetchTransactions',
  async (params: { page?: number; status?: string }, { rejectWithValue }) => {
    try {
      const response = await api.get('/api/payments/transactions/', { params });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch transactions');
    }
  }
);

export const createTransaction = createAsyncThunk(
  'payments/createTransaction',
  async (transactionData: {
    campaign_id: number;
    amount: number;
    payment_method_id: number;
    payment_details: any;
  }, { rejectWithValue }) => {
    try {
      const response = await api.post('/api/payments/transactions/', transactionData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to create transaction');
    }
  }
);

export const processPayment = createAsyncThunk(
  'payments/processPayment',
  async (transactionId: number, { rejectWithValue }) => {
    try {
      const response = await api.post(`/api/payments/transactions/${transactionId}/process/`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || 'Failed to process payment');
    }
  }
);

const paymentSlice = createSlice({
  name: 'payments',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setCurrentTransaction: (state, action: PayloadAction<Transaction | null>) => {
      state.currentTransaction = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch payment methods
      .addCase(fetchPaymentMethods.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchPaymentMethods.fulfilled, (state, action) => {
        state.isLoading = false;
        state.paymentMethods = action.payload;
      })
      .addCase(fetchPaymentMethods.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Fetch transactions
      .addCase(fetchTransactions.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchTransactions.fulfilled, (state, action) => {
        state.isLoading = false;
        state.transactions = action.payload.results;
      })
      .addCase(fetchTransactions.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Create transaction
      .addCase(createTransaction.fulfilled, (state, action) => {
        state.transactions.unshift(action.payload);
        state.currentTransaction = action.payload;
      })
      // Process payment
      .addCase(processPayment.fulfilled, (state, action) => {
        const index = state.transactions.findIndex(t => t.id === action.payload.id);
        if (index !== -1) {
          state.transactions[index] = action.payload;
        }
        if (state.currentTransaction?.id === action.payload.id) {
          state.currentTransaction = action.payload;
        }
      });
  },
});

export const { clearError, setCurrentTransaction } = paymentSlice.actions;
export default paymentSlice.reducer;

