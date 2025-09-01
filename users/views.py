from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, UserDocument
from .serializers import (
    UserSerializer, UserProfileSerializer, UserDocumentSerializer,
    UserRegistrationSerializer, UserLoginSerializer
)


# Placeholder views - will be implemented in detail later
class UserListView(generics.ListAPIView):
    """List all users"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update user details"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserProfileView(generics.RetrieveAPIView):
    """Retrieve user profile"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]


class CurrentUserProfileView(APIView):
    """Get current user's profile"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            # Return user data with profile data
            user_data = UserSerializer(request.user).data
            profile_data = UserProfileSerializer(profile).data
            
            # Combine user and profile data
            combined_data = {
                **user_data,
                **profile_data,
                'profile_id': profile.id
            }
            return Response(combined_data)
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist
            profile = UserProfile.objects.create(user=request.user)
            user_data = UserSerializer(request.user).data
            profile_data = UserProfileSerializer(profile).data
            
            # Combine user and profile data
            combined_data = {
                **user_data,
                **profile_data,
                'profile_id': profile.id
            }
            return Response(combined_data, status=status.HTTP_201_CREATED)


class TestProfileView(APIView):
    """Test endpoint for debugging"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'message': 'Profile endpoint is working',
            'user': request.user.username if request.user.is_authenticated else 'Anonymous'
        })


class UserProfileUpdateView(generics.UpdateAPIView):
    """Update user profile"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]


class UserDocumentListView(generics.ListCreateAPIView):
    """List and create user documents"""
    queryset = UserDocument.objects.all()
    serializer_class = UserDocumentSerializer
    permission_classes = [IsAuthenticated]


class UserDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update and delete user documents"""
    queryset = UserDocument.objects.all()
    serializer_class = UserDocumentSerializer
    permission_classes = [IsAuthenticated]


class UserDocumentUploadView(generics.CreateAPIView):
    """Upload user documents"""
    queryset = UserDocument.objects.all()
    serializer_class = UserDocumentSerializer
    permission_classes = [IsAuthenticated]


class UserSearchView(generics.ListAPIView):
    """Search users"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class CreatorListView(generics.ListAPIView):
    """List all creators"""
    queryset = User.objects.filter(user_type='creator')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class InvestorListView(generics.ListAPIView):
    """List all investors"""
    queryset = User.objects.filter(user_type='investor')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserStatsView(APIView):
    """Get user statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'message': 'User stats will be implemented'})


# Authentication views
class UserRegistrationView(generics.CreateAPIView):
    """User registration"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    """User login"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        })


class UserLogoutView(APIView):
    """User logout"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Blacklist the refresh token
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                from rest_framework_simplejwt.tokens import RefreshToken
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({'message': 'Logout successful'})
        except Exception as e:
            return Response({'message': 'Logout successful'})


class PasswordChangeView(APIView):
    """Change password"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response({'message': 'Password change will be implemented'})


class PasswordResetView(APIView):
    """Reset password"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        return Response({'message': 'Password reset will be implemented'})


class PasswordResetConfirmView(APIView):
    """Confirm password reset"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        return Response({'message': 'Password reset confirm will be implemented'})


class EmailVerificationView(APIView):
    """Verify email"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        return Response({'message': 'Email verification will be implemented'})


class ResendVerificationView(APIView):
    """Resend verification email"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response({'message': 'Resend verification will be implemented'})


class AccountRecoveryView(APIView):
    """Account recovery"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        return Response({'message': 'Account recovery will be implemented'})



