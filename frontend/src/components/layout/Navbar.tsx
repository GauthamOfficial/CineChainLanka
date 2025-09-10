import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../../store/hooks';
import { logout } from '../../store/slices/authSlice';
import LanguageSwitcher from '../common/LanguageSwitcher';
import WalletConnection from '../blockchain/WalletConnection';
import { 
  Bars3Icon, 
  XMarkIcon, 
  UserCircleIcon,
  FilmIcon,
  HomeIcon,
  PlusCircleIcon,
  UserGroupIcon,
  Cog6ToothIcon,
  ChartBarIcon,
  CurrencyDollarIcon,
  ShoppingBagIcon
} from '@heroicons/react/24/outline';

const Navbar: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { isAuthenticated, user } = useAppSelector((state) => state.auth);
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  // Debug log to check authentication state
  console.log('Navbar - isAuthenticated:', isAuthenticated, 'user:', user);

  const handleLogout = async () => {
    await dispatch(logout());
    navigate('/');
  };


  const navigation = [
    { name: 'Home', href: '/', icon: HomeIcon },
    { name: 'Campaigns', href: '/campaigns', icon: FilmIcon },
    { name: 'Marketplace', href: '/marketplace', icon: ShoppingBagIcon },
  ];

  const authenticatedNavigation = [
    { name: 'Dashboard', href: '/dashboard', icon: UserCircleIcon },
    { name: 'Create Campaign', href: '/create-campaign', icon: PlusCircleIcon },
    { name: 'Profile', href: '/profile', icon: UserGroupIcon },
  ];

  const analyticsNavigation = [
    { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
  ];

  const adminNavigation = [
    { name: 'Admin', href: '/admin', icon: Cog6ToothIcon },
  ];

  return (
    <nav className="bg-white shadow-lg border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <FilmIcon className="h-8 w-8 text-primary-600" />
              <span className="text-xl font-bold text-gray-900">CineChainLanka</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center space-x-4">
            {/* Main Navigation */}
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className="text-gray-700 hover:text-primary-600 hover:bg-gray-50 px-3 py-2 rounded-lg text-sm font-medium flex items-center transition-colors"
              >
                <item.icon className="h-4 w-4 mr-2" />
                {item.name}
              </Link>
            ))}

            {/* User Navigation - Only show when authenticated */}
            {isAuthenticated && (
              <>
                {authenticatedNavigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className="text-gray-700 hover:text-primary-600 hover:bg-gray-50 px-3 py-2 rounded-lg text-sm font-medium flex items-center transition-colors"
                  >
                    <item.icon className="h-4 w-4 mr-2" />
                    {item.name}
                  </Link>
                ))}

                {analyticsNavigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className="text-gray-700 hover:text-primary-600 hover:bg-gray-50 px-3 py-2 rounded-lg text-sm font-medium flex items-center transition-colors"
                  >
                    <item.icon className="h-4 w-4 mr-2" />
                    {item.name}
                  </Link>
                ))}

                {user?.user_type === 'admin' && adminNavigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className="text-gray-700 hover:text-primary-600 hover:bg-gray-50 px-3 py-2 rounded-lg text-sm font-medium flex items-center transition-colors"
                  >
                    <item.icon className="h-4 w-4 mr-2" />
                    {item.name}
                  </Link>
                ))}
              </>
            )}

            {/* Right Side Actions */}
            <div className="flex items-center space-x-2 pl-4 border-l border-gray-200">
              <LanguageSwitcher />
              <WalletConnection />
              
              {isAuthenticated ? (
                <>
                  <span className="text-sm text-gray-600">
                    Welcome, {user?.first_name || user?.username}
                  </span>
                  <button
                    onClick={handleLogout}
                    className="bg-red-50 hover:bg-red-100 text-red-700 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
                  >
                    Login
                  </Link>
                  <Link
                    to="/register"
                    className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                  >
                    Register
                  </Link>
                </>
              )}
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="lg:hidden flex items-center">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="inline-flex items-center justify-center p-2 rounded-lg text-gray-700 hover:text-primary-600 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500 transition-colors"
            >
              {isOpen ? (
                <XMarkIcon className="block h-6 w-6" />
              ) : (
                <Bars3Icon className="block h-6 w-6" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isOpen && (
        <div className="lg:hidden">
          <div className="px-4 py-4 space-y-2 bg-white border-t border-gray-200">
            {/* Main Navigation */}
            <div className="space-y-1">
              <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Main Navigation
              </div>
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className="text-gray-700 hover:text-primary-600 hover:bg-gray-50 block px-3 py-2 rounded-lg text-sm font-medium flex items-center transition-colors"
                  onClick={() => setIsOpen(false)}
                >
                  <item.icon className="h-4 w-4 mr-3" />
                  {item.name}
                </Link>
              ))}
            </div>

            {/* User Navigation */}
            {isAuthenticated && (
              <div className="space-y-1">
                <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Account
                </div>
                {authenticatedNavigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className="text-gray-700 hover:text-primary-600 hover:bg-gray-50 block px-3 py-2 rounded-lg text-sm font-medium flex items-center transition-colors"
                    onClick={() => setIsOpen(false)}
                  >
                    <item.icon className="h-4 w-4 mr-3" />
                    {item.name}
                  </Link>
                ))}

                {analyticsNavigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className="text-gray-700 hover:text-primary-600 hover:bg-gray-50 block px-3 py-2 rounded-lg text-sm font-medium flex items-center transition-colors"
                    onClick={() => setIsOpen(false)}
                  >
                    <item.icon className="h-4 w-4 mr-3" />
                    {item.name}
                  </Link>
                ))}

                {user?.user_type === 'admin' && adminNavigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className="text-gray-700 hover:text-primary-600 hover:bg-gray-50 block px-3 py-2 rounded-lg text-sm font-medium flex items-center transition-colors"
                    onClick={() => setIsOpen(false)}
                  >
                    <item.icon className="h-4 w-4 mr-3" />
                    {item.name}
                  </Link>
                ))}
              </div>
            )}

            {/* Language Switcher for Mobile */}
            <div className="space-y-1">
              <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Language / භාෂාව / மொழி
              </div>
              <div className="px-3">
                <LanguageSwitcher onLanguageChange={() => setIsOpen(false)} />
              </div>
            </div>

            {/* Wallet Connection for Mobile */}
            <div className="space-y-1">
              <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Wallet
              </div>
              <div className="px-3">
                <WalletConnection />
              </div>
            </div>

            {/* User Actions */}
            <div className="space-y-1">
              <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Account Actions
              </div>
              {isAuthenticated ? (
                <>
                  <div className="px-3 py-2 text-sm text-gray-600">
                    Welcome, {user?.first_name || user?.username}
                  </div>
                  <button
                    onClick={() => {
                      handleLogout();
                      setIsOpen(false);
                    }}
                    className="w-full text-left text-gray-700 hover:text-red-600 hover:bg-red-50 block px-3 py-2 rounded-lg text-sm font-medium transition-colors"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <div className="px-3 space-y-2">
                  <Link
                    to="/login"
                    className="text-gray-700 hover:text-primary-600 hover:bg-gray-50 block px-3 py-2 rounded-lg text-sm font-medium transition-colors"
                    onClick={() => setIsOpen(false)}
                  >
                    Login
                  </Link>
                  <Link
                    to="/register"
                    className="bg-primary-600 hover:bg-primary-700 text-white block px-3 py-2 rounded-lg text-sm font-medium text-center transition-colors"
                    onClick={() => setIsOpen(false)}
                  >
                    Register
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
