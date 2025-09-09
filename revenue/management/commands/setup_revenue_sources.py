from django.core.management.base import BaseCommand
from django.conf import settings
from decimal import Decimal
from revenue.models import RevenueSource, OTTPlatformIntegration


class Command(BaseCommand):
    help = 'Setup default revenue sources and OTT platform integrations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing revenue sources and OTT platforms',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Resetting existing revenue sources and OTT platforms...')
            RevenueSource.objects.all().delete()
            OTTPlatformIntegration.objects.all().delete()

        # Create default revenue sources
        self.create_revenue_sources()
        
        # Create OTT platform integrations
        self.create_ott_platforms()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully setup revenue sources and OTT platforms')
        )

    def create_revenue_sources(self):
        """Create default revenue sources"""
        revenue_sources = [
            {
                'name': 'Box Office',
                'revenue_type': 'box_office',
                'description': 'Theatrical box office revenue',
                'token_address': getattr(settings, 'USDT_CONTRACT_ADDRESS', '0x0000000000000000000000000000000000000000'),
                'platform_fee_percentage': Decimal('5.00'),
                'creator_fee_percentage': Decimal('30.00'),
                'investor_fee_percentage': Decimal('65.00'),
            },
            {
                'name': 'Netflix',
                'revenue_type': 'ott_platform',
                'description': 'Netflix streaming revenue',
                'token_address': getattr(settings, 'USDT_CONTRACT_ADDRESS', '0x0000000000000000000000000000000000000000'),
                'platform_fee_percentage': Decimal('5.00'),
                'creator_fee_percentage': Decimal('30.00'),
                'investor_fee_percentage': Decimal('65.00'),
            },
            {
                'name': 'Amazon Prime Video',
                'revenue_type': 'ott_platform',
                'description': 'Amazon Prime Video streaming revenue',
                'token_address': getattr(settings, 'USDT_CONTRACT_ADDRESS', '0x0000000000000000000000000000000000000000'),
                'platform_fee_percentage': Decimal('5.00'),
                'creator_fee_percentage': Decimal('30.00'),
                'investor_fee_percentage': Decimal('65.00'),
            },
            {
                'name': 'Disney+',
                'revenue_type': 'ott_platform',
                'description': 'Disney+ streaming revenue',
                'token_address': getattr(settings, 'USDT_CONTRACT_ADDRESS', '0x0000000000000000000000000000000000000000'),
                'platform_fee_percentage': Decimal('5.00'),
                'creator_fee_percentage': Decimal('30.00'),
                'investor_fee_percentage': Decimal('65.00'),
            },
            {
                'name': 'HBO Max',
                'revenue_type': 'ott_platform',
                'description': 'HBO Max streaming revenue',
                'token_address': getattr(settings, 'USDT_CONTRACT_ADDRESS', '0x0000000000000000000000000000000000000000'),
                'platform_fee_percentage': Decimal('5.00'),
                'creator_fee_percentage': Decimal('30.00'),
                'investor_fee_percentage': Decimal('65.00'),
            },
            {
                'name': 'Paramount+',
                'revenue_type': 'ott_platform',
                'description': 'Paramount+ streaming revenue',
                'token_address': getattr(settings, 'USDT_CONTRACT_ADDRESS', '0x0000000000000000000000000000000000000000'),
                'platform_fee_percentage': Decimal('5.00'),
                'creator_fee_percentage': Decimal('30.00'),
                'investor_fee_percentage': Decimal('65.00'),
            },
            {
                'name': 'DVD Sales',
                'revenue_type': 'dvd_sales',
                'description': 'Physical DVD and Blu-ray sales',
                'token_address': getattr(settings, 'USDT_CONTRACT_ADDRESS', '0x0000000000000000000000000000000000000000'),
                'platform_fee_percentage': Decimal('5.00'),
                'creator_fee_percentage': Decimal('30.00'),
                'investor_fee_percentage': Decimal('65.00'),
            },
            {
                'name': 'Merchandise',
                'revenue_type': 'merchandise',
                'description': 'Film merchandise and licensing revenue',
                'token_address': getattr(settings, 'USDT_CONTRACT_ADDRESS', '0x0000000000000000000000000000000000000000'),
                'platform_fee_percentage': Decimal('5.00'),
                'creator_fee_percentage': Decimal('30.00'),
                'investor_fee_percentage': Decimal('65.00'),
            },
        ]

        for source_data in revenue_sources:
            source, created = RevenueSource.objects.get_or_create(
                name=source_data['name'],
                defaults=source_data
            )
            if created:
                self.stdout.write(f'Created revenue source: {source.name}')
            else:
                self.stdout.write(f'Revenue source already exists: {source.name}')

    def create_ott_platforms(self):
        """Create OTT platform integrations"""
        ott_platforms = [
            {
                'name': 'Netflix',
                'platform_type': 'netflix',
                'api_endpoint': 'https://api.netflix.com/v1/revenue',
                'webhook_url': 'https://your-domain.com/api/revenue/webhooks/netflix/',
                'is_active': True,
            },
            {
                'name': 'Amazon Prime Video',
                'platform_type': 'amazon_prime',
                'api_endpoint': 'https://api.amazon.com/prime-video/revenue',
                'webhook_url': 'https://your-domain.com/api/revenue/webhooks/amazon-prime/',
                'is_active': True,
            },
            {
                'name': 'Disney+',
                'platform_type': 'disney_plus',
                'api_endpoint': 'https://api.disney.com/plus/revenue',
                'webhook_url': 'https://your-domain.com/api/revenue/webhooks/disney-plus/',
                'is_active': True,
            },
            {
                'name': 'HBO Max',
                'platform_type': 'hbo_max',
                'api_endpoint': 'https://api.hbomax.com/revenue',
                'webhook_url': 'https://your-domain.com/api/revenue/webhooks/ott/1/',
                'is_active': True,
            },
            {
                'name': 'Paramount+',
                'platform_type': 'paramount_plus',
                'api_endpoint': 'https://api.paramountplus.com/revenue',
                'webhook_url': 'https://your-domain.com/api/revenue/webhooks/ott/2/',
                'is_active': True,
            },
        ]

        for platform_data in ott_platforms:
            platform, created = OTTPlatformIntegration.objects.get_or_create(
                name=platform_data['name'],
                defaults=platform_data
            )
            if created:
                self.stdout.write(f'Created OTT platform: {platform.name}')
            else:
                self.stdout.write(f'OTT platform already exists: {platform.name}')
