import logging
import requests
import json
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import (
    OTTPlatformIntegration, RevenueWebhook, RevenueEntry, 
    RevenueSource, Campaign
)

logger = logging.getLogger(__name__)


class OTTIntegrationService:
    """Service for OTT platform revenue integration"""
    
    def __init__(self):
        self.platforms = OTTPlatformIntegration.objects.filter(is_active=True)
    
    def process_webhook(self, platform_id: int, payload: Dict[str, Any]) -> bool:
        """Process incoming webhook from OTT platform"""
        try:
            platform = OTTPlatformIntegration.objects.get(id=platform_id)
            
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
    
    def _process_netflix_webhook(self, webhook: RevenueWebhook, payload: Dict[str, Any]) -> bool:
        """Process Netflix revenue webhook"""
        try:
            # Extract revenue data from Netflix payload
            revenue_data = payload.get('revenue_data', {})
            campaign_id = payload.get('campaign_id')
            
            if not campaign_id or not revenue_data:
                webhook.status = 'failed'
                webhook.response_message = 'Missing campaign_id or revenue_data'
                webhook.save()
                return False
            
            # Get or create Netflix revenue source
            source, created = RevenueSource.objects.get_or_create(
                name='Netflix',
                revenue_type='ott_platform',
                defaults={
                    'token_address': settings.USDT_CONTRACT_ADDRESS,
                    'platform_fee_percentage': Decimal('5.00'),
                    'creator_fee_percentage': Decimal('30.00'),
                    'investor_fee_percentage': Decimal('65.00'),
                    'is_active': True
                }
            )
            
            # Create revenue entry
            revenue_entry = RevenueEntry.objects.create(
                campaign_id=campaign_id,
                source=source,
                amount=Decimal(str(revenue_data.get('amount', 0))),
                currency=revenue_data.get('currency', 'USDT'),
                description=f"Netflix streaming revenue - {revenue_data.get('period', 'Unknown period')}",
                revenue_date=datetime.fromisoformat(revenue_data.get('date', timezone.now().isoformat())).date(),
                status='verified'  # Netflix data is considered verified
            )
            
            webhook.status = 'processed'
            webhook.processed_at = timezone.now()
            webhook.save()
            
            logger.info(f"Netflix webhook processed successfully: {webhook.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing Netflix webhook: {e}")
            webhook.status = 'failed'
            webhook.response_message = str(e)
            webhook.save()
            return False
    
    def _process_amazon_prime_webhook(self, webhook: RevenueWebhook, payload: Dict[str, Any]) -> bool:
        """Process Amazon Prime revenue webhook"""
        try:
            revenue_data = payload.get('revenue_data', {})
            campaign_id = payload.get('campaign_id')
            
            if not campaign_id or not revenue_data:
                webhook.status = 'failed'
                webhook.response_message = 'Missing campaign_id or revenue_data'
                webhook.save()
                return False
            
            # Get or create Amazon Prime revenue source
            source, created = RevenueSource.objects.get_or_create(
                name='Amazon Prime Video',
                revenue_type='ott_platform',
                defaults={
                    'token_address': settings.USDT_CONTRACT_ADDRESS,
                    'platform_fee_percentage': Decimal('5.00'),
                    'creator_fee_percentage': Decimal('30.00'),
                    'investor_fee_percentage': Decimal('65.00'),
                    'is_active': True
                }
            )
            
            # Create revenue entry
            revenue_entry = RevenueEntry.objects.create(
                campaign_id=campaign_id,
                source=source,
                amount=Decimal(str(revenue_data.get('amount', 0))),
                currency=revenue_data.get('currency', 'USDT'),
                description=f"Amazon Prime Video revenue - {revenue_data.get('period', 'Unknown period')}",
                revenue_date=datetime.fromisoformat(revenue_data.get('date', timezone.now().isoformat())).date(),
                status='verified'
            )
            
            webhook.status = 'processed'
            webhook.processed_at = timezone.now()
            webhook.save()
            
            logger.info(f"Amazon Prime webhook processed successfully: {webhook.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing Amazon Prime webhook: {e}")
            webhook.status = 'failed'
            webhook.response_message = str(e)
            webhook.save()
            return False
    
    def _process_disney_plus_webhook(self, webhook: RevenueWebhook, payload: Dict[str, Any]) -> bool:
        """Process Disney+ revenue webhook"""
        try:
            revenue_data = payload.get('revenue_data', {})
            campaign_id = payload.get('campaign_id')
            
            if not campaign_id or not revenue_data:
                webhook.status = 'failed'
                webhook.response_message = 'Missing campaign_id or revenue_data'
                webhook.save()
                return False
            
            # Get or create Disney+ revenue source
            source, created = RevenueSource.objects.get_or_create(
                name='Disney+',
                revenue_type='ott_platform',
                defaults={
                    'token_address': settings.USDT_CONTRACT_ADDRESS,
                    'platform_fee_percentage': Decimal('5.00'),
                    'creator_fee_percentage': Decimal('30.00'),
                    'investor_fee_percentage': Decimal('65.00'),
                    'is_active': True
                }
            )
            
            # Create revenue entry
            revenue_entry = RevenueEntry.objects.create(
                campaign_id=campaign_id,
                source=source,
                amount=Decimal(str(revenue_data.get('amount', 0))),
                currency=revenue_data.get('currency', 'USDT'),
                description=f"Disney+ streaming revenue - {revenue_data.get('period', 'Unknown period')}",
                revenue_date=datetime.fromisoformat(revenue_data.get('date', timezone.now().isoformat())).date(),
                status='verified'
            )
            
            webhook.status = 'processed'
            webhook.processed_at = timezone.now()
            webhook.save()
            
            logger.info(f"Disney+ webhook processed successfully: {webhook.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing Disney+ webhook: {e}")
            webhook.status = 'failed'
            webhook.response_message = str(e)
            webhook.save()
            return False
    
    def _process_generic_webhook(self, webhook: RevenueWebhook, payload: Dict[str, Any]) -> bool:
        """Process generic OTT platform webhook"""
        try:
            revenue_data = payload.get('revenue_data', {})
            campaign_id = payload.get('campaign_id')
            platform_name = webhook.platform.name
            
            if not campaign_id or not revenue_data:
                webhook.status = 'failed'
                webhook.response_message = 'Missing campaign_id or revenue_data'
                webhook.save()
                return False
            
            # Get or create generic revenue source
            source, created = RevenueSource.objects.get_or_create(
                name=platform_name,
                revenue_type='ott_platform',
                defaults={
                    'token_address': settings.USDT_CONTRACT_ADDRESS,
                    'platform_fee_percentage': Decimal('5.00'),
                    'creator_fee_percentage': Decimal('30.00'),
                    'investor_fee_percentage': Decimal('65.00'),
                    'is_active': True
                }
            )
            
            # Create revenue entry
            revenue_entry = RevenueEntry.objects.create(
                campaign_id=campaign_id,
                source=source,
                amount=Decimal(str(revenue_data.get('amount', 0))),
                currency=revenue_data.get('currency', 'USDT'),
                description=f"{platform_name} revenue - {revenue_data.get('period', 'Unknown period')}",
                revenue_date=datetime.fromisoformat(revenue_data.get('date', timezone.now().isoformat())).date(),
                status='verified'
            )
            
            webhook.status = 'processed'
            webhook.processed_at = timezone.now()
            webhook.save()
            
            logger.info(f"Generic webhook processed successfully: {webhook.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing generic webhook: {e}")
            webhook.status = 'failed'
            webhook.response_message = str(e)
            webhook.save()
            return False
    
    def sync_revenue_data(self, platform_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Sync revenue data from OTT platform API"""
        try:
            platform = OTTPlatformIntegration.objects.get(id=platform_id)
            
            # This would integrate with actual OTT platform APIs
            # For now, we'll return a mock response
            return {
                'status': 'success',
                'platform': platform.name,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'revenue_entries_created': 0,
                'total_revenue': 0
            }
            
        except Exception as e:
            logger.error(f"Error syncing revenue data: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_platform_revenue_summary(self, platform_id: int, days: int = 30) -> Dict[str, Any]:
        """Get revenue summary for a specific platform"""
        try:
            platform = OTTPlatformIntegration.objects.get(id=platform_id)
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)
            
            # Get revenue entries for this platform
            revenue_entries = RevenueEntry.objects.filter(
                source__name=platform.name,
                revenue_date__range=[start_date, end_date],
                status__in=['verified', 'processed']
            )
            
            total_revenue = sum(entry.amount for entry in revenue_entries)
            entry_count = revenue_entries.count()
            
            # Get campaigns with revenue from this platform
            campaigns = Campaign.objects.filter(
                revenue_entries__source__name=platform.name,
                revenue_entries__revenue_date__range=[start_date, end_date]
            ).distinct()
            
            return {
                'platform_name': platform.name,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                },
                'total_revenue': float(total_revenue),
                'entry_count': entry_count,
                'campaign_count': campaigns.count(),
                'average_revenue_per_entry': float(total_revenue / entry_count) if entry_count > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting platform revenue summary: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }


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
                'token_address': settings.USDT_CONTRACT_ADDRESS,
                'platform_fee_percentage': Decimal('5.00'),
                'creator_fee_percentage': Decimal('30.00'),
                'investor_fee_percentage': Decimal('65.00'),
                'is_active': True
            }
        )
        return source
    
    def record_box_office_revenue(
        self,
        campaign_id: int,
        amount: Decimal,
        currency: str,
        description: str,
        revenue_date: datetime,
        verification_document=None
    ) -> RevenueEntry:
        """Record box office revenue"""
        try:
            revenue_entry = RevenueEntry.objects.create(
                campaign_id=campaign_id,
                source=self.box_office_source,
                amount=amount,
                currency=currency,
                description=description,
                revenue_date=revenue_date.date(),
                verification_document=verification_document,
                status='pending'  # Box office revenue needs verification
            )
            
            logger.info(f"Box office revenue recorded: {revenue_entry.id}")
            return revenue_entry
            
        except Exception as e:
            logger.error(f"Error recording box office revenue: {e}")
            raise
    
    def get_box_office_summary(self, campaign_id: int) -> Dict[str, Any]:
        """Get box office revenue summary for a campaign"""
        try:
            campaign = Campaign.objects.get(id=campaign_id)
            
            # Get box office revenue entries
            revenue_entries = RevenueEntry.objects.filter(
                campaign=campaign,
                source=self.box_office_source,
                status__in=['verified', 'processed']
            )
            
            total_revenue = sum(entry.amount for entry in revenue_entries)
            entry_count = revenue_entries.count()
            
            # Get daily breakdown
            daily_revenue = {}
            for entry in revenue_entries:
                date_str = entry.revenue_date.isoformat()
                if date_str in daily_revenue:
                    daily_revenue[date_str] += float(entry.amount)
                else:
                    daily_revenue[date_str] = float(entry.amount)
            
            return {
                'campaign_id': campaign_id,
                'campaign_title': campaign.title,
                'total_revenue': float(total_revenue),
                'entry_count': entry_count,
                'daily_revenue': daily_revenue,
                'average_daily_revenue': float(total_revenue / len(daily_revenue)) if daily_revenue else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting box office summary: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
