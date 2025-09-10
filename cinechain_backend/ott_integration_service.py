"""
OTT Platform Integration Service for CineChainLanka
Handles integration with global OTT platforms for revenue sharing
"""

import logging
import requests
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.core.cache import cache
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class OTTIntegrationService:
    """
    Service for integrating with OTT platforms
    """
    
    # Supported OTT platforms
    OTT_PLATFORMS = {
        'netflix': {
            'name': 'Netflix',
            'api_base_url': 'https://api.netflix.com/v1',
            'revenue_share_percentage': 0.15,  # 15%
            'minimum_revenue_threshold': 1000,  # USD
            'payment_frequency': 'monthly',
            'supported_regions': ['US', 'UK', 'CA', 'AU', 'SG', 'LK'],
            'content_categories': ['movies', 'series', 'documentaries'],
            'api_version': 'v1.0'
        },
        'amazon_prime': {
            'name': 'Amazon Prime Video',
            'api_base_url': 'https://api.primevideo.com/v1',
            'revenue_share_percentage': 0.12,  # 12%
            'minimum_revenue_threshold': 500,  # USD
            'payment_frequency': 'monthly',
            'supported_regions': ['US', 'UK', 'CA', 'AU', 'SG', 'LK', 'IN'],
            'content_categories': ['movies', 'series', 'originals'],
            'api_version': 'v1.0'
        },
        'disney_plus': {
            'name': 'Disney+',
            'api_base_url': 'https://api.disneyplus.com/v1',
            'revenue_share_percentage': 0.18,  # 18%
            'minimum_revenue_threshold': 2000,  # USD
            'payment_frequency': 'quarterly',
            'supported_regions': ['US', 'UK', 'CA', 'AU', 'SG', 'LK'],
            'content_categories': ['movies', 'series', 'originals', 'documentaries'],
            'api_version': 'v1.0'
        },
        'hbo_max': {
            'name': 'HBO Max',
            'api_base_url': 'https://api.hbomax.com/v1',
            'revenue_share_percentage': 0.14,  # 14%
            'minimum_revenue_threshold': 1500,  # USD
            'payment_frequency': 'monthly',
            'supported_regions': ['US', 'UK', 'CA', 'AU', 'SG'],
            'content_categories': ['movies', 'series', 'originals'],
            'api_version': 'v1.0'
        },
        'paramount_plus': {
            'name': 'Paramount+',
            'api_base_url': 'https://api.paramountplus.com/v1',
            'revenue_share_percentage': 0.13,  # 13%
            'minimum_revenue_threshold': 800,  # USD
            'payment_frequency': 'monthly',
            'supported_regions': ['US', 'UK', 'CA', 'AU', 'SG'],
            'content_categories': ['movies', 'series', 'originals'],
            'api_version': 'v1.0'
        }
    }
    
    @classmethod
    def get_platform_config(cls, platform: str) -> Dict:
        """Get configuration for a specific OTT platform"""
        return cls.OTT_PLATFORMS.get(platform.lower(), {})
    
    @classmethod
    def submit_content(cls, platform: str, content_data: Dict) -> Dict:
        """Submit content to OTT platform for distribution"""
        try:
            platform_config = cls.get_platform_config(platform)
            if not platform_config:
                return {'success': False, 'error': f'Unsupported platform: {platform}'}
            
            # Prepare submission data
            submission_data = {
                'title': content_data.get('title'),
                'description': content_data.get('description'),
                'genre': content_data.get('genre'),
                'duration': content_data.get('duration'),
                'language': content_data.get('language', 'en'),
                'subtitles': content_data.get('subtitles', []),
                'content_rating': content_data.get('content_rating'),
                'release_date': content_data.get('release_date'),
                'content_url': content_data.get('content_url'),
                'thumbnail_url': content_data.get('thumbnail_url'),
                'trailer_url': content_data.get('trailer_url'),
                'metadata': content_data.get('metadata', {}),
                'revenue_share_percentage': platform_config['revenue_share_percentage'],
                'minimum_revenue_threshold': platform_config['minimum_revenue_threshold']
            }
            
            # Submit to platform API
            response = cls._call_platform_api(platform, 'content/submit', submission_data)
            
            if response.get('success'):
                # Store submission record
                cls._store_content_submission(platform, content_data, response)
                
                return {
                    'success': True,
                    'platform': platform,
                    'content_id': response.get('content_id'),
                    'status': response.get('status'),
                    'revenue_share_percentage': platform_config['revenue_share_percentage'],
                    'estimated_approval_time': response.get('estimated_approval_time', '7-14 days')
                }
            else:
                return {
                    'success': False,
                    'error': response.get('error', 'Content submission failed'),
                    'platform': platform
                }
                
        except Exception as e:
            logger.error(f"Content submission error for {platform}: {e}")
            return {
                'success': False,
                'error': f'Content submission failed: {str(e)}',
                'platform': platform
            }
    
    @classmethod
    def get_revenue_data(cls, platform: str, content_id: str, start_date: datetime, end_date: datetime) -> Dict:
        """Get revenue data from OTT platform"""
        try:
            platform_config = cls.get_platform_config(platform)
            if not platform_config:
                return {'success': False, 'error': f'Unsupported platform: {platform}'}
            
            # Prepare API request
            params = {
                'content_id': content_id,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'include_breakdown': True
            }
            
            # Call platform API
            response = cls._call_platform_api(platform, 'revenue/data', params, method='GET')
            
            if response.get('success'):
                revenue_data = response.get('data', {})
                
                # Calculate our share
                total_revenue = revenue_data.get('total_revenue', 0)
                our_share = total_revenue * platform_config['revenue_share_percentage']
                
                return {
                    'success': True,
                    'platform': platform,
                    'content_id': content_id,
                    'period': {
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat()
                    },
                    'revenue_data': {
                        'total_revenue': total_revenue,
                        'our_share': our_share,
                        'revenue_share_percentage': platform_config['revenue_share_percentage'],
                        'breakdown': revenue_data.get('breakdown', {}),
                        'views': revenue_data.get('views', 0),
                        'watch_time': revenue_data.get('watch_time', 0),
                        'regions': revenue_data.get('regions', {})
                    }
                }
            else:
                return {
                    'success': False,
                    'error': response.get('error', 'Failed to fetch revenue data'),
                    'platform': platform
                }
                
        except Exception as e:
            logger.error(f"Revenue data fetch error for {platform}: {e}")
            return {
                'success': False,
                'error': f'Revenue data fetch failed: {str(e)}',
                'platform': platform
            }
    
    @classmethod
    def get_content_performance(cls, platform: str, content_id: str) -> Dict:
        """Get content performance metrics from OTT platform"""
        try:
            platform_config = cls.get_platform_config(platform)
            if not platform_config:
                return {'success': False, 'error': f'Unsupported platform: {platform}'}
            
            # Call platform API for performance data
            response = cls._call_platform_api(platform, f'content/{content_id}/performance', {}, method='GET')
            
            if response.get('success'):
                performance_data = response.get('data', {})
                
                return {
                    'success': True,
                    'platform': platform,
                    'content_id': content_id,
                    'performance': {
                        'total_views': performance_data.get('total_views', 0),
                        'unique_viewers': performance_data.get('unique_viewers', 0),
                        'average_watch_time': performance_data.get('average_watch_time', 0),
                        'completion_rate': performance_data.get('completion_rate', 0),
                        'rating': performance_data.get('rating', 0),
                        'reviews_count': performance_data.get('reviews_count', 0),
                        'trending_score': performance_data.get('trending_score', 0),
                        'region_performance': performance_data.get('region_performance', {}),
                        'demographics': performance_data.get('demographics', {}),
                        'last_updated': performance_data.get('last_updated')
                    }
                }
            else:
                return {
                    'success': False,
                    'error': response.get('error', 'Failed to fetch performance data'),
                    'platform': platform
                }
                
        except Exception as e:
            logger.error(f"Performance data fetch error for {platform}: {e}")
            return {
                'success': False,
                'error': f'Performance data fetch failed: {str(e)}',
                'platform': platform
            }
    
    @classmethod
    def sync_revenue_data(cls, platform: str, content_id: str = None) -> Dict:
        """Sync revenue data from OTT platform"""
        try:
            platform_config = cls.get_platform_config(platform)
            if not platform_config:
                return {'success': False, 'error': f'Unsupported platform: {platform}'}
            
            # Get all content for this platform
            if content_id:
                content_list = [{'id': content_id}]
            else:
                content_list = cls._get_platform_content(platform)
            
            synced_count = 0
            total_revenue = 0
            errors = []
            
            for content in content_list:
                try:
                    # Get recent revenue data (last 30 days)
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=30)
                    
                    revenue_response = cls.get_revenue_data(platform, content['id'], start_date, end_date)
                    
                    if revenue_response.get('success'):
                        # Store revenue data
                        cls._store_revenue_data(platform, content['id'], revenue_response['revenue_data'])
                        synced_count += 1
                        total_revenue += revenue_response['revenue_data']['our_share']
                    else:
                        errors.append(f"Failed to sync {content['id']}: {revenue_response.get('error')}")
                        
                except Exception as e:
                    errors.append(f"Error syncing {content['id']}: {str(e)}")
            
            return {
                'success': True,
                'platform': platform,
                'synced_content_count': synced_count,
                'total_revenue_synced': total_revenue,
                'errors': errors
            }
            
        except Exception as e:
            logger.error(f"Revenue sync error for {platform}: {e}")
            return {
                'success': False,
                'error': f'Revenue sync failed: {str(e)}',
                'platform': platform
            }
    
    @classmethod
    def _call_platform_api(cls, platform: str, endpoint: str, data: Dict, method: str = 'POST') -> Dict:
        """Call OTT platform API"""
        try:
            platform_config = cls.get_platform_config(platform)
            api_key = settings.OTT_PLATFORMS.get(platform, {}).get('api_key', '')
            
            if not api_key:
                return {'success': False, 'error': f'API key not configured for {platform}'}
            
            url = f"{platform_config['api_base_url']}/{endpoint}"
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'CineChainLanka/1.0'
            }
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=data, timeout=30)
            else:
                response = requests.post(url, headers=headers, json=data, timeout=30)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API call error for {platform}: {e}")
            return {'success': False, 'error': f'API call failed: {str(e)}'}
        except Exception as e:
            logger.error(f"Unexpected error calling {platform} API: {e}")
            return {'success': False, 'error': f'Unexpected error: {str(e)}'}
    
    @classmethod
    def _store_content_submission(cls, platform: str, content_data: Dict, response: Dict) -> None:
        """Store content submission record"""
        try:
            from revenue.models import OTTContentSubmission
            
            OTTContentSubmission.objects.create(
                platform=platform,
                content_id=response.get('content_id'),
                title=content_data.get('title'),
                status=response.get('status', 'submitted'),
                revenue_share_percentage=cls.get_platform_config(platform)['revenue_share_percentage'],
                submission_data=content_data,
                platform_response=response
            )
        except Exception as e:
            logger.error(f"Error storing content submission: {e}")
    
    @classmethod
    def _store_revenue_data(cls, platform: str, content_id: str, revenue_data: Dict) -> None:
        """Store revenue data from OTT platform"""
        try:
            from revenue.models import OTTRevenueData
            
            OTTRevenueData.objects.create(
                platform=platform,
                content_id=content_id,
                total_revenue=revenue_data.get('total_revenue', 0),
                our_share=revenue_data.get('our_share', 0),
                revenue_share_percentage=revenue_data.get('revenue_share_percentage', 0),
                views=revenue_data.get('views', 0),
                watch_time=revenue_data.get('watch_time', 0),
                regions=revenue_data.get('regions', {}),
                breakdown=revenue_data.get('breakdown', {}),
                period_start=revenue_data.get('period_start'),
                period_end=revenue_data.get('period_end')
            )
        except Exception as e:
            logger.error(f"Error storing revenue data: {e}")
    
    @classmethod
    def _get_platform_content(cls, platform: str) -> List[Dict]:
        """Get all content for a platform"""
        try:
            from revenue.models import OTTContentSubmission
            
            submissions = OTTContentSubmission.objects.filter(
                platform=platform,
                status__in=['approved', 'live']
            )
            
            return [{'id': sub.content_id, 'title': sub.title} for sub in submissions]
        except Exception as e:
            logger.error(f"Error getting platform content: {e}")
            return []
    
    @classmethod
    def get_platform_analytics(cls, platform: str) -> Dict:
        """Get analytics summary for a platform"""
        try:
            from revenue.models import OTTRevenueData, OTTContentSubmission
            
            # Get content count
            content_count = OTTContentSubmission.objects.filter(platform=platform).count()
            live_content_count = OTTContentSubmission.objects.filter(
                platform=platform, 
                status='live'
            ).count()
            
            # Get revenue summary
            revenue_data = OTTRevenueData.objects.filter(platform=platform)
            total_revenue = sum(rd.our_share for rd in revenue_data)
            total_views = sum(rd.views for rd in revenue_data)
            
            # Get recent performance
            recent_revenue = OTTRevenueData.objects.filter(
                platform=platform,
                created_at__gte=datetime.now() - timedelta(days=30)
            )
            recent_total = sum(rd.our_share for rd in recent_revenue)
            
            return {
                'platform': platform,
                'content_summary': {
                    'total_submissions': content_count,
                    'live_content': live_content_count,
                    'approval_rate': (live_content_count / content_count * 100) if content_count > 0 else 0
                },
                'revenue_summary': {
                    'total_revenue': total_revenue,
                    'total_views': total_views,
                    'recent_revenue_30d': recent_total,
                    'average_revenue_per_content': total_revenue / live_content_count if live_content_count > 0 else 0
                },
                'performance_metrics': {
                    'total_watch_time': sum(rd.watch_time for rd in revenue_data),
                    'average_rating': 0,  # Would be calculated from performance data
                    'top_regions': cls._get_top_regions(platform)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting platform analytics: {e}")
            return {'error': f'Analytics fetch failed: {str(e)}'}
    
    @classmethod
    def _get_top_regions(cls, platform: str) -> List[Dict]:
        """Get top performing regions for a platform"""
        try:
            from revenue.models import OTTRevenueData
            
            revenue_data = OTTRevenueData.objects.filter(platform=platform)
            region_revenue = {}
            
            for rd in revenue_data:
                regions = rd.regions or {}
                for region, amount in regions.items():
                    if region not in region_revenue:
                        region_revenue[region] = 0
                    region_revenue[region] += amount
            
            # Sort by revenue and return top 5
            sorted_regions = sorted(region_revenue.items(), key=lambda x: x[1], reverse=True)
            return [{'region': region, 'revenue': amount} for region, amount in sorted_regions[:5]]
            
        except Exception as e:
            logger.error(f"Error getting top regions: {e}")
            return []

