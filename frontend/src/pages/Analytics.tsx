import React, { useState } from 'react';
import { useAppSelector } from '../store/hooks';
import CreatorAnalytics from '../components/analytics/CreatorAnalytics';
import InvestorAnalytics from '../components/analytics/InvestorAnalytics';
import {
  ChartBarIcon,
  UserGroupIcon,
  CurrencyDollarIcon,
  ArrowTrendingUpIcon
} from '@heroicons/react/24/outline';

const Analytics: React.FC = () => {
  const { user } = useAppSelector((state) => state.auth);
  const [activeTab, setActiveTab] = useState<'creator' | 'investor'>('creator');

  // Determine user role and available tabs
  const isCreator = user?.user_type === 'creator' || user?.user_type === 'admin';
  const isInvestor = user?.user_type === 'investor' || user?.user_type === 'admin';

  const tabs = [
    ...(isCreator ? [{
      id: 'creator',
      name: 'Creator Analytics',
      icon: ChartBarIcon,
      description: 'Campaign performance and revenue analytics'
    }] : []),
    ...(isInvestor ? [{
      id: 'investor',
      name: 'Investment Portfolio',
      icon: UserGroupIcon,
      description: 'Investment performance and royalty tracking'
    }] : [])
  ];

  if (tabs.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <ChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No analytics available</h3>
            <p className="mt-1 text-sm text-gray-500">
              You need to be a creator or investor to view analytics.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Track your campaign performance and investment returns
          </p>
        </div>

        {/* Tab Navigation */}
        {tabs.length > 1 && (
          <div className="mb-8">
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex space-x-8">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id as 'creator' | 'investor')}
                      className={`${
                        activeTab === tab.id
                          ? 'border-primary-500 text-primary-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center`}
                    >
                      <Icon className="h-5 w-5 mr-2" />
                      {tab.name}
                    </button>
                  );
                })}
              </nav>
            </div>
            <div className="mt-4">
              <p className="text-sm text-gray-600">
                {tabs.find(tab => tab.id === activeTab)?.description}
              </p>
            </div>
          </div>
        )}

        {/* Analytics Content */}
        <div className="bg-white rounded-lg shadow">
          {activeTab === 'creator' && isCreator && <CreatorAnalytics />}
          {activeTab === 'investor' && isInvestor && <InvestorAnalytics />}
        </div>

        {/* Quick Stats Overview */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Campaigns</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {isCreator ? '12' : '0'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CurrencyDollarIcon className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Revenue</p>
                <p className="text-2xl font-semibold text-gray-900">
                  ${isCreator ? '125,000' : '0'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UserGroupIcon className="h-8 w-8 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Backers</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {isCreator ? '1,250' : '0'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ArrowTrendingUpIcon className="h-8 w-8 text-orange-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Average ROI</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {isInvestor ? '15.2%' : '0%'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="mt-8 bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
          </div>
          <div className="px-6 py-4">
            <div className="flow-root">
              <ul className="-mb-8">
                <li>
                  <div className="relative pb-8">
                    <div className="relative flex space-x-3">
                      <div>
                        <span className="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center ring-8 ring-white">
                          <CurrencyDollarIcon className="h-5 w-5 text-white" />
                        </span>
                      </div>
                      <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                        <div>
                          <p className="text-sm text-gray-500">
                            New revenue received from <span className="font-medium text-gray-900">Netflix</span>
                          </p>
                        </div>
                        <div className="text-right text-sm whitespace-nowrap text-gray-500">
                          <time>2 hours ago</time>
                        </div>
                      </div>
                    </div>
                  </div>
                </li>
                <li>
                  <div className="relative pb-8">
                    <div className="relative flex space-x-3">
                      <div>
                        <span className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center ring-8 ring-white">
                          <UserGroupIcon className="h-5 w-5 text-white" />
                        </span>
                      </div>
                      <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                        <div>
                          <p className="text-sm text-gray-500">
                            New backer joined <span className="font-medium text-gray-900">Shadows of Tomorrow</span>
                          </p>
                        </div>
                        <div className="text-right text-sm whitespace-nowrap text-gray-500">
                          <time>4 hours ago</time>
                        </div>
                      </div>
                    </div>
                  </div>
                </li>
                <li>
                  <div className="relative">
                    <div className="relative flex space-x-3">
                      <div>
                        <span className="h-8 w-8 rounded-full bg-purple-500 flex items-center justify-center ring-8 ring-white">
                          <ArrowTrendingUpIcon className="h-5 w-5 text-white" />
                        </span>
                      </div>
                      <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                        <div>
                          <p className="text-sm text-gray-500">
                            Royalty distribution completed for <span className="font-medium text-gray-900">3 campaigns</span>
                          </p>
                        </div>
                        <div className="text-right text-sm whitespace-nowrap text-gray-500">
                          <time>1 day ago</time>
                        </div>
                      </div>
                    </div>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
