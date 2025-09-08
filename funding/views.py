from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _
from .models import (
    FundingRound, FundingMilestone, FundingAllocation,
    FundingProgress, FundingAnalytics
)
from .serializers import (
    FundingRoundSerializer, FundingRoundUpdateSerializer,
    FundingMilestoneSerializer, FundingAllocationSerializer,
    FundingAllocationUpdateSerializer, FundingProgressSerializer,
    FundingAnalyticsSerializer
)


# Placeholder views - will be implemented in detail later
class FundingRoundListView(generics.ListCreateAPIView):
    """List and create funding rounds"""
    queryset = FundingRound.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'message': 'Funding rounds will be implemented'})


class FundingRoundCreateView(generics.CreateAPIView):
    """Create funding round"""
    queryset = FundingRound.objects.all()
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response({'message': 'Funding round creation will be implemented'})


class FundingRoundDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update and delete funding rounds"""
    queryset = FundingRound.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        return Response({'message': f'Funding round {pk} details will be implemented'})


class FundingRoundUpdateView(generics.UpdateAPIView):
    """Update funding round"""
    queryset = FundingRound.objects.all()
    serializer_class = FundingRoundUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get the funding round object and check permissions"""
        funding_round = super().get_object()
        # Check if the user is the campaign creator
        if funding_round.campaign.creator != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only update funding rounds for your own campaigns.")
        return funding_round
    
    def perform_update(self, serializer):
        """Perform the update"""
        serializer.save()
    
    def update(self, request, *args, **kwargs):
        """Handle both PUT and PATCH requests"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'message': 'Funding round updated successfully',
            'data': FundingRoundSerializer(instance).data
        }, status=status.HTTP_200_OK)


class FundingRoundDeleteView(generics.DestroyAPIView):
    """Delete funding round"""
    queryset = FundingRound.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get the funding round object and check permissions"""
        funding_round = super().get_object()
        # Check if the user is the campaign creator
        if funding_round.campaign.creator != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only delete funding rounds for your own campaigns.")
        
        # Check if funding round has any current funding (can't delete if money is involved)
        if funding_round.current_funding > 0:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Cannot delete funding round that has received funding.")
        
        return funding_round
    
    def perform_destroy(self, instance):
        """Perform the deletion"""
        round_title = instance.title
        campaign_title = instance.campaign.title
        instance.delete()
        return round_title, campaign_title
    
    def destroy(self, request, *args, **kwargs):
        """Handle DELETE request"""
        instance = self.get_object()
        round_title, campaign_title = self.perform_destroy(instance)
        
        return Response({
            'message': f'Funding round "{round_title}" for campaign "{campaign_title}" has been deleted successfully'
        }, status=status.HTTP_200_OK)


class FundingMilestoneListView(generics.ListCreateAPIView):
    """List and create funding milestones"""
    queryset = FundingMilestone.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'message': 'Funding milestones will be implemented'})


class FundingMilestoneCreateView(generics.CreateAPIView):
    """Create funding milestone"""
    queryset = FundingMilestone.objects.all()
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response({'message': 'Funding milestone creation will be implemented'})


class FundingMilestoneDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update and delete funding milestones"""
    queryset = FundingMilestone.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        return Response({'message': f'Funding milestone {pk} details will be implemented'})


class FundingMilestoneUpdateView(generics.UpdateAPIView):
    """Update funding milestone"""
    queryset = FundingMilestone.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk):
        return Response({'message': f'Funding milestone {pk} update will be implemented'})


class FundingMilestoneDeleteView(generics.DestroyAPIView):
    """Delete funding milestone"""
    queryset = FundingMilestone.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        return Response({'message': f'Funding milestone {pk} deletion will be implemented'})


class FundingAllocationListView(generics.ListCreateAPIView):
    """List and create funding allocations"""
    queryset = FundingAllocation.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'message': 'Funding allocations will be implemented'})


class FundingAllocationCreateView(generics.CreateAPIView):
    """Create funding allocation"""
    queryset = FundingAllocation.objects.all()
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response({'message': 'Funding allocation creation will be implemented'})


class FundingAllocationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update and delete funding allocations"""
    queryset = FundingAllocation.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        return Response({'message': f'Funding allocation {pk} details will be implemented'})


class FundingAllocationUpdateView(generics.UpdateAPIView):
    """Update funding allocation"""
    queryset = FundingAllocation.objects.all()
    serializer_class = FundingAllocationUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get the funding allocation object and check permissions"""
        allocation = super().get_object()
        # Check if the user is the campaign creator
        if allocation.campaign.creator != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only update funding allocations for your own campaigns.")
        return allocation
    
    def perform_update(self, serializer):
        """Perform the update"""
        serializer.save()
    
    def update(self, request, *args, **kwargs):
        """Handle both PUT and PATCH requests"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'message': 'Funding allocation updated successfully',
            'data': FundingAllocationSerializer(instance).data
        }, status=status.HTTP_200_OK)


class FundingAllocationDeleteView(generics.DestroyAPIView):
    """Delete funding allocation"""
    queryset = FundingAllocation.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get the funding allocation object and check permissions"""
        allocation = super().get_object()
        # Check if the user is the campaign creator
        if allocation.campaign.creator != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only delete funding allocations for your own campaigns.")
        
        # Check if any actual amount has been spent (can't delete if money has been spent)
        if allocation.actual_amount > 0:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Cannot delete funding allocation that has actual spending recorded.")
        
        return allocation
    
    def perform_destroy(self, instance):
        """Perform the deletion"""
        allocation_type = instance.get_allocation_type_display()
        campaign_title = instance.campaign.title
        instance.delete()
        return allocation_type, campaign_title
    
    def destroy(self, request, *args, **kwargs):
        """Handle DELETE request"""
        instance = self.get_object()
        allocation_type, campaign_title = self.perform_destroy(instance)
        
        return Response({
            'message': f'Funding allocation "{allocation_type}" for campaign "{campaign_title}" has been deleted successfully'
        }, status=status.HTTP_200_OK)


class FundingProgressListView(generics.ListAPIView):
    """List funding progress"""
    queryset = FundingProgress.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'message': 'Funding progress will be implemented'})


class FundingProgressDetailView(generics.RetrieveAPIView):
    """Retrieve funding progress details"""
    queryset = FundingProgress.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        return Response({'message': f'Funding progress {pk} details will be implemented'})


class FundingAnalyticsListView(generics.ListAPIView):
    """List funding analytics"""
    queryset = FundingAnalytics.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'message': 'Funding analytics will be implemented'})


class FundingAnalyticsDetailView(generics.RetrieveAPIView):
    """Retrieve funding analytics details"""
    queryset = FundingAnalytics.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        return Response({'message': f'Funding analytics {pk} details will be implemented'})


class FundingDashboardView(APIView):
    """Get funding dashboard"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'message': 'Funding dashboard will be implemented'})


class CreatorDashboardView(APIView):
    """Get creator dashboard"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'message': 'Creator dashboard will be implemented'})


class InvestorDashboardView(APIView):
    """Get investor dashboard"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'message': 'Investor dashboard will be implemented'})


class FundingReportView(APIView):
    """Get funding reports"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'message': 'Funding reports will be implemented'})


class CampaignFundingReportView(APIView):
    """Get campaign funding report"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, campaign_pk):
        return Response({'message': f'Campaign {campaign_pk} funding report will be implemented'})


class UserFundingReportView(APIView):
    """Get user funding report"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_pk):
        return Response({'message': f'User {user_pk} funding report will be implemented'})
