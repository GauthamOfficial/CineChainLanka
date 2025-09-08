from rest_framework import serializers
from .models import (
    FundingRound, FundingMilestone, FundingAllocation,
    FundingProgress, FundingAnalytics
)
from campaigns.serializers import CampaignSerializer


class FundingRoundSerializer(serializers.ModelSerializer):
    """Serializer for FundingRound model"""
    campaign = CampaignSerializer(read_only=True)
    
    class Meta:
        model = FundingRound
        fields = [
            'id', 'campaign', 'round_type', 'title', 'description',
            'funding_goal', 'current_funding', 'start_date', 'end_date',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'campaign', 'current_funding', 'created_at', 'updated_at'
        ]
    
    def validate(self, data):
        """Validate funding round data"""
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError(
                    "End date must be after start date."
                )
        return data


class FundingRoundUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating funding rounds"""
    
    class Meta:
        model = FundingRound
        fields = [
            'title', 'description', 'funding_goal', 'start_date', 'end_date', 'is_active'
        ]
    
    def validate(self, data):
        """Validate funding round update data"""
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError(
                    "End date must be after start date."
                )
        return data
    
    def update(self, instance, validated_data):
        """Update funding round instance"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class FundingMilestoneSerializer(serializers.ModelSerializer):
    """Serializer for FundingMilestone model"""
    campaign = CampaignSerializer(read_only=True)
    
    class Meta:
        model = FundingMilestone
        fields = [
            'id', 'campaign', 'title', 'description', 'funding_target',
            'is_achieved', 'achieved_at', 'order', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'campaign', 'is_achieved', 'achieved_at', 'created_at', 'updated_at'
        ]


class FundingAllocationSerializer(serializers.ModelSerializer):
    """Serializer for FundingAllocation model"""
    campaign = CampaignSerializer(read_only=True)
    
    class Meta:
        model = FundingAllocation
        fields = [
            'id', 'campaign', 'allocation_type', 'description',
            'budgeted_amount', 'actual_amount', 'percentage_of_total',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'campaign', 'actual_amount', 'created_at', 'updated_at'
        ]
    
    def validate_percentage_of_total(self, value):
        """Validate percentage is between 0 and 100"""
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Percentage must be between 0 and 100."
            )
        return value


class FundingAllocationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating funding allocations"""
    
    class Meta:
        model = FundingAllocation
        fields = [
            'description', 'budgeted_amount', 'percentage_of_total'
        ]
    
    def validate_percentage_of_total(self, value):
        """Validate percentage is between 0 and 100"""
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Percentage must be between 0 and 100."
            )
        return value
    
    def update(self, instance, validated_data):
        """Update funding allocation instance"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class FundingProgressSerializer(serializers.ModelSerializer):
    """Serializer for FundingProgress model"""
    campaign = CampaignSerializer(read_only=True)
    
    class Meta:
        model = FundingProgress
        fields = [
            'id', 'campaign', 'date', 'total_funding', 'daily_funding',
            'backer_count', 'new_backers', 'created_at'
        ]
        read_only_fields = [
            'id', 'campaign', 'created_at'
        ]


class FundingAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for FundingAnalytics model"""
    campaign = CampaignSerializer(read_only=True)
    
    class Meta:
        model = FundingAnalytics
        fields = [
            'id', 'campaign', 'total_contributions', 'average_contribution',
            'median_contribution', 'largest_contribution', 'unique_backers',
            'repeat_backers', 'new_backers', 'view_to_backer_rate',
            'top_locations', 'payment_method_distribution',
            'peak_funding_day', 'peak_funding_amount',
            'projected_completion_date', 'funding_velocity',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'campaign', 'created_at', 'updated_at'
        ]
