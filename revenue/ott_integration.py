import logging
import requests
import json
from decimal import Decimal
from typing import Dict, List, Optional, Any
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    OTTPlatformIntegration, RevenueEntry, RevenueWebhook, 
    RevenueSource, Campaign
)
from django.conf import settings

logger = logging.getLogger(__name__)


class OTTIntegrationService:
    """Service for OTT platform integrations"""
    
    def __init__(self):
        self.platforms = OTTPlatformIntegration.objects.filter(is_active=True)
    
    def process_webhook(self, platform_name: str, payload: Dict) -> bool:
        """Process webhook from OTT platform"""
        try:
            platform = self.platforms.filter(name=platform_name).first()
            if not platform:
                logger.error(f"Platform not found: {platform_name}")
                return False
            
            # Create webhook record
            webhook = RevenueWebhook.objects.create(
                platform=platform,
                campaign_id=payload.get('campaign_id'),
                payload=payload,
                status='pending'
            )
            
            # Process based on platform type
            if platform.platform_type == 'netflix':
                return self._process_netflix_webhook(webhook, payload)
            elif platform.platform_type == 'amazon_prime':
                return self._process_amazon_prime_webhook(webhook, payload)
            elif platform.platform_type == 'disney_plus':
                return self._process_disney_plus_webhook(webhook, payload)
            else:
                return self._process_generic_webhook(webhook, payload)
                
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return False
    
    def _process_netflix_webhook(self, webhook: RevenueWebhook, payload: Dict) -> bool:
        """Process Netflix webhook"""
        try:
            # Extract revenue data from Netflix payload
            revenue_data = payload.get('revenue_data', {})
            campaign_id = payload.get('campaign_id')
            
            if not campaign_id or not revenue_data:
                webhook.status = 'failed'
                webhook.response_message = "Missing campaign_id or revenue_data"
                webhook.save()
                return False
            
            # Get or create Netflix revenue source
            source, created = RevenueSource.objects.get_or_create(
                name='Netflix',
                revenue_type='ott_platform',
                defaults={
                    'description': 'Netflix streaming revenue',
                    'platform_fee_percentage': Decimal('5.00'),
                    'creator_fee_percentage': Decimal('30.00'),
                    'investor_fee_percentage': Decimal('65.00'),
                }
            )
            
            # Create revenue entries
            for entry_data in revenue_data.get('entries', []):
                RevenueEntry.objects.create(
                    campaign_id=campaign_id,
                    source=source,
                    amount=Decimal(str(entry_data.get('amount', 0))),
                    currency=entry_data.get('currency', 'USDT'),
                    description=f"Netflix revenue - {entry_data.get('title', 'Unknown')}",
                    revenue_date=datetime.fromisoformat(entry_data.get('date', timezone.now().isoformat())),
                    status='verified'  # Netflix data is pre-verified
                )
            
            webhook.status = 'processed'
            webhook.processed_at = timezone.now()
            webhook.save()
            
            logger.info(f"Netflix webhook processed: {webhook.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing Netflix webhook: {e}")
            webhook.status = 'failed'
            webhook.response_message = str(e)
            webhook.save()
            return False
    
    def _process_amazon_prime_webhook(self, webhook: RevenueWebhook, payload: Dict) -> bool:
        """Process Amazon Prime webhook"""
        try:
            revenue_data = payload.get('revenue_data', {})
            campaign_id = payload.get('campaign_id')
            
            if not campaign_id or not revenue_data:
                webhook.status = 'failed'
                webhook.response_message = "Missing campaign_id or revenue_data"
                webhook.save()
                return False
            
            # Get or create Amazon Prime revenue source
            source, created = RevenueSource.objects.get_or_create(
                name='Amazon Prime',
                revenue_type='ott_platform',
                defaults={
                    'description': 'Amazon Prime Video revenue',
                    'platform_fee_percentage': Decimal('4.50'),
                    'creator_fee_percentage': Decimal('30.00'),
                    'investor_fee_percentage': Decimal('65.50'),
                }
            )
            
            # Create revenue entries
            for entry_data in revenue_data.get('entries', []):
                RevenueEntry.objects.create(
                    campaign_id=campaign_id,
                    source=source,
                    amount=Decimal(str(entry_data.get('amount', 0))),
                    currency=entry_data.get('currency', 'USDT'),
                    description=f"Amazon Prime revenue - {entry_data.get('title', 'Unknown')}",
                    revenue_date=datetime.fromisoformat(entry_data.get('date', timezone.now().isoformat())),
                    status='verified'
                )
            
            webhook.status = 'processed'
            webhook.processed_at = timezone.now()
            webhook.save()
            
            logger.info(f"Amazon Prime webhook processed: {webhook.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing Amazon Prime webhook: {e}")
            webhook.status = 'failed'
            webhook.response_message = str(e)
            webhook.save()
            return False
    
    def _process_disney_plus_webhook(self, webhook: RevenueWebhook, payload: Dict) -> bool:
        """Process Disney+ webhook"""
        try:
            revenue_data = payload.get('revenue_data', {})
            campaign_id = payload.get('campaign_id')
            
            if not campaign_id or not revenue_data:
                webhook.status = 'failed'
                webhook.response_message = "Missing campaign_id or revenue_data"
                webhook.save()
                return False
            
            # Get or create Disney+ revenue source
            source, created = RevenueSource.objects.get_or_create(
                name='Disney+',
                revenue_type='ott_platform',
                defaults={
                    'description': 'Disney+ streaming revenue',
                    'platform_fee_percentage': Decimal('6.00'),
                    'creator_fee_percentage': Decimal('30.00'),
                    'investor_fee_percentage': Decimal('64.00'),
                }
            )
            
            # Create revenue entries
            for entry_data in revenue_data.get('entries', []):
                RevenueEntry.objects.create(
                    campaign_id=campaign_id,
                    source=source,
                    amount=Decimal(str(entry_data.get('amount', 0))),
                    currency=entry_data.get('currency', 'USDT'),
                    description=f"Disney+ revenue - {entry_data.get('title', 'Unknown')}",
                    revenue_date=datetime.fromisoformat(entry_data.get('date', timezone.now().isoformat())),
                    status='verified'
                )
            
            webhook.status = 'processed'
            webhook.processed_at = timezone.now()
            webhook.save()
            
            logger.info(f"Disney+ webhook processed: {webhook.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing Disney+ webhook: {e}")
            webhook.status = 'failed'
            webhook.response_message = str(e)
            webhook.save()
            return False
    
    def _process_generic_webhook(self, webhook: RevenueWebhook, payload: Dict) -> bool:
        """Process generic OTT webhook"""
        try:
            revenue_data = payload.get('revenue_data', {})
            campaign_id = payload.get('campaign_id')
            platform_name = webhook.platform.name
            
            if not campaign_id or not revenue_data:
                webhook.status = 'failed'
                webhook.response_message = "Missing campaign_id or revenue_data"
                webhook.save()
                return False
            
            # Get or create generic revenue source
            source, created = RevenueSource.objects.get_or_create(
                name=platform_name,
                revenue_type='ott_platform',
                defaults={
                    'description': f'{platform_name} streaming revenue',
                    'platform_fee_percentage': Decimal('5.00'),
                    'creator_fee_percentage': Decimal('30.00'),
                    'investor_fee_percentage': Decimal('65.00'),
                }
            )
            
            # Create revenue entries
            for entry_data in revenue_data.get('entries', []):
                RevenueEntry.objects.create(
                    campaign_id=campaign_id,
                    source=source,
                    amount=Decimal(str(entry_data.get('amount', 0))),
                    currency=entry_data.get('currency', 'USDT'),
                    description=f"{platform_name} revenue - {entry_data.get('title', 'Unknown')}",
                    revenue_date=datetime.fromisoformat(entry_data.get('date', timezone.now().isoformat())),
                    status='pending'  # Generic webhooks need verification
                )
            
            webhook.status = 'processed'
            webhook.processed_at = timezone.now()
            webhook.save()
            
            logger.info(f"Generic webhook processed: {webhook.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing generic webhook: {e}")
            webhook.status = 'failed'
            webhook.response_message = str(e)
            webhook.save()
            return False
    
    def sync_revenue_data(self, platform_name: str, campaign_id: int) -> bool:
        """Sync revenue data from OTT platform API"""
        try:
            platform = self.platforms.filter(name=platform_name).first()
            if not platform or not platform.api_endpoint:
                logger.error(f"Platform not found or no API endpoint: {platform_name}")
                return False
            
            # Make API request to platform
            headers = {
                'Authorization': f'Bearer {platform.api_key}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'campaign_id': campaign_id,
                'start_date': (timezone.now() - timedelta(days=30)).isoformat(),
                'end_date': timezone.now().isoformat()
            }
            
            response = requests.get(
                platform.api_endpoint,
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"API request failed: {response.status_code}")
                return False
            
            data = response.json()
            
            # Process the response as webhook
            webhook_payload = {
                'campaign_id': campaign_id,
                'revenue_data': data.get('revenue_data', [])
            }
            
            return self.process_webhook(platform_name, webhook_payload)
            
        except Exception as e:
            logger.error(f"Error syncing revenue data: {e}")
            return False
    
    def get_platform_revenue_summary(self, platform_name: str, days: int = 30) -> Dict:
        """Get revenue summary for a platform"""
        try:
            platform = self.platforms.filter(name=platform_name).first()
            if not platform:
                return {}
            
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)
            
            # Get revenue entries for this platform
            revenue_entries = RevenueEntry.objects.filter(
                source__name=platform_name,
                revenue_date__range=[start_date, end_date],
                status__in=['verified', 'processed']
            )
            
            total_revenue = revenue_entries.aggregate(
                total=models.Sum('amount')
            )['total'] or Decimal('0')
            
            total_entries = revenue_entries.count()
            
            # Get campaign breakdown
            campaign_breakdown = revenue_entries.values('campaign__title').annotate(
                total=Sum('amount'),
                count=Count('id')
            ).order_by('-total')
            
            return {
                'platform_name': platform_name,
                'total_revenue': total_revenue,
                'total_entries': total_entries,
                'period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'days': days
                },
                'campaign_breakdown': list(campaign_breakdown)
            }
            
        except Exception as e:
            logger.error(f"Error getting platform revenue summary: {e}")
            return {}
    
    def create_platform_integration(
        self,
        name: str,
        platform_type: str,
        api_endpoint: str = None,
        api_key: str = None,
        webhook_url: str = None
    ) -> OTTPlatformIntegration:
        """Create a new OTT platform integration"""
        try:
            platform = OTTPlatformIntegration.objects.create(
                name=name,
                platform_type=platform_type,
                api_endpoint=api_endpoint,
                api_key=api_key,
                webhook_url=webhook_url
            )
            
            logger.info(f"Platform integration created: {platform.id}")
            return platform
            
        except Exception as e:
            logger.error(f"Error creating platform integration: {e}")
            raise
    
    def test_platform_connection(self, platform_id: int) -> bool:
        """Test connection to OTT platform"""
        try:
            platform = OTTPlatformIntegration.objects.get(id=platform_id)
            
            if not platform.api_endpoint or not platform.api_key:
                return False
            
            headers = {
                'Authorization': f'Bearer {platform.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{platform.api_endpoint}/test",
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error testing platform connection: {e}")
            return False


class BoxOfficeIntegrationService:
    """Service for box office revenue integration"""
    
    def __init__(self):
        self.box_office_source = self._get_or_create_box_office_source()
    
    def _get_or_create_box_office_source(self) -> RevenueSource:
        """Get or create box office revenue source"""
        source, created = RevenueSource.objects.get_or_create(
            name='Box Office',
            revenue_type='box_office',
            defaults={
                'description': 'Box office ticket sales revenue',
                'platform_fee_percentage': Decimal('3.00'),
                'creator_fee_percentage': Decimal('35.00'),
                'investor_fee_percentage': Decimal('62.00'),
            }
        )
        return source
    
    def add_box_office_revenue(
        self,
        campaign_id: int,
        amount: Decimal,
        currency: str,
        description: str,
        revenue_date: datetime,
        verification_document=None
    ) -> RevenueEntry:
        """Add box office revenue entry"""
        try:
            revenue_entry = RevenueEntry.objects.create(
                campaign_id=campaign_id,
                source=self.box_office_source,
                amount=amount,
                currency=currency,
                description=description,
                revenue_date=revenue_date,
                verification_document=verification_document,
                status='pending'
            )
            
            logger.info(f"Box office revenue added: {revenue_entry.id}")
            return revenue_entry
            
        except Exception as e:
            logger.error(f"Error adding box office revenue: {e}")
            raise
    
    def sync_cinema_revenue(self, campaign_id: int, cinema_data: List[Dict]) -> bool:
        """Sync revenue from multiple cinemas"""
        try:
            total_revenue = Decimal('0')
            
            for cinema in cinema_data:
                amount = Decimal(str(cinema.get('revenue', 0)))
                total_revenue += amount
                
                RevenueEntry.objects.create(
                    campaign_id=campaign_id,
                    source=self.box_office_source,
                    amount=amount,
                    currency=cinema.get('currency', 'LKR'),
                    description=f"Box office revenue - {cinema.get('cinema_name', 'Unknown Cinema')}",
                    revenue_date=datetime.fromisoformat(cinema.get('date', timezone.now().isoformat())),
                    status='pending'
                )
            
            logger.info(f"Synced cinema revenue for campaign {campaign_id}: {total_revenue}")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing cinema revenue: {e}")
            return False