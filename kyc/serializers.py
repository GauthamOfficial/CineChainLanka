from rest_framework import serializers
from .models import (
    KYCRequest, KYCVerification, KYCDocument, KYCComplianceCheck
)
from users.serializers import UserSerializer


class KYCRequestSerializer(serializers.ModelSerializer):
    """Serializer for KYCRequest model"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = KYCRequest
        fields = [
            'id', 'user', 'verification_level', 'status', 'legal_name',
            'date_of_birth', 'nationality', 'residential_address',
            'identity_document_type', 'identity_document_number',
            'identity_document_expiry', 'address_proof_type',
            'address_proof_date', 'source_of_funds', 'annual_income',
            'employment_status', 'employer_name', 'political_exposure',
            'politically_exposed_person', 'sanctions_check',
            'submitted_at', 'reviewed_at', 'review_notes'
        ]
        read_only_fields = [
            'id', 'user', 'submitted_at', 'reviewed_at', 'review_notes'
        ]


class KYCDocumentSerializer(serializers.ModelSerializer):
    """Serializer for KYCDocument model"""
    kyc_request = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = KYCDocument
        fields = [
            'id', 'kyc_request', 'document_type', 'document_file',
            'document_name', 'document_number', 'issue_date',
            'expiry_date', 'issuing_authority', 'status',
            'verification_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'kyc_request', 'status', 'verification_notes',
            'created_at', 'updated_at'
        ]
    
    def validate_document_file(self, value):
        """Validate document file"""
        if value.size > 10 * 1024 * 1024:  # 10MB limit
            raise serializers.ValidationError("File size cannot exceed 10MB.")
        
        allowed_types = ['image/jpeg', 'image/png', 'application/pdf']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                "Only JPEG, PNG, and PDF files are allowed."
            )
        
        return value


class KYCDocumentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating KYC documents"""
    
    class Meta:
        model = KYCDocument
        fields = [
            'document_name', 'document_number', 'issue_date',
            'expiry_date', 'issuing_authority'
        ]
    
    def update(self, instance, validated_data):
        """Update KYC document instance"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class KYCVerificationSerializer(serializers.ModelSerializer):
    """Serializer for KYCVerification model"""
    kyc_request = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = KYCVerification
        fields = [
            'id', 'kyc_request', 'verification_type', 'status',
            'verification_method', 'verification_provider',
            'verification_reference', 'is_verified', 'confidence_score',
            'started_at', 'completed_at', 'notes', 'error_message'
        ]
        read_only_fields = [
            'id', 'kyc_request', 'started_at', 'completed_at'
        ]


class KYCComplianceCheckSerializer(serializers.ModelSerializer):
    """Serializer for KYCComplianceCheck model"""
    kyc_request = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = KYCComplianceCheck
        fields = [
            'id', 'kyc_request', 'check_type', 'status',
            'check_provider', 'check_reference', 'risk_score',
            'risk_level', 'initiated_at', 'completed_at',
            'notes', 'findings'
        ]
        read_only_fields = [
            'id', 'kyc_request', 'initiated_at', 'completed_at'
        ]
