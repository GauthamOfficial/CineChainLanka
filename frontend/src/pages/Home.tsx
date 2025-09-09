import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAppSelector, useAppDispatch } from '../store/hooks';
import { fetchCampaigns } from '../store/slices/campaignSlice';
import { 
  FilmIcon, 
  CurrencyDollarIcon, 
  ShieldCheckIcon, 
  GlobeAltIcon,
  PlayIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';

const Home: React.FC = () => {
  const { t } = useTranslation();
  const dispatch = useAppDispatch();
  const { campaigns, isLoading } = useAppSelector((state) => state.campaigns);

  useEffect(() => {
    dispatch(fetchCampaigns({ page: 1, status: 'active' }));
  }, [dispatch]);

  // Ensure campaigns is always an array
  const safeCampaigns = Array.isArray(campaigns) ? campaigns : [];
  const featuredCampaigns = safeCampaigns.slice(0, 3);

  const features = [
    {
      icon: FilmIcon,
      title: t('campaigns.title'),
      description: 'Support independent filmmakers and content creators in Sri Lanka through transparent crowdfunding.',
    },
    {
      icon: CurrencyDollarIcon,
      title: 'Secure Payments',
      description: 'Multiple local payment methods including LankaQR, eZ Cash, and FriMi for easy transactions.',
    },
    {
      icon: ShieldCheckIcon,
      title: 'KYC Verified',
      description: 'All users undergo Know Your Customer verification for security and compliance.',
    },
    {
      icon: GlobeAltIcon,
      title: 'Blockchain Ready',
      description: 'Built on blockchain technology for transparency and automated royalty distribution.',
    },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-900 via-primary-800 to-primary-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Transform Film Funding
              <span className="block text-primary-200">in Sri Lanka</span>
            </h1>
            <p className="text-xl md:text-2xl text-primary-100 mb-8 max-w-3xl mx-auto">
              Join the revolution in content creation. Fund films, documentaries, and web series 
              through our blockchain-powered platform with transparent, secure, and automated processes.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/campaigns"
                className="bg-white text-primary-700 hover:bg-primary-50 px-8 py-3 rounded-lg font-semibold text-lg flex items-center justify-center"
              >
                <PlayIcon className="h-5 w-5 mr-2" />
                Explore Campaigns
              </Link>
              <Link
                to="/register"
                className="border-2 border-white text-white hover:bg-white hover:text-primary-700 px-8 py-3 rounded-lg font-semibold text-lg transition-colors"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </section>


      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Why Choose CineChainLanka?
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Our platform combines the best of traditional crowdfunding with cutting-edge blockchain technology.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="text-center">
                <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <feature.icon className="h-8 w-8 text-primary-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Campaigns Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Featured Campaigns
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Discover amazing projects that need your support to come to life.
            </p>
          </div>

          {isLoading ? (
            <div className="flex justify-center">
              <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {featuredCampaigns.map((campaign) => (
                <div key={campaign.id} className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
                  <div className="relative">
                    <img
                      src={campaign.cover_image}
                      alt={campaign.title}
                      className="w-full h-48 object-cover"
                    />
                    <div className="absolute top-4 left-4">
                      <span className="bg-primary-600 text-white px-2 py-1 rounded-full text-xs font-medium">
                        {campaign.category.name}
                      </span>
                    </div>
                  </div>
                  <div className="p-6">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      {campaign.title}
                    </h3>
                    <p className="text-gray-600 mb-4 line-clamp-2">
                      {campaign.short_description}
                    </p>
                    
                    {/* Funding Progress */}
                    <div className="mb-4">
                      <div className="flex justify-between text-sm text-gray-600 mb-1">
                        <span>Raised: LKR {campaign.current_funding.toLocaleString()}</span>
                        <span>Goal: LKR {campaign.funding_goal.toLocaleString()}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-primary-600 h-2 rounded-full"
                          style={{
                            width: `${Math.min((campaign.current_funding / campaign.funding_goal) * 100, 100)}%`,
                          }}
                        ></div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="text-sm text-gray-500">
                        by {campaign.creator.first_name} {campaign.creator.last_name}
                      </div>
                      <Link
                        to={`/campaigns/${campaign.id}`}
                        className="text-primary-600 hover:text-primary-700 font-medium flex items-center"
                      >
                        View Details
                        <ArrowRightIcon className="h-4 w-4 ml-1" />
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="text-center mt-12">
            <Link
              to="/campaigns"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
            >
              View All Campaigns
              <ArrowRightIcon className="ml-2 h-5 w-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to Make a Difference?
          </h2>
          <p className="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
            Join thousands of creators and backers who are already using CineChainLanka 
            to bring amazing stories to life.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="bg-white text-primary-700 hover:bg-primary-50 px-8 py-3 rounded-lg font-semibold text-lg"
            >
              Start Your Journey
            </Link>
            <Link
              to="/campaigns"
              className="border-2 border-white text-white hover:bg-white hover:text-primary-700 px-8 py-3 rounded-lg font-semibold text-lg transition-colors"
            >
              Explore Projects
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
