from django.shortcuts import render
from django.db import models
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _
from .models import (
    Campaign, CampaignCategory, CampaignReward, 
    CampaignUpdate, CampaignComment
)


from .serializers import (
    CampaignSerializer, CampaignCategorySerializer, CampaignRewardSerializer,
    CampaignUpdateSerializer, CampaignCommentSerializer, CampaignCreateSerializer
)

class CampaignListView(generics.ListCreateAPIView):
    """List and create campaigns"""
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CampaignCreateSerializer
        return CampaignSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]
    
    def get_queryset(self):
        queryset = Campaign.objects.all()
        
        # Filter by status
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Search by title or description
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) |
                models.Q(description__icontains=search) |
                models.Q(short_description__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class CampaignCreateView(generics.CreateAPIView):
    """Create a new campaign"""
    queryset = Campaign.objects.all()
    serializer_class = CampaignCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class CampaignDetailView(generics.RetrieveAPIView):
    """Retrieve campaign details"""
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    permission_classes = [AllowAny]


class CampaignUpdateView(generics.UpdateAPIView):
    """Update campaign"""
    queryset = Campaign.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk):
        return Response({'message': f'Campaign {pk} update will be implemented'})


class CampaignDeleteView(generics.DestroyAPIView):
    """Delete campaign"""
    queryset = Campaign.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        return Response({'message': f'Campaign {pk} deletion will be implemented'})


class CampaignCategoryListView(generics.ListAPIView):
    """List campaign categories"""
    queryset = CampaignCategory.objects.all()
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({'message': 'Campaign categories will be implemented'})


class CampaignCategoryDetailView(generics.RetrieveAPIView):
    """Retrieve campaign category details"""
    queryset = CampaignCategory.objects.all()
    permission_classes = [AllowAny]
    
    def get(self, request, pk):
        return Response({'message': f'Category {pk} details will be implemented'})


class CampaignRewardListView(generics.ListCreateAPIView):
    """List and create campaign rewards"""
    queryset = CampaignReward.objects.all()
    permission_classes = [AllowAny]
    
    def get(self, request, campaign_pk):
        return Response({'message': f'Rewards for campaign {campaign_pk} will be implemented'})


class CampaignRewardCreateView(generics.CreateAPIView):
    """Create campaign reward"""
    queryset = CampaignReward.objects.all()
    permission_classes = [IsAuthenticated]
    
    def post(self, request, campaign_pk):
        return Response({'message': f'Reward creation for campaign {campaign_pk} will be implemented'})


class CampaignRewardDetailView(generics.RetrieveAPIView):
    """Retrieve campaign reward details"""
    queryset = CampaignReward.objects.all()
    permission_classes = [AllowAny]
    
    def get(self, request, pk):
        return Response({'message': f'Reward {pk} details will be implemented'})


class CampaignRewardUpdateView(generics.UpdateAPIView):
    """Update campaign reward"""
    queryset = CampaignReward.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk):
        return Response({'message': f'Reward {pk} update will be implemented'})


class CampaignRewardDeleteView(generics.DestroyAPIView):
    """Delete campaign reward"""
    queryset = CampaignReward.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        return Response({'message': f'Reward {pk} deletion will be implemented'})


class CampaignUpdateListView(generics.ListCreateAPIView):
    """List and create campaign updates"""
    queryset = CampaignUpdate.objects.all()
    permission_classes = [AllowAny]
    
    def get(self, request, campaign_pk):
        return Response({'message': f'Updates for campaign {campaign_pk} will be implemented'})


class CampaignUpdateCreateView(generics.CreateAPIView):
    """Create campaign update"""
    queryset = CampaignUpdate.objects.all()
    permission_classes = [IsAuthenticated]
    
    def post(self, request, campaign_pk):
        return Response({'message': f'Update creation for campaign {campaign_pk} will be implemented'})


class CampaignUpdateDetailView(generics.RetrieveAPIView):
    """Retrieve campaign update details"""
    queryset = CampaignUpdate.objects.all()
    permission_classes = [AllowAny]
    
    def get(self, request, pk):
        return Response({'message': f'Update {pk} details will be implemented'})


class CampaignUpdateUpdateView(generics.UpdateAPIView):
    """Update campaign update"""
    queryset = CampaignUpdate.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk):
        return Response({'message': f'Update {pk} modification will be implemented'})


class CampaignUpdateDeleteView(generics.DestroyAPIView):
    """Delete campaign update"""
    queryset = CampaignUpdate.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        return Response({'message': f'Update {pk} deletion will be implemented'})


class CampaignCommentListView(generics.ListCreateAPIView):
    """List and create campaign comments"""
    queryset = CampaignComment.objects.all()
    permission_classes = [AllowAny]
    
    def get(self, request, campaign_pk):
        return Response({'message': f'Comments for campaign {campaign_pk} will be implemented'})


class CampaignCommentCreateView(generics.CreateAPIView):
    """Create campaign comment"""
    queryset = CampaignComment.objects.all()
    permission_classes = [IsAuthenticated]
    
    def post(self, request, campaign_pk):
        return Response({'message': f'Comment creation for campaign {campaign_pk} will be implemented'})


class CampaignCommentDetailView(generics.RetrieveAPIView):
    """Retrieve campaign comment details"""
    queryset = CampaignComment.objects.all()
    permission_classes = [AllowAny]
    
    def get(self, request, pk):
        return Response({'message': f'Comment {pk} details will be implemented'})


class CampaignCommentUpdateView(generics.UpdateAPIView):
    """Update campaign comment"""
    queryset = CampaignComment.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk):
        return Response({'message': f'Comment {pk} update will be implemented'})


class CampaignCommentDeleteView(generics.DestroyAPIView):
    """Delete campaign comment"""
    queryset = CampaignComment.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, pk):
        return Response({'message': f'Comment {pk} deletion will be implemented'})


class CampaignSearchView(generics.ListAPIView):
    """Search campaigns"""
    queryset = Campaign.objects.all()
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({'message': 'Campaign search will be implemented'})


class FeaturedCampaignListView(generics.ListAPIView):
    """List featured campaigns"""
    queryset = Campaign.objects.all()
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({'message': 'Featured campaigns will be implemented'})


class TrendingCampaignListView(generics.ListAPIView):
    """List trending campaigns"""
    queryset = Campaign.objects.all()
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({'message': 'Trending campaigns will be implemented'})


class CampaignLikeView(APIView):
    """Like a campaign"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        return Response({'message': f'Campaign {pk} like will be implemented'})


class CampaignUnlikeView(APIView):
    """Unlike a campaign"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        return Response({'message': f'Campaign {pk} unlike will be implemented'})


class CampaignShareView(APIView):
    """Share a campaign"""
    permission_classes = [AllowAny]
    
    def post(self, request, pk):
        return Response({'message': f'Campaign {pk} share will be implemented'})


class CampaignReportView(APIView):
    """Report a campaign"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        return Response({'message': f'Campaign {pk} report will be implemented'})


class CampaignStatsView(APIView):
    """Get campaign statistics"""
    permission_classes = [AllowAny]
    
    def get(self, request, pk):
        return Response({'message': f'Campaign {pk} stats will be implemented'})


class CampaignAnalyticsView(APIView):
    """Get campaign analytics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        return Response({'message': f'Campaign {pk} analytics will be implemented'})
