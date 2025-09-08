import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { createCampaign, updateCampaign, fetchCampaignById, clearError } from '../store/slices/campaignSlice';
import { 
  PhotoIcon, 
  DocumentTextIcon,
  CurrencyDollarIcon,
  CalendarIcon,
  TagIcon,
  UserIcon
} from '@heroicons/react/24/outline';

interface CampaignFormData {
  title: string;
  subtitle: string;
  description: string;
  short_description: string;
  category: string;
  funding_goal: string;
  funding_deadline: string;
  cover_image: File | null;
  rewards: Array<{
    title: string;
    description: string;
    amount: string;
    quantity: string;
  }>;
}

const CreateCampaign: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const dispatch = useAppDispatch();
  const { isLoading, error, currentCampaign } = useAppSelector((state) => state.campaigns);
  
  const isEditing = !!id;

  const [formData, setFormData] = useState<CampaignFormData>({
    title: '',
    subtitle: '',
    description: '',
    short_description: '',
    category: '',
    funding_goal: '',
    funding_deadline: '',
    cover_image: null,
    rewards: [
      {
        title: '',
        description: '',
        amount: '',
        quantity: '',
      },
    ],
  });

  const [previewImage, setPreviewImage] = useState<string | null>(null);

  const categories = [
    { id: 1, name: 'Film', icon: '🎬' },
    { id: 2, name: 'Documentary', icon: '📹' },
    { id: 3, name: 'Web Series', icon: '📺' },
    { id: 4, name: 'Short Film', icon: '🎥' },
    { id: 5, name: 'Animation', icon: '🎨' },
    { id: 6, name: 'Music Video', icon: '🎵' },
  ];

  useEffect(() => {
    return () => {
      dispatch(clearError());
    };
  }, [dispatch]);

  // Load campaign data when editing
  useEffect(() => {
    if (isEditing && id) {
      dispatch(fetchCampaignById(parseInt(id)));
    }
  }, [dispatch, isEditing, id]);

  // Populate form when editing campaign data is loaded
  useEffect(() => {
    if (isEditing && currentCampaign) {
      setFormData({
        title: currentCampaign.title || '',
        subtitle: currentCampaign.subtitle || '',
        description: currentCampaign.description || '',
        short_description: currentCampaign.short_description || '',
        category: currentCampaign.category?.id?.toString() || '',
        funding_goal: currentCampaign.funding_goal?.toString() || '',
        funding_deadline: currentCampaign.end_date ? new Date(currentCampaign.end_date).toISOString().split('T')[0] : '',
        cover_image: null, // Keep as null, user can upload new image
        rewards: currentCampaign.rewards?.map(reward => ({
          title: reward.title || '',
          description: reward.description || '',
          amount: reward.amount?.toString() || '',
          quantity: reward.max_backers?.toString() || '',
        })) || []
      });
    }
  }, [isEditing, currentCampaign]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFormData(prev => ({
        ...prev,
        cover_image: file,
      }));
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewImage(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRewardChange = (index: number, field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      rewards: prev.rewards.map((reward, i) =>
        i === index ? { ...reward, [field]: value } : reward
      ),
    }));
  };

  const addReward = () => {
    setFormData(prev => ({
      ...prev,
      rewards: [
        ...prev.rewards,
        {
          title: '',
          description: '',
          amount: '',
          quantity: '',
        },
      ],
    }));
  };

  const removeReward = (index: number) => {
    setFormData(prev => ({
      ...prev,
      rewards: prev.rewards.filter((_, i) => i !== index),
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const formDataToSend = new FormData();
    formDataToSend.append('title', formData.title);
    formDataToSend.append('subtitle', formData.subtitle);
    formDataToSend.append('description', formData.description);
    formDataToSend.append('short_description', formData.short_description);
    formDataToSend.append('category', formData.category);
    formDataToSend.append('funding_goal', formData.funding_goal);
    formDataToSend.append('end_date', formData.funding_deadline);
    
    if (formData.cover_image) {
      formDataToSend.append('cover_image', formData.cover_image);
    }

    // Add rewards
    formData.rewards.forEach((reward, index) => {
      if (reward.title && reward.description && reward.amount) {
        formDataToSend.append(`rewards[${index}][title]`, reward.title);
        formDataToSend.append(`rewards[${index}][description]`, reward.description);
        formDataToSend.append(`rewards[${index}][amount]`, reward.amount);
        formDataToSend.append(`rewards[${index}][quantity]`, reward.quantity || '0');
      }
    });

    try {
      if (isEditing && id) {
        await dispatch(updateCampaign({ id: parseInt(id), campaignData: formDataToSend })).unwrap();
      } else {
        await dispatch(createCampaign(formDataToSend)).unwrap();
      }
      navigate('/dashboard');
    } catch (error) {
      // Error is handled by the slice
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            {isEditing ? 'Edit Campaign' : 'Create New Campaign'}
          </h1>
          <p className="text-gray-600 mt-2">
            Share your creative vision and start raising funds for your project
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
              {error}
            </div>
          )}

          {/* Basic Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-6 flex items-center">
              <DocumentTextIcon className="h-5 w-5 mr-2" />
              Basic Information
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-2">
                <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
                  Campaign Title *
                </label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  required
                  value={formData.title}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Enter your campaign title"
                />
              </div>

              <div className="md:col-span-2">
                <label htmlFor="subtitle" className="block text-sm font-medium text-gray-700 mb-2">
                  Subtitle
                </label>
                <input
                  type="text"
                  id="subtitle"
                  name="subtitle"
                  value={formData.subtitle}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="A brief tagline for your campaign"
                />
              </div>

              <div className="md:col-span-2">
                <label htmlFor="short_description" className="block text-sm font-medium text-gray-700 mb-2">
                  Short Description *
                </label>
                <textarea
                  id="short_description"
                  name="short_description"
                  required
                  rows={3}
                  value={formData.short_description}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                  placeholder="Brief summary of your campaign (max 500 characters)"
                  maxLength={500}
                />
                <p className="text-sm text-gray-500 mt-1">
                  {formData.short_description.length}/500 characters
                </p>
              </div>

              <div>
                <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
                  Category *
                </label>
                <select
                  id="category"
                  name="category"
                  required
                  value={formData.category}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">Select a category</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.icon} {category.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Detailed Description */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-6 flex items-center">
              <DocumentTextIcon className="h-5 w-5 mr-2" />
              Detailed Description
            </h2>
            
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                Full Description *
              </label>
              <textarea
                id="description"
                name="description"
                required
                rows={8}
                value={formData.description}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                placeholder="Tell your story, share your vision, and explain why people should support your project..."
              />
            </div>
          </div>

          {/* Funding Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-6 flex items-center">
              <CurrencyDollarIcon className="h-5 w-5 mr-2" />
              Funding Information
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="funding_goal" className="block text-sm font-medium text-gray-700 mb-2">
                  Funding Goal (LKR) *
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-2 text-gray-500">LKR</span>
                  <input
                    type="number"
                    id="funding_goal"
                    name="funding_goal"
                    required
                    min="1000"
                    value={formData.funding_goal}
                    onChange={handleInputChange}
                    className="w-full pl-12 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    placeholder="10000"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="funding_deadline" className="block text-sm font-medium text-gray-700 mb-2">
                  Funding Deadline *
                </label>
                <input
                  type="date"
                  id="funding_deadline"
                  name="funding_deadline"
                  required
                  min={new Date().toISOString().split('T')[0]}
                  value={formData.funding_deadline}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>
          </div>

          {/* Cover Image */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-6 flex items-center">
              <PhotoIcon className="h-5 w-5 mr-2" />
              Campaign Cover Image
            </h2>
            
            <div className="space-y-4">
              <div>
                <label htmlFor="cover_image" className="block text-sm font-medium text-gray-700 mb-2">
                  Upload Cover Image
                </label>
                <input
                  type="file"
                  id="cover_image"
                  name="cover_image"
                  accept="image/*"
                  onChange={handleImageChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                />
                <p className="text-sm text-gray-500 mt-1">
                  Recommended size: 1200x800 pixels. Max file size: 5MB.
                </p>
              </div>

              {previewImage && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Preview:</p>
                  <img
                    src={previewImage}
                    alt="Cover preview"
                    className="w-full max-w-md h-48 object-cover rounded-lg border border-gray-300"
                  />
                </div>
              )}
            </div>
          </div>

          {/* Rewards */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-6 flex items-center">
              <TagIcon className="h-5 w-5 mr-2" />
              Rewards for Backers
            </h2>
            
            <div className="space-y-6">
              {formData.rewards.map((reward, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-md font-medium text-gray-900">Reward {index + 1}</h3>
                    {formData.rewards.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeReward(index)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Remove
                      </button>
                    )}
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Reward Title *
                      </label>
                      <input
                        type="text"
                        value={reward.title}
                        onChange={(e) => handleRewardChange(index, 'title', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                        placeholder="e.g., Digital Copy"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Amount (LKR) *
                      </label>
                      <input
                        type="number"
                        value={reward.amount}
                        onChange={(e) => handleRewardChange(index, 'amount', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                        placeholder="1000"
                        min="1"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Quantity Available
                      </label>
                      <input
                        type="number"
                        value={reward.quantity}
                        onChange={(e) => handleRewardChange(index, 'quantity', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                        placeholder="0 (unlimited)"
                        min="0"
                      />
                    </div>
                  </div>
                  
                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Description *
                    </label>
                    <textarea
                      value={reward.description}
                      onChange={(e) => handleRewardChange(index, 'description', e.target.value)}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                      placeholder="Describe what backers will receive..."
                    />
                  </div>
                </div>
              ))}
              
              <button
                type="button"
                onClick={addReward}
                className="w-full py-2 px-4 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-primary-500 hover:text-primary-600 transition-colors"
              >
                + Add Another Reward
              </button>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => navigate('/dashboard')}
              className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? (isEditing ? 'Updating...' : 'Creating...') : (isEditing ? 'Update Campaign' : 'Create Campaign')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateCampaign;

