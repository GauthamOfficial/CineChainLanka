import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
  Image,
  Dimensions,
} from 'react-native';
import { useAppSelector, useAppDispatch } from '../store/hooks';
import { fetchCampaigns } from '../store/slices/campaignSlice';
import { fetchUserProfile } from '../store/slices/userSlice';
import { Card, Title, Paragraph, Button, Chip } from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialIcons';
import LinearGradient from 'react-native-linear-gradient';

const { width } = Dimensions.get('window');

interface Campaign {
  id: number;
  title: string;
  description: string;
  goal_amount: number;
  current_amount: number;
  end_date: string;
  status: string;
  cover_image: string;
  creator: {
    username: string;
    first_name: string;
    last_name: string;
  };
  category: string;
}

const HomeScreen: React.FC = () => {
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.auth);
  const { campaigns, isLoading } = useAppSelector((state) => state.campaigns);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    await Promise.all([
      dispatch(fetchCampaigns({ page: 1, limit: 6 })),
      dispatch(fetchUserProfile()),
    ]);
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const getProgressPercentage = (current: number, goal: number) => {
    return Math.min((current / goal) * 100, 100);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return '#10B981';
      case 'funded':
        return '#3B82F6';
      case 'completed':
        return '#8B5CF6';
      default:
        return '#6B7280';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return 'Active';
      case 'funded':
        return 'Funded';
      case 'completed':
        return 'Completed';
      default:
        return 'Unknown';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const renderCampaignCard = (campaign: Campaign) => {
    const progress = getProgressPercentage(campaign.current_amount, campaign.goal_amount);
    
    return (
      <TouchableOpacity key={campaign.id} style={styles.campaignCard}>
        <Card style={styles.card}>
          <Image
            source={{ uri: campaign.cover_image || 'https://via.placeholder.com/300x200' }}
            style={styles.cardImage}
            resizeMode="cover"
          />
          <Card.Content style={styles.cardContent}>
            <View style={styles.cardHeader}>
              <Title style={styles.cardTitle} numberOfLines={2}>
                {campaign.title}
              </Title>
              <Chip
                style={[styles.statusChip, { backgroundColor: getStatusColor(campaign.status) }]}
                textStyle={styles.statusText}
              >
                {getStatusText(campaign.status)}
              </Chip>
            </View>
            
            <Paragraph style={styles.cardDescription} numberOfLines={2}>
              {campaign.description}
            </Paragraph>
            
            <View style={styles.creatorInfo}>
              <Icon name="person" size={16} color="#6B7280" />
              <Text style={styles.creatorText}>
                {campaign.creator.first_name} {campaign.creator.last_name}
              </Text>
            </View>
            
            <View style={styles.progressContainer}>
              <View style={styles.progressBar}>
                <View
                  style={[
                    styles.progressFill,
                    { width: `${progress}%` }
                  ]}
                />
              </View>
              <Text style={styles.progressText}>{progress.toFixed(1)}%</Text>
            </View>
            
            <View style={styles.amountContainer}>
              <Text style={styles.currentAmount}>
                {formatCurrency(campaign.current_amount)}
              </Text>
              <Text style={styles.goalAmount}>
                of {formatCurrency(campaign.goal_amount)} goal
              </Text>
            </View>
            
            <View style={styles.cardFooter}>
              <Text style={styles.endDate}>
                Ends {formatDate(campaign.end_date)}
              </Text>
              <Button
                mode="contained"
                style={styles.viewButton}
                labelStyle={styles.viewButtonText}
              >
                View
              </Button>
            </View>
          </Card.Content>
        </Card>
      </TouchableOpacity>
    );
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Welcome Header */}
      <LinearGradient
        colors={['#3B82F6', '#1D4ED8']}
        style={styles.welcomeHeader}
      >
        <View style={styles.welcomeContent}>
          <Text style={styles.welcomeTitle}>
            Welcome back, {user?.first_name || 'Creator'}!
          </Text>
          <Text style={styles.welcomeSubtitle}>
            Discover amazing film projects and support creators
          </Text>
        </View>
      </LinearGradient>

      {/* Quick Stats */}
      <View style={styles.statsContainer}>
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>1,250</Text>
          <Text style={styles.statLabel}>Active Campaigns</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>$2.5M</Text>
          <Text style={styles.statLabel}>Total Raised</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statNumber}>15.2%</Text>
          <Text style={styles.statLabel}>Avg ROI</Text>
        </View>
      </View>

      {/* Featured Campaigns */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Featured Campaigns</Text>
          <TouchableOpacity>
            <Text style={styles.seeAllText}>See All</Text>
          </TouchableOpacity>
        </View>
        
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          style={styles.campaignsScroll}
        >
          {campaigns.map(renderCampaignCard)}
        </ScrollView>
      </View>

      {/* Categories */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Browse by Category</Text>
        <View style={styles.categoriesContainer}>
          {[
            { name: 'Drama', icon: 'theater-comedy', color: '#EF4444' },
            { name: 'Action', icon: 'flash-on', color: '#F59E0B' },
            { name: 'Comedy', icon: 'sentiment-very-satisfied', color: '#10B981' },
            { name: 'Horror', icon: 'nightlight-round', color: '#8B5CF6' },
            { name: 'Documentary', icon: 'description', color: '#06B6D4' },
            { name: 'Animation', icon: 'animation', color: '#EC4899' },
          ].map((category, index) => (
            <TouchableOpacity key={index} style={styles.categoryItem}>
              <View style={[styles.categoryIcon, { backgroundColor: category.color }]}>
                <Icon name={category.icon} size={24} color="white" />
              </View>
              <Text style={styles.categoryText}>{category.name}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Recent Activity */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent Activity</Text>
        <Card style={styles.activityCard}>
          <Card.Content>
            <View style={styles.activityItem}>
              <Icon name="notifications" size={20} color="#3B82F6" />
              <View style={styles.activityContent}>
                <Text style={styles.activityTitle}>New backer joined your campaign</Text>
                <Text style={styles.activityTime}>2 hours ago</Text>
              </View>
            </View>
            <View style={styles.activityItem}>
              <Icon name="trending-up" size={20} color="#10B981" />
              <View style={styles.activityContent}>
                <Text style={styles.activityTitle}>Revenue received from Netflix</Text>
                <Text style={styles.activityTime}>1 day ago</Text>
              </View>
            </View>
            <View style={styles.activityItem}>
              <Icon name="account-balance-wallet" size={20} color="#8B5CF6" />
              <View style={styles.activityContent}>
                <Text style={styles.activityTitle}>Royalty distribution completed</Text>
                <Text style={styles.activityTime}>3 days ago</Text>
              </View>
            </View>
          </Card.Content>
        </Card>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  welcomeHeader: {
    padding: 20,
    paddingTop: 40,
  },
  welcomeContent: {
    marginTop: 20,
  },
  welcomeTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 8,
  },
  welcomeSubtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.9)',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 20,
    backgroundColor: 'white',
    marginTop: -10,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  statLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 4,
  },
  section: {
    padding: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  seeAllText: {
    fontSize: 14,
    color: '#3B82F6',
    fontWeight: '600',
  },
  campaignsScroll: {
    marginHorizontal: -20,
  },
  campaignCard: {
    width: width * 0.8,
    marginRight: 16,
    marginLeft: 20,
  },
  card: {
    elevation: 2,
    borderRadius: 12,
    overflow: 'hidden',
  },
  cardImage: {
    height: 120,
    width: '100%',
  },
  cardContent: {
    padding: 16,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    flex: 1,
    marginRight: 8,
  },
  statusChip: {
    height: 24,
  },
  statusText: {
    fontSize: 10,
    color: 'white',
  },
  cardDescription: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 8,
  },
  creatorInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  creatorText: {
    fontSize: 12,
    color: '#6B7280',
    marginLeft: 4,
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  progressBar: {
    flex: 1,
    height: 6,
    backgroundColor: '#E5E7EB',
    borderRadius: 3,
    marginRight: 8,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#3B82F6',
    borderRadius: 3,
  },
  progressText: {
    fontSize: 12,
    color: '#6B7280',
    fontWeight: '600',
  },
  amountContainer: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginBottom: 12,
  },
  currentAmount: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  goalAmount: {
    fontSize: 12,
    color: '#6B7280',
    marginLeft: 4,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  endDate: {
    fontSize: 12,
    color: '#6B7280',
  },
  viewButton: {
    borderRadius: 20,
  },
  viewButtonText: {
    fontSize: 12,
  },
  categoriesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  categoryItem: {
    width: '30%',
    alignItems: 'center',
    marginBottom: 16,
  },
  categoryIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  categoryText: {
    fontSize: 12,
    color: '#6B7280',
    textAlign: 'center',
  },
  activityCard: {
    elevation: 1,
    borderRadius: 12,
  },
  activityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
  },
  activityContent: {
    marginLeft: 12,
    flex: 1,
  },
  activityTitle: {
    fontSize: 14,
    color: '#1F2937',
    marginBottom: 2,
  },
  activityTime: {
    fontSize: 12,
    color: '#6B7280',
  },
});

export default HomeScreen;
