from django.core.management.base import BaseCommand
from payments.models import PaymentMethod


class Command(BaseCommand):
    help = 'Populate payment methods for the platform'

    def handle(self, *args, **options):
        payment_methods = [
            {
                'name': 'LankaQR',
                'payment_type': 'lanka_qr',
                'description': 'Scan QR code with your mobile banking app',
                'processing_fee_percentage': 0.5,
                'processing_fee_fixed': 5.00,
                'minimum_amount': 10.00,
                'maximum_amount': 100000.00,
                'is_active': True,
            },
            {
                'name': 'eZ Cash',
                'payment_type': 'ez_cash',
                'description': 'Pay using Dialog eZ Cash mobile wallet',
                'processing_fee_percentage': 1.0,
                'processing_fee_fixed': 2.00,
                'minimum_amount': 5.00,
                'maximum_amount': 50000.00,
                'is_active': True,
            },
            {
                'name': 'FriMi',
                'payment_type': 'frimi',
                'description': 'Pay using FriMi mobile wallet',
                'processing_fee_percentage': 1.0,
                'processing_fee_fixed': 2.00,
                'minimum_amount': 5.00,
                'maximum_amount': 50000.00,
                'is_active': True,
            },
            {
                'name': 'Bank Transfer',
                'payment_type': 'bank_transfer',
                'description': 'Direct bank transfer to our account',
                'processing_fee_percentage': 0.0,
                'processing_fee_fixed': 0.00,
                'minimum_amount': 100.00,
                'maximum_amount': 1000000.00,
                'is_active': True,
            },
            {
                'name': 'Credit Card',
                'payment_type': 'credit_card',
                'description': 'Pay with your credit card',
                'processing_fee_percentage': 2.5,
                'processing_fee_fixed': 10.00,
                'minimum_amount': 50.00,
                'maximum_amount': 200000.00,
                'is_active': True,
            },
            {
                'name': 'Debit Card',
                'payment_type': 'debit_card',
                'description': 'Pay with your debit card',
                'processing_fee_percentage': 2.0,
                'processing_fee_fixed': 5.00,
                'minimum_amount': 25.00,
                'maximum_amount': 100000.00,
                'is_active': True,
            },
            {
                'name': 'USDT (Cryptocurrency)',
                'payment_type': 'crypto',
                'description': 'Pay using USDT cryptocurrency',
                'processing_fee_percentage': 0.1,
                'processing_fee_fixed': 0.00,
                'minimum_amount': 1.00,
                'maximum_amount': 100000.00,
                'is_active': True,
            },
        ]

        created_count = 0
        for method_data in payment_methods:
            method, created = PaymentMethod.objects.get_or_create(
                name=method_data['name'],
                defaults=method_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created payment method: {method.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Payment method already exists: {method.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} payment methods')
        )
