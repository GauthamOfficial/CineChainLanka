from rest_framework import serializers
from .models import (
    Campaign, CampaignCategory, CampaignReward, 
    CampaignUpdate, CampaignComment
)
from users.serializers import UserSerializer


class CampaignCategorySerializer(serializers.ModelSerializer):
    """Serializer for CampaignCategory model"""
    
    class Meta:
        model = CampaignCategory
        fields = ['id', 'name', 'description', 'icon', 'is_active']


class CampaignRewardSerializer(serializers.ModelSerializer):
    """Serializer for CampaignReward model"""
    
    class Meta:
        model = CampaignReward
        fields = [
            'id', 'title', 'description', 'amount', 'max_backers', 
            'current_backers', 'estimated_delivery', 'is_active', 'created_at'
        ]


class CampaignSerializer(serializers.ModelSerializer):
    """Serializer for Campaign model"""
    creator = UserSerializer(read_only=True)
    category = CampaignCategorySerializer(read_only=True)
    rewards = CampaignRewardSerializer(many=True, read_only=True)
    
    class Meta:
        model = Campaign
        fields = [
            'id', 'title', 'subtitle', 'description', 'short_description',
            'category', 'creator', 'funding_goal', 'current_funding',
            'end_date', 'status', 'cover_image', 'created_at',
            'updated_at', 'rewards'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'current_funding']


class CampaignCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating campaigns"""
    
    class Meta:
        model = Campaign
        fields = [
            'title', 'subtitle', 'description', 'short_description',
            'category', 'funding_goal', 'end_date', 'cover_image'
        ]
    
    def validate_end_date(self, value):
        """Convert date string to datetime if needed"""
        from django.utils import timezone
        from datetime import datetime
        
        if isinstance(value, str):
            try:
                # Parse the date string and set time to end of day
                date_obj = datetime.strptime(value, '%Y-%m-%d')
                return timezone.make_aware(datetime.combine(date_obj.date(), datetime.max.time()))
            except ValueError:
                raise serializers.ValidationError("Invalid date format. Use YYYY-MM-DD.")
        return value
    
    def create(self, validated_data):
        from django.utils import timezone
        from datetime import timedelta
        
        validated_data['creator'] = self.context['request'].user
        # Set start_date to current time if not provided
        if 'start_date' not in validated_data:
            validated_data['start_date'] = timezone.now()
        # Set estimated_completion_date to end_date + 6 months if not provided
        if 'estimated_completion_date' not in validated_data:
            end_date = validated_data.get('end_date')
            if end_date:
                validated_data['estimated_completion_date'] = end_date.date() + timedelta(days=180)
        
        return super().create(validated_data)
    
    def to_representation(self, instance):
        """Return the full campaign representation after creation"""
        return CampaignSerializer(instance, context=self.context).data


class CampaignUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating campaigns"""
    
    class Meta:
        model = Campaign
        fields = [
            'title', 'subtitle', 'description', 'short_description',
            'category', 'funding_goal', 'funding_deadline', 'cover_image'
        ]


class CampaignUpdateModelSerializer(serializers.ModelSerializer):
    """Serializer for CampaignUpdate model"""
    
    class Meta:
        model = CampaignUpdate
        fields = [
            'id', 'title', 'content', 'is_public', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CampaignCommentSerializer(serializers.ModelSerializer):
    """Serializer for CampaignComment model"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = CampaignComment
        fields = [
            'id', 'content', 'user', 'is_public', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
