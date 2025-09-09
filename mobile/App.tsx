import React, { useEffect } from 'react';
import { StatusBar, Platform } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { Provider } from 'react-redux';
import { PaperProvider } from 'react-native-paper';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { store } from './src/store/store';
import { useAppDispatch, useAppSelector } from './src/store/hooks';
import { checkAuthStatus } from './src/store/slices/authSlice';
import AuthNavigator from './src/navigation/AuthNavigator';
import MainNavigator from './src/navigation/MainNavigator';
import SplashScreen from './src/screens/SplashScreen';
import { theme } from './src/theme/theme';
import PushNotificationService from './src/services/PushNotificationService';
import BiometricService from './src/services/BiometricService';

const Stack = createStackNavigator();

// Inner component that has access to Redux hooks
const AppContent: React.FC = () => {
  const dispatch = useAppDispatch();
  const { isAuthenticated, isLoading } = useAppSelector((state) => state.auth);

  useEffect(() => {
    // Initialize services
    PushNotificationService.initialize();
    BiometricService.initialize();
    
    // Check authentication status
    dispatch(checkAuthStatus());
  }, [dispatch]);

  if (isLoading) {
    return <SplashScreen />;
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {isAuthenticated ? (
          <Stack.Screen name="Main" component={MainNavigator} />
        ) : (
          <Stack.Screen name="Auth" component={AuthNavigator} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <GestureHandlerRootView style={{ flex: 1 }}>
        <SafeAreaProvider>
          <PaperProvider theme={theme}>
            <StatusBar
              barStyle={Platform.OS === 'ios' ? 'dark-content' : 'light-content'}
              backgroundColor={theme.colors.primary}
            />
            <AppContent />
          </PaperProvider>
        </SafeAreaProvider>
      </GestureHandlerRootView>
    </Provider>
  );
};

export default App;
