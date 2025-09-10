"""
Advanced caching service for CineChainLanka
Provides intelligent caching with TTL management and cache invalidation
"""

import json
import hashlib
from typing import Any, Optional, Dict, List
from django.core.cache import cache
from django.conf import settings
from django.core.cache.utils import make_template_fragment_key
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """
    Advanced caching service with intelligent cache management
    """
    
    CACHE_PREFIX = 'cinechain'
    DEFAULT_TTL = 300  # 5 minutes
    
    # Cache key patterns
    USER_CACHE_PREFIX = f"{CACHE_PREFIX}:user"
    CAMPAIGN_CACHE_PREFIX = f"{CACHE_PREFIX}:campaign"
    ANALYTICS_CACHE_PREFIX = f"{CACHE_PREFIX}:analytics"
    API_CACHE_PREFIX = f"{CACHE_PREFIX}:api"
    
    @classmethod
    def _generate_cache_key(cls, prefix: str, identifier: str, *args) -> str:
        """Generate a consistent cache key"""
        key_parts = [prefix, str(identifier)]
        if args:
            key_parts.extend(str(arg) for arg in args)
        return ':'.join(key_parts)
    
    @classmethod
    def _serialize_data(cls, data: Any) -> str:
        """Serialize data for caching"""
        try:
            return json.dumps(data, default=str)
        except (TypeError, ValueError) as e:
            logger.warning(f"Failed to serialize data for cache: {e}")
            return str(data)
    
    @classmethod
    def _deserialize_data(cls, data: str) -> Any:
        """Deserialize data from cache"""
        try:
            return json.loads(data)
        except (TypeError, ValueError, json.JSONDecodeError):
            return data
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get data from cache"""
        try:
            data = cache.get(key)
            if data is None:
                return default
            return cls._deserialize_data(data)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return default
    
    @classmethod
    def set(cls, key: str, data: Any, ttl: int = None) -> bool:
        """Set data in cache"""
        try:
            ttl = ttl or cls.DEFAULT_TTL
            serialized_data = cls._serialize_data(data)
            cache.set(key, serialized_data, ttl)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    @classmethod
    def delete(cls, key: str) -> bool:
        """Delete data from cache"""
        try:
            cache.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    @classmethod
    def get_or_set(cls, key: str, callable_func, ttl: int = None, *args, **kwargs) -> Any:
        """Get data from cache or set it using callable"""
        data = cls.get(key)
        if data is None:
            data = callable_func(*args, **kwargs)
            cls.set(key, data, ttl)
        return data
    
    @classmethod
    def invalidate_pattern(cls, pattern: str) -> int:
        """Invalidate all cache keys matching pattern"""
        try:
            # This is a simplified version - in production, you'd use Redis SCAN
            # For now, we'll maintain a list of keys to invalidate
            keys_to_invalidate = cache.get(f"{cls.CACHE_PREFIX}:keys:{pattern}", [])
            if keys_to_invalidate:
                cache.delete_many(keys_to_invalidate)
                cache.delete(f"{cls.CACHE_PREFIX}:keys:{pattern}")
            return len(keys_to_invalidate)
        except Exception as e:
            logger.error(f"Cache pattern invalidation error for {pattern}: {e}")
            return 0
    
    @classmethod
    def register_key(cls, pattern: str, key: str) -> None:
        """Register a key under a pattern for later invalidation"""
        try:
            keys_key = f"{cls.CACHE_PREFIX}:keys:{pattern}"
            keys = cache.get(keys_key, [])
            if key not in keys:
                keys.append(key)
                cache.set(keys_key, keys, 3600)  # Store for 1 hour
        except Exception as e:
            logger.error(f"Cache key registration error: {e}")


class UserCacheService(CacheService):
    """User-specific caching service"""
    
    @classmethod
    def get_user_profile(cls, user_id: int) -> Optional[Dict]:
        """Get cached user profile"""
        key = cls._generate_cache_key(cls.USER_CACHE_PREFIX, user_id, 'profile')
        return cls.get(key)
    
    @classmethod
    def set_user_profile(cls, user_id: int, profile_data: Dict, ttl: int = 3600) -> bool:
        """Cache user profile"""
        key = cls._generate_cache_key(cls.USER_CACHE_PREFIX, user_id, 'profile')
        cls.register_key('user', key)
        return cls.set(key, profile_data, ttl)
    
    @classmethod
    def invalidate_user_cache(cls, user_id: int) -> int:
        """Invalidate all user-related cache"""
        return cls.invalidate_pattern(f"user:{user_id}")


class CampaignCacheService(CacheService):
    """Campaign-specific caching service"""
    
    @classmethod
    def get_campaign_list(cls, filters: Dict = None) -> Optional[List]:
        """Get cached campaign list"""
        filter_hash = hashlib.md5(str(filters or {}).encode()).hexdigest()[:8]
        key = cls._generate_cache_key(cls.CAMPAIGN_CACHE_PREFIX, 'list', filter_hash)
        return cls.get(key)
    
    @classmethod
    def set_campaign_list(cls, campaigns: List, filters: Dict = None, ttl: int = 300) -> bool:
        """Cache campaign list"""
        filter_hash = hashlib.md5(str(filters or {}).encode()).hexdigest()[:8]
        key = cls._generate_cache_key(cls.CAMPAIGN_CACHE_PREFIX, 'list', filter_hash)
        cls.register_key('campaign', key)
        return cls.set(key, campaigns, ttl)
    
    @classmethod
    def get_campaign_detail(cls, campaign_id: int) -> Optional[Dict]:
        """Get cached campaign detail"""
        key = cls._generate_cache_key(cls.CAMPAIGN_CACHE_PREFIX, campaign_id, 'detail')
        return cls.get(key)
    
    @classmethod
    def set_campaign_detail(cls, campaign_id: int, campaign_data: Dict, ttl: int = 600) -> bool:
        """Cache campaign detail"""
        key = cls._generate_cache_key(cls.CAMPAIGN_CACHE_PREFIX, campaign_id, 'detail')
        cls.register_key('campaign', key)
        return cls.set(key, campaign_data, ttl)
    
    @classmethod
    def invalidate_campaign_cache(cls, campaign_id: int = None) -> int:
        """Invalidate campaign cache"""
        if campaign_id:
            return cls.invalidate_pattern(f"campaign:{campaign_id}")
        return cls.invalidate_pattern('campaign')


class AnalyticsCacheService(CacheService):
    """Analytics-specific caching service"""
    
    @classmethod
    def get_analytics_data(cls, analytics_type: str, params: Dict = None) -> Optional[Dict]:
        """Get cached analytics data"""
        param_hash = hashlib.md5(str(params or {}).encode()).hexdigest()[:8]
        key = cls._generate_cache_key(cls.ANALYTICS_CACHE_PREFIX, analytics_type, param_hash)
        return cls.get(key)
    
    @classmethod
    def set_analytics_data(cls, analytics_type: str, data: Dict, params: Dict = None, ttl: int = 300) -> bool:
        """Cache analytics data"""
        param_hash = hashlib.md5(str(params or {}).encode()).hexdigest()[:8]
        key = cls._generate_cache_key(cls.ANALYTICS_CACHE_PREFIX, analytics_type, param_hash)
        cls.register_key('analytics', key)
        return cls.set(key, data, ttl)
    
    @classmethod
    def invalidate_analytics_cache(cls) -> int:
        """Invalidate all analytics cache"""
        return cls.invalidate_pattern('analytics')


class APICacheService(CacheService):
    """API-specific caching service"""
    
    @classmethod
    def get_api_response(cls, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Get cached API response"""
        param_hash = hashlib.md5(str(params or {}).encode()).hexdigest()[:8]
        key = cls._generate_cache_key(cls.API_CACHE_PREFIX, endpoint, param_hash)
        return cls.get(key)
    
    @classmethod
    def set_api_response(cls, endpoint: str, response_data: Dict, params: Dict = None, ttl: int = 600) -> bool:
        """Cache API response"""
        param_hash = hashlib.md5(str(params or {}).encode()).hexdigest()[:8]
        key = cls._generate_cache_key(cls.API_CACHE_PREFIX, endpoint, param_hash)
        cls.register_key('api', key)
        return cls.set(key, response_data, ttl)
    
    @classmethod
    def invalidate_api_cache(cls, endpoint: str = None) -> int:
        """Invalidate API cache"""
        if endpoint:
            return cls.invalidate_pattern(f"api:{endpoint}")
        return cls.invalidate_pattern('api')


def cache_result(ttl: int = 300, key_prefix: str = None):
    """
    Decorator to cache function results
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_prefix:
                cache_key = f"{key_prefix}:{func.__name__}"
            else:
                cache_key = f"func:{func.__name__}"
            
            # Add args and kwargs to key
            key_data = str(args) + str(sorted(kwargs.items()))
            key_hash = hashlib.md5(key_data.encode()).hexdigest()[:8]
            full_key = f"{cache_key}:{key_hash}"
            
            # Try to get from cache
            result = CacheService.get(full_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            CacheService.set(full_key, result, ttl)
            return result
        
        return wrapper
    return decorator