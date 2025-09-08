from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _
from .models import (
    KYCRequest, KYCVerification, KYCDocument, KYCComplianceCheck
)
from .serializers import (
    KYCRequestSerializer, KYCDocumentSerializer, KYCDocumentUpdateSerializer,
    KYCVerificationSerializer, KYCComplianceCheckSerializer
)


# Placeholder views - will be implemented in detail later
class KYCRequestListView(generics.ListCreateAPIView):
    """List and create KYC requests"""
    queryset = KYCRequest.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'message': 'KYC requests will be implemented'})


class KYCRequestCreateView(generics.CreateAPIView):
    """Create KYC request"""
    queryset = KYCRequest.objects.all()
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response({'message': 'KYC request creation will be implemented'})


class KYCRequestDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update KYC request details"""
    queryset = KYCRequest.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        return Response({'message': f'KYC request {pk} details will be implemented'})


class KYCRequestUpdateView(generics.UpdateAPIView):
    """Update KYC request"""
    queryset = KYCRequest.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk):
        return Response({'message': f'KYC request {pk} update will be implemented'})


class KYCRequestSubmitView(APIView):
    """Submit KYC request for review"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        return Response({'message': f'KYC request {pk} submission will be implemented'})


class KYCVerificationListView(generics.ListAPIView):
    """List KYC verifications"""
    queryset = KYCVerification.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'message': 'KYC verifications will be implemented'})


class KYCVerificationDetailView(generics.RetrieveAPIView):
    """Retrieve KYC verification details"""
    queryset = KYCVerification.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        return Response({'message': f'KYC verification {pk} details will be implemented'})


class KYCVerificationUpdateView(generics.UpdateAPIView):
    """Update KYC verification"""
    queryset = KYCVerification.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk):
        return Response({'message': f'KYC verification {pk} update will be implemented'})


class KYCDocumentListView(generics.ListCreateAPIView):
    """List and create KYC documents"""
    queryset = KYCDocument.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'message': 'KYC documents will be implemented'})


class KYCDocumentUploadView(generics.CreateAPIView):
    """Upload KYC documents"""
    queryset = KYCDocument.objects.all()
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response({'message': 'KYC document upload will be implemented'})


class KYCDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update and delete KYC documents"""
    queryset = KYCDocument.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        return Response({'message': f'KYC document {pk} details will be implemented'})


class KYCDocumentUpdateView(generics.UpdateAPIView):
    """Update KYC document"""
    queryset = KYCDocument.objects.all()
    serializer_class = KYCDocumentUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get the KYC document object and check permissions"""
        document = super().get_object()
        # Check if the user owns the KYC request
        if document.kyc_request.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only update your own KYC documents.")
        return document
    
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
            'message': 'KYC document updated successfully',
            'data': KYCDocumentSerializer(instance).data
        }, status=status.HTTP_200_OK)


class KYCDocumentDeleteView(generics.DestroyAPIView):
    """Delete KYC document"""
    queryset = KYCDocument.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get the KYC document object and check permissions"""
        document = super().get_object()
        # Check if the user owns the KYC request
        if document.kyc_request.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only delete your own KYC documents.")
        
        # Check if document is still pending (can't delete verified/rejected docs)
        if document.status in ['verified', 'rejected']:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(f"Cannot delete document with status: {document.get_status_display()}")
        
        return document
    
    def perform_destroy(self, instance):
        """Perform the deletion"""
        document_name = instance.document_name
        document_type = instance.get_document_type_display()
        
        # Delete the file from storage if it exists
        if instance.document_file:
            try:
                instance.document_file.delete(save=False)
            except Exception as e:
                # Log the error but don't fail the deletion
                pass
        
        instance.delete()
        return document_name, document_type
    
    def destroy(self, request, *args, **kwargs):
        """Handle DELETE request"""
        instance = self.get_object()
        document_name, document_type = self.perform_destroy(instance)
        
        return Response({
            'message': f'KYC document "{document_name}" ({document_type}) has been deleted successfully'
        }, status=status.HTTP_200_OK)


class KYCComplianceCheckListView(generics.ListAPIView):
    """List KYC compliance checks"""
    queryset = KYCComplianceCheck.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'message': 'KYC compliance checks will be implemented'})


class KYCComplianceCheckDetailView(generics.RetrieveAPIView):
    """Retrieve KYC compliance check details"""
    queryset = KYCComplianceCheck.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        return Response({'message': f'KYC compliance check {pk} details will be implemented'})


class KYCComplianceCheckUpdateView(generics.UpdateAPIView):
    """Update KYC compliance check"""
    queryset = KYCComplianceCheck.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self, request, pk):
        return Response({'message': f'KYC compliance check {pk} update will be implemented'})


class KYCReviewListView(generics.ListAPIView):
    """List KYC requests for review"""
    queryset = KYCRequest.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'message': 'KYC review list will be implemented'})


class KYCReviewDetailView(generics.RetrieveAPIView):
    """Retrieve KYC request for review"""
    queryset = KYCRequest.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        return Response({'message': f'KYC review {pk} details will be implemented'})


class KYCApproveView(APIView):
    """Approve KYC request"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        return Response({'message': f'KYC request {pk} approval will be implemented'})


class KYCRejectView(APIView):
    """Reject KYC request"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        return Response({'message': f'KYC request {pk} rejection will be implemented'})


class KYCRequestInfoView(APIView):
    """Request additional information for KYC"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        return Response({'message': f'KYC request {pk} additional info request will be implemented'})


class KYCStatusView(APIView):
    """Get KYC status"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'message': 'KYC status will be implemented'})


class KYCTrackingView(APIView):
    """Track KYC progress"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        return Response({'message': f'KYC tracking for {pk} will be implemented'})


class KYCAnalyticsView(APIView):
    """Get KYC analytics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'message': 'KYC analytics will be implemented'})


class KYCReportView(APIView):
    """Get KYC reports"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({'message': 'KYC reports will be implemented'})
