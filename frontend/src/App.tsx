import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './store/store';
import { useAppSelector, useAppDispatch } from './store/hooks';
import { fetchUserProfile } from './store/slices/userSlice';
import { Web3Provider } from './contexts/Web3Context';
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';
import Home from './pages/Home';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import Dashboard from './pages/Dashboard';
import Campaigns from './pages/Campaigns';
import CampaignDetail from './pages/CampaignDetail';
import CreateCampaign from './pages/CreateCampaign';
import Profile from './pages/Profile';
import KYC from './pages/KYC';
import AdminDashboard from './pages/admin/AdminDashboard';
import Analytics from './pages/Analytics';
import NFTMarketplace from './pages/marketplace/NFTMarketplace';
import ProtectedRoute from './components/auth/ProtectedRoute';
import './i18n';

// Inner component that has access to Redux hooks
const AppContent: React.FC = () => {
  const dispatch = useAppDispatch();
  const { isAuthenticated, user } = useAppSelector((state) => state.auth);

  // Load user profile on app initialization if authenticated but no user data
  useEffect(() => {
    if (isAuthenticated && !user) {
      dispatch(fetchUserProfile());
    }
  }, [dispatch, isAuthenticated, user]);

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/campaigns" element={<Campaigns />} />
            <Route path="/campaigns/:id" element={<CampaignDetail />} />
            
            {/* Protected Routes */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/create-campaign" element={
              <ProtectedRoute>
                <CreateCampaign />
              </ProtectedRoute>
            } />
            <Route path="/campaigns/:id/edit" element={
              <ProtectedRoute>
                <CreateCampaign />
              </ProtectedRoute>
            } />
            <Route path="/profile" element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } />
            <Route path="/kyc" element={
              <ProtectedRoute>
                <KYC />
              </ProtectedRoute>
            } />
            <Route path="/admin" element={
              <ProtectedRoute>
                <AdminDashboard />
              </ProtectedRoute>
            } />
            
            {/* Analytics Routes */}
            <Route path="/analytics" element={
              <ProtectedRoute>
                <Analytics />
              </ProtectedRoute>
            } />
            
            {/* Marketplace Routes */}
            <Route path="/marketplace" element={
              <ProtectedRoute>
                <NFTMarketplace />
              </ProtectedRoute>
            } />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
};

function App() {
  return (
    <Provider store={store}>
      <Web3Provider>
        <AppContent />
      </Web3Provider>
    </Provider>
  );
}

export default App;
