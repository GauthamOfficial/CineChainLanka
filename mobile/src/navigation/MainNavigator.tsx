import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useAppSelector } from '../store/hooks';

// Screens
import HomeScreen from '../screens/HomeScreen';
import CampaignsScreen from '../screens/CampaignsScreen';
import CampaignDetailScreen from '../screens/CampaignDetailScreen';
import CreateCampaignScreen from '../screens/CreateCampaignScreen';
import ProfileScreen from '../screens/ProfileScreen';
import AnalyticsScreen from '../screens/AnalyticsScreen';
import MarketplaceScreen from '../screens/MarketplaceScreen';
import WalletScreen from '../screens/WalletScreen';
import NotificationsScreen from '../screens/NotificationsScreen';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

const CampaignStack = () => (
  <Stack.Navigator>
    <Stack.Screen 
      name="CampaignsList" 
      component={CampaignsScreen}
      options={{ title: 'Campaigns' }}
    />
    <Stack.Screen 
      name="CampaignDetail" 
      component={CampaignDetailScreen}
      options={{ title: 'Campaign Details' }}
    />
    <Stack.Screen 
      name="CreateCampaign" 
      component={CreateCampaignScreen}
      options={{ title: 'Create Campaign' }}
    />
  </Stack.Navigator>
);

const ProfileStack = () => (
  <Stack.Navigator>
    <Stack.Screen 
      name="ProfileMain" 
      component={ProfileScreen}
      options={{ title: 'Profile' }}
    />
    <Stack.Screen 
      name="Analytics" 
      component={AnalyticsScreen}
      options={{ title: 'Analytics' }}
    />
    <Stack.Screen 
      name="Wallet" 
      component={WalletScreen}
      options={{ title: 'Wallet' }}
    />
    <Stack.Screen 
      name="Notifications" 
      component={NotificationsScreen}
      options={{ title: 'Notifications' }}
    />
  </Stack.Navigator>
);

const MainNavigator: React.FC = () => {
  const { user } = useAppSelector((state) => state.auth);

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: string;

          switch (route.name) {
            case 'Home':
              iconName = 'home';
              break;
            case 'Campaigns':
              iconName = 'movie';
              break;
            case 'Marketplace':
              iconName = 'store';
              break;
            case 'Profile':
              iconName = 'person';
              break;
            default:
              iconName = 'help';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#3B82F6',
        tabBarInactiveTintColor: 'gray',
        headerShown: false,
      })}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{ title: 'Home' }}
      />
      <Tab.Screen 
        name="Campaigns" 
        component={CampaignStack}
        options={{ title: 'Campaigns' }}
      />
      <Tab.Screen 
        name="Marketplace" 
        component={MarketplaceScreen}
        options={{ title: 'Marketplace' }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileStack}
        options={{ title: 'Profile' }}
      />
    </Tab.Navigator>
  );
};

export default MainNavigator;
