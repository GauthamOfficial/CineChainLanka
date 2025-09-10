"""
Rate limiting utilities for CineChainLanka
Provides decorators and mixins for API rate limiting
"""

from django.core.cache import cache
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.vary import vary_on_headers
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def rate_limit_by_user(rate='100/hour', method='GET', block=True):
    """
    Rate limit decorator based on user
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                key = f"rate_limit_user_{request.user.id}_{method}"
            else:
                key = f"rate_limit_anon_{request.META.get('REMOTE_ADDR')}_{method}"
            
            # Check rate limit
            if not _check_rate_limit(key, rate):
                if block:
                    return JsonResponse({
                        'error': 'Rate limit exceeded',
                        'message': f'Too many {method} requests. Limit: {rate}'
                    }, status=429)
                else:
                    logger.warning(f"Rate limit exceeded for {key}")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def rate_limit_by_ip(rate='50/hour', method='GET', block=True):
    """
    Rate limit decorator based on IP address
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            ip = request.META.get('REMOTE_ADDR', 'unknown')
            key = f"rate_limit_ip_{ip}_{method}"
            
            if not _check_rate_limit(key, rate):
                if block:
                    return JsonResponse({
                        'error': 'Rate limit exceeded',
                        'message': f'Too many {method} requests from this IP. Limit: {rate}'
                    }, status=429)
                else:
                    logger.warning(f"Rate limit exceeded for IP {ip}")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def _check_rate_limit(key, rate):
    """
    Check if rate limit is exceeded
    """
    try:
        # Parse rate (e.g., '100/hour', '10/minute')
        count, period = rate.split('/')
        count = int(count)
        
        if period == 'minute':
            ttl = 60
        elif period == 'hour':
            ttl = 3600
        elif period == 'day':
            ttl = 86400
        else:
            ttl = 60  # Default to minute
        
        # Get current count
        current_count = cache.get(key, 0)
        
        if current_count >= count:
            return False
        
        # Increment count
        cache.set(key, current_count + 1, ttl)
        return True
        
    except Exception as e:
        logger.error(f"Rate limit check error: {e}")
        return True  # Allow request on error


class RateLimitMixin:
    """
    Mixin for rate limiting in class-based views
    """
    
    rate_limit_rate = '100/hour'
    rate_limit_method = 'GET'
    rate_limit_block = True
    
    def dispatch(self, request, *args, **kwargs):
        # Apply rate limiting
        if not self._check_rate_limit(request):
            if self.rate_limit_block:
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many {self.rate_limit_method} requests. Limit: {self.rate_limit_rate}'
                }, status=429)
            else:
                logger.warning(f"Rate limit exceeded for {request.path}")
        
        return super().dispatch(request, *args, **kwargs)
    
    def _check_rate_limit(self, request):
        """Check rate limit for the request"""
        if request.user.is_authenticated:
            key = f"rate_limit_user_{request.user.id}_{self.rate_limit_method}"
        else:
            key = f"rate_limit_anon_{request.META.get('REMOTE_ADDR')}_{self.rate_limit_method}"
        
        return _check_rate_limit(key, self.rate_limit_rate)


class APIThrottleMixin:
    """
    Mixin for API throttling with different rates for different actions
    """
    
    # Override these in your view
    throttle_rates = {
        'list': '100/hour',
        'create': '20/hour',
        'update': '50/hour',
        'destroy': '10/hour',
        'retrieve': '200/hour',
    }
    
    def get_throttle_rate(self, action):
        """Get throttle rate for specific action"""
        return self.throttle_rates.get(action, '100/hour')
    
    def dispatch(self, request, *args, **kwargs):
        # Determine action based on HTTP method
        action = self._get_action_from_method(request.method)
        rate = self.get_throttle_rate(action)
        
        if not _check_rate_limit(f"api_throttle_{request.user.id if request.user.is_authenticated else request.META.get('REMOTE_ADDR')}_{action}", rate):
            return JsonResponse({
                'error': 'API rate limit exceeded',
                'message': f'Too many {action} requests. Limit: {rate}',
                'action': action,
                'rate_limit': rate
            }, status=429)
        
        return super().dispatch(request, *args, **kwargs)
    
    def _get_action_from_method(self, method):
        """Map HTTP method to action"""
        method_action_map = {
            'GET': 'list' if 'pk' not in self.kwargs else 'retrieve',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'destroy',
        }
        return method_action_map.get(method, 'list')


def custom_rate_limit(rate, method='GET', key_func=None, block=True):
    """
    Custom rate limit decorator with custom key function
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if key_func:
                key = key_func(request)
            elif request.user.is_authenticated:
                key = f"custom_rate_{request.user.id}_{method}"
            else:
                key = f"custom_rate_{request.META.get('REMOTE_ADDR')}_{method}"
            
            if not _check_rate_limit(key, rate):
                if block:
                    return JsonResponse({
                        'error': 'Custom rate limit exceeded',
                        'message': f'Too many {method} requests. Limit: {rate}'
                    }, status=429)
                else:
                    logger.warning(f"Custom rate limit exceeded for {key}")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# Predefined rate limit decorators for common use cases
login_rate_limit = rate_limit_by_ip('5/minute', 'POST')
register_rate_limit = rate_limit_by_ip('3/minute', 'POST')
password_reset_rate_limit = rate_limit_by_ip('2/minute', 'POST')
api_rate_limit = rate_limit_by_user('1000/hour', 'GET')
upload_rate_limit = rate_limit_by_user('10/minute', 'POST')
payment_rate_limit = rate_limit_by_user('5/minute', 'POST')

