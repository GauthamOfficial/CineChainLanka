import json
import hashlib
from typing import Any, Optional, Union
from django.core.cache import cache
from django.conf import settings
from django.core.cache.utils import make_template_fragment_key
from django.utils.encoding import force_str
from django.core.serializers.json import DjangoJSONEncoder


class CacheService:
    """Service for managing Redis caching operations"""
    
    def __init__(self, cache_alias: str = 'default'):
        self.cache_alias = cache_alias
        self.default_timeout = settings.CACHES[cache_alias]['TIMEOUT']
    
    def get(self, key: str) -> Any:
        """Get value from cache"""
        try:
            return cache.get(key, version=None, using=self.cache_alias)
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            if timeout is None:
                timeout = self.default_timeout
            
            # Serialize complex objects
            if not isinstance(value, (str, int, float, bool, type(None))):
                value = json.dumps(value, cls=DjangoJSONEncoder)
            
            return cache.set(key, value, timeout=timeout, using=self.cache_alias)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            return cache.delete(key, using=self.cache_alias)
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def delete_many(self, keys: list) -> int:
        """Delete multiple keys from cache"""
        try:
            return cache.delete_many(keys, using=self.cache_alias)
        except Exception as e:
            print(f"Cache delete_many error: {e}")
            return 0
    
    def get_or_set(self, key: str, callable_func, timeout: Optional[int] = None) -> Any:
        """Get value from cache or set it using callable"""
        try:
            if timeout is None:
                timeout = self.default_timeout
            
            return cache.get_or_set(
                key, 
                callable_func, 
                timeout=timeout, 
                using=self.cache_alias
            )
        except Exception as e:
            print(f"Cache get_or_set error: {e}")
            return callable_func()
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            # This requires redis-py to be available
            from django.core.cache import caches
            redis_cache = caches[self.cache_alias]
            redis_client = redis_cache._cache.get_client()
            
            keys = redis_client.keys(f"*{pattern}*")
            if keys:
                return redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache clear_pattern error: {e}")
            return 0
    
    def increment(self, key: str, delta: int = 1) -> Optional[int]:
        """Increment a numeric value in cache"""
        try:
            return cache.incr(key, delta=delta, using=self.cache_alias)
        except Exception as e:
            print(f"Cache increment error: {e}")
            return None
    
    def decrement(self, key: str, delta: int = 1) -> Optional[int]:
        """Decrement a numeric value in cache"""
        try:
            return cache.decr(key, delta=delta, using=self.cache_alias)
        except Exception as e:
            print(f"Cache decrement error: {e}")
            return None
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return cache.has_key(key, using=self.cache_alias)
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False
    
    def ttl(self, key: str) -> Optional[int]:
        """Get time to live for a key"""
        try:
            from django.core.cache import caches
            redis_cache = caches[self.cache_alias]
            redis_client = redis_cache._cache.get_client()
            return redis_client.ttl(key)
        except Exception as e:
            print(f"Cache ttl error: {e}")
            return None
    
    def generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from prefix and arguments"""
        key_parts = [prefix]
        
        # Add positional arguments
        for arg in args:
            if isinstance(arg, (list, dict)):
                key_parts.append(json.dumps(arg, sort_keys=True))
            else:
                key_parts.append(str(arg))
        
        # Add keyword arguments
        for key, value in sorted(kwargs.items()):
            if isinstance(value, (list, dict)):
                key_parts.append(f"{key}:{json.dumps(value, sort_keys=True)}")
            else:
                key_parts.append(f"{key}:{value}")
        
        # Create hash for long keys
        key_string = ":".join(key_parts)
        if len(key_string) > 250:  # Redis key length limit
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f"{prefix}:hash:{key_hash}"
        
        return key_string


# Cache decorators
def cache_result(timeout: int = 300, cache_alias: str = 'default', key_prefix: str = ''):
    """Decorator to cache function results"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_service = CacheService(cache_alias)
            
            # Generate cache key
            key = cache_service.generate_key(
                f"{key_prefix}:{func.__name__}",
                *args,
                **kwargs
            )
            
            # Try to get from cache
            result = cache_service.get(key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_service.set(key, result, timeout)
            
            return result
        return wrapper
    return decorator


def cache_invalidate(pattern: str, cache_alias: str = 'default'):
    """Decorator to invalidate cache on function call"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Invalidate cache
            cache_service = CacheService(cache_alias)
            cache_service.clear_pattern(pattern)
            
            return result
        return wrapper
    return decorator


# Specific cache services for different data types
class CampaignCacheService(CacheService):
    """Cache service specifically for campaign data"""
    
    def __init__(self):
        super().__init__('api')
        self.prefix = 'campaign'
    
    def get_campaign(self, campaign_id: int) -> Optional[dict]:
        """Get campaign data from cache"""
        key = f"{self.prefix}:detail:{campaign_id}"
        return self.get(key)
    
    def set_campaign(self, campaign_id: int, data: dict, timeout: int = 600) -> bool:
        """Set campaign data in cache"""
        key = f"{self.prefix}:detail:{campaign_id}"
        return self.set(key, data, timeout)
    
    def get_campaigns_list(self, filters: dict) -> Optional[list]:
        """Get campaigns list from cache"""
        key = self.generate_key(f"{self.prefix}:list", **filters)
        return self.get(key)
    
    def set_campaigns_list(self, filters: dict, data: list, timeout: int = 300) -> bool:
        """Set campaigns list in cache"""
        key = self.generate_key(f"{self.prefix}:list", **filters)
        return self.set(key, data, timeout)
    
    def invalidate_campaign(self, campaign_id: int) -> bool:
        """Invalidate campaign cache"""
        keys = [
            f"{self.prefix}:detail:{campaign_id}",
            f"{self.prefix}:list:*"
        ]
        return self.delete_many(keys) > 0


class UserCacheService(CacheService):
    """Cache service specifically for user data"""
    
    def __init__(self):
        super().__init__('api')
        self.prefix = 'user'
    
    def get_user_profile(self, user_id: int) -> Optional[dict]:
        """Get user profile from cache"""
        key = f"{self.prefix}:profile:{user_id}"
        return self.get(key)
    
    def set_user_profile(self, user_id: int, data: dict, timeout: int = 1800) -> bool:
        """Set user profile in cache"""
        key = f"{self.prefix}:profile:{user_id}"
        return self.set(key, data, timeout)
    
    def invalidate_user(self, user_id: int) -> bool:
        """Invalidate user cache"""
        keys = [
            f"{self.prefix}:profile:{user_id}",
            f"{self.prefix}:analytics:{user_id}",
            f"{self.prefix}:portfolio:{user_id}"
        ]
        return self.delete_many(keys) > 0


class AnalyticsCacheService(CacheService):
    """Cache service specifically for analytics data"""
    
    def __init__(self):
        super().__init__('api')
        self.prefix = 'analytics'
    
    def get_creator_analytics(self, user_id: int, period: str = '30') -> Optional[dict]:
        """Get creator analytics from cache"""
        key = f"{self.prefix}:creator:{user_id}:{period}"
        return self.get(key)
    
    def set_creator_analytics(self, user_id: int, data: dict, period: str = '30', timeout: int = 900) -> bool:
        """Set creator analytics in cache"""
        key = f"{self.prefix}:creator:{user_id}:{period}"
        return self.set(key, data, timeout)
    
    def get_investor_portfolio(self, user_id: int, period: str = '30') -> Optional[dict]:
        """Get investor portfolio from cache"""
        key = f"{self.prefix}:investor:{user_id}:{period}"
        return self.get(key)
    
    def set_investor_portfolio(self, user_id: int, data: dict, period: str = '30', timeout: int = 900) -> bool:
        """Set investor portfolio in cache"""
        key = f"{self.prefix}:investor:{user_id}:{period}"
        return self.set(key, data, timeout)
    
    def invalidate_user_analytics(self, user_id: int) -> bool:
        """Invalidate user analytics cache"""
        pattern = f"{self.prefix}:*:{user_id}:*"
        return self.clear_pattern(pattern) > 0


# Global cache service instances
campaign_cache = CampaignCacheService()
user_cache = UserCacheService()
analytics_cache = AnalyticsCacheService()
