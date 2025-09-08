from rest_framework import serializers
from .models import PaymentMethod, Transaction, Contribution, Refund, PaymentProvider


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'name', 'payment_type', 'description', 
            'processing_fee_percentage', 'processing_fee_fixed',
            'minimum_amount', 'maximum_amount', 'is_active'
        ]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id', 'campaign', 'backer', 'amount', 'payment_method',
            'status', 'transaction_id', 'created_at', 'updated_at'
        ]


class ContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contribution
        fields = [
            'id', 'campaign', 'backer', 'amount', 'payment_method',
            'status', 'transaction_id', 'created_at', 'updated_at'
        ]


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = [
            'id', 'transaction', 'amount', 'reason', 'status',
            'processed_at', 'created_at', 'updated_at'
        ]


class PaymentProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentProvider
        fields = [
            'id', 'name', 'provider_type', 'is_active',
            'configuration', 'created_at', 'updated_at'
        ]
