import { MD3LightTheme, MD3DarkTheme } from 'react-native-paper';

export const lightTheme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    primary: '#3B82F6',
    primaryContainer: '#DBEAFE',
    secondary: '#10B981',
    secondaryContainer: '#D1FAE5',
    tertiary: '#8B5CF6',
    tertiaryContainer: '#EDE9FE',
    surface: '#FFFFFF',
    surfaceVariant: '#F3F4F6',
    background: '#F9FAFB',
    error: '#EF4444',
    errorContainer: '#FEE2E2',
    onPrimary: '#FFFFFF',
    onSecondary: '#FFFFFF',
    onTertiary: '#FFFFFF',
    onSurface: '#1F2937',
    onSurfaceVariant: '#6B7280',
    onBackground: '#1F2937',
    onError: '#FFFFFF',
    outline: '#D1D5DB',
    outlineVariant: '#E5E7EB',
  },
  roundness: 12,
};

export const darkTheme = {
  ...MD3DarkTheme,
  colors: {
    ...MD3DarkTheme.colors,
    primary: '#60A5FA',
    primaryContainer: '#1E40AF',
    secondary: '#34D399',
    secondaryContainer: '#065F46',
    tertiary: '#A78BFA',
    tertiaryContainer: '#5B21B6',
    surface: '#1F2937',
    surfaceVariant: '#374151',
    background: '#111827',
    error: '#F87171',
    errorContainer: '#7F1D1D',
    onPrimary: '#000000',
    onSecondary: '#000000',
    onTertiary: '#000000',
    onSurface: '#F9FAFB',
    onSurfaceVariant: '#D1D5DB',
    onBackground: '#F9FAFB',
    onError: '#000000',
    outline: '#4B5563',
    outlineVariant: '#374151',
  },
  roundness: 12,
};

export const theme = lightTheme;

export const colors = {
  primary: '#3B82F6',
  primaryDark: '#1D4ED8',
  primaryLight: '#60A5FA',
  secondary: '#10B981',
  secondaryDark: '#059669',
  secondaryLight: '#34D399',
  tertiary: '#8B5CF6',
  tertiaryDark: '#7C3AED',
  tertiaryLight: '#A78BFA',
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#06B6D4',
  surface: '#FFFFFF',
  background: '#F9FAFB',
  text: '#1F2937',
  textSecondary: '#6B7280',
  textLight: '#9CA3AF',
  border: '#E5E7EB',
  borderLight: '#F3F4F6',
  shadow: 'rgba(0, 0, 0, 0.1)',
  shadowDark: 'rgba(0, 0, 0, 0.25)',
};

export const typography = {
  h1: {
    fontSize: 32,
    fontWeight: 'bold' as const,
    lineHeight: 40,
  },
  h2: {
    fontSize: 24,
    fontWeight: 'bold' as const,
    lineHeight: 32,
  },
  h3: {
    fontSize: 20,
    fontWeight: '600' as const,
    lineHeight: 28,
  },
  h4: {
    fontSize: 18,
    fontWeight: '600' as const,
    lineHeight: 24,
  },
  body1: {
    fontSize: 16,
    fontWeight: 'normal' as const,
    lineHeight: 24,
  },
  body2: {
    fontSize: 14,
    fontWeight: 'normal' as const,
    lineHeight: 20,
  },
  caption: {
    fontSize: 12,
    fontWeight: 'normal' as const,
    lineHeight: 16,
  },
  button: {
    fontSize: 16,
    fontWeight: '600' as const,
    lineHeight: 24,
  },
  overline: {
    fontSize: 10,
    fontWeight: '500' as const,
    lineHeight: 16,
    textTransform: 'uppercase' as const,
  },
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 40,
};

export const borderRadius = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  xxl: 24,
  round: 50,
};

export const shadows = {
  sm: {
    shadowColor: colors.shadow,
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.2,
    shadowRadius: 1.41,
    elevation: 2,
  },
  md: {
    shadowColor: colors.shadow,
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  lg: {
    shadowColor: colors.shadow,
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 4.65,
    elevation: 8,
  },
  xl: {
    shadowColor: colors.shadow,
    shadowOffset: {
      width: 0,
      height: 6,
    },
    shadowOpacity: 0.37,
    shadowRadius: 7.49,
    elevation: 12,
  },
};
