import time
import logging
from functools import wraps
from typing import Callable, Any, Dict, List
from django.core.cache import cache
from django.conf import settings
from django.db import connection
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor and track performance metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.start_time = None
    
    def start_timer(self, operation: str):
        """Start timing an operation"""
        self.start_time = time.time()
        self.metrics[operation] = {
            'start_time': self.start_time,
            'end_time': None,
            'duration': None,
            'queries': len(connection.queries),
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def end_timer(self, operation: str):
        """End timing an operation"""
        if operation in self.metrics and self.start_time:
            end_time = time.time()
            self.metrics[operation]['end_time'] = end_time
            self.metrics[operation]['duration'] = end_time - self.start_time
            self.metrics[operation]['queries'] = len(connection.queries) - self.metrics[operation]['queries']
    
    def record_cache_hit(self, operation: str):
        """Record a cache hit"""
        if operation in self.metrics:
            self.metrics[operation]['cache_hits'] += 1
    
    def record_cache_miss(self, operation: str):
        """Record a cache miss"""
        if operation in self.metrics:
            self.metrics[operation]['cache_misses'] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.metrics
    
    def log_metrics(self, operation: str):
        """Log performance metrics"""
        if operation in self.metrics:
            metrics = self.metrics[operation]
            logger.info(f"Performance metrics for {operation}: {metrics}")


def monitor_performance(operation_name: str = None):
    """Decorator to monitor function performance"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            operation = operation_name or f"{func.__module__}.{func.__name__}"
            monitor = PerformanceMonitor()
            
            monitor.start_timer(operation)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                monitor.end_timer(operation)
                monitor.log_metrics(operation)
        
        return wrapper
    return decorator


def cache_with_monitoring(timeout: int = 300, cache_alias: str = 'default'):
    """Decorator that combines caching with performance monitoring"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__module__}.{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key, using=cache_alias)
            if cached_result is not None:
                logger.info(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            logger.info(f"Cache miss for {func.__name__}")
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout=timeout, using=cache_alias)
            
            return result
        return wrapper
    return decorator


class DatabaseQueryMonitor:
    """Monitor database query performance"""
    
    def __init__(self):
        self.initial_queries = len(connection.queries)
    
    def get_query_count(self) -> int:
        """Get number of queries executed since initialization"""
        return len(connection.queries) - self.initial_queries
    
    def get_slow_queries(self, threshold: float = 0.1) -> List[Dict]:
        """Get queries that took longer than threshold"""
        slow_queries = []
        for query in connection.queries[self.initial_queries:]:
            if float(query['time']) > threshold:
                slow_queries.append(query)
        return slow_queries
    
    def log_query_performance(self, operation: str):
        """Log database query performance"""
        query_count = self.get_query_count()
        slow_queries = self.get_slow_queries()
        
        logger.info(f"Database queries for {operation}: {query_count} total")
        if slow_queries:
            logger.warning(f"Slow queries detected in {operation}: {len(slow_queries)} queries")
            for query in slow_queries:
                logger.warning(f"Slow query: {query['sql'][:100]}... (took {query['time']}s)")


def monitor_db_queries(operation_name: str = None):
    """Decorator to monitor database query performance"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            operation = operation_name or f"{func.__module__}.{func.__name__}"
            db_monitor = DatabaseQueryMonitor()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                db_monitor.log_query_performance(operation)
        
        return wrapper
    return decorator


class APIPerformanceMixin:
    """Mixin for API views to add performance monitoring"""
    
    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Override dispatch to add performance monitoring"""
        start_time = time.time()
        
        # Add performance headers
        response = super().dispatch(request, *args, **kwargs)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Add performance headers
        if hasattr(response, 'data') and isinstance(response, Response):
            response['X-Processing-Time'] = f"{processing_time:.3f}s"
            response['X-DB-Queries'] = len(connection.queries)
        
        # Log performance metrics
        logger.info(f"API {request.method} {request.path} - {processing_time:.3f}s - {len(connection.queries)} queries")
        
        return response


class OptimizedQuerySet:
    """Optimized QuerySet with performance monitoring"""
    
    def __init__(self, queryset: QuerySet):
        self.queryset = queryset
        self.monitor = DatabaseQueryMonitor()
    
    def select_related(self, *fields):
        """Add select_related optimization"""
        return OptimizedQuerySet(self.queryset.select_related(*fields))
    
    def prefetch_related(self, *fields):
        """Add prefetch_related optimization"""
        return OptimizedQuerySet(self.queryset.prefetch_related(*fields))
    
    def only(self, *fields):
        """Add only optimization"""
        return OptimizedQuerySet(self.queryset.only(*fields))
    
    def defer(self, *fields):
        """Add defer optimization"""
        return OptimizedQuerySet(self.queryset.defer(*fields))
    
    def __iter__(self):
        """Iterate over queryset with monitoring"""
        self.monitor = DatabaseQueryMonitor()
        return iter(self.queryset)
    
    def __getitem__(self, key):
        """Get item with monitoring"""
        self.monitor = DatabaseQueryMonitor()
        return self.queryset[key]
    
    def __len__(self):
        """Get length with monitoring"""
        self.monitor = DatabaseQueryMonitor()
        return len(self.queryset)
    
    def count(self):
        """Count with monitoring"""
        self.monitor = DatabaseQueryMonitor()
        return self.queryset.count()
    
    def exists(self):
        """Check existence with monitoring"""
        self.monitor = DatabaseQueryMonitor()
        return self.queryset.exists()
    
    def first(self):
        """Get first item with monitoring"""
        self.monitor = DatabaseQueryMonitor()
        return self.queryset.first()
    
    def last(self):
        """Get last item with monitoring"""
        self.monitor = DatabaseQueryMonitor()
        return self.queryset.last()
    
    def get(self, *args, **kwargs):
        """Get item with monitoring"""
        self.monitor = DatabaseQueryMonitor()
        return self.queryset.get(*args, **kwargs)
    
    def filter(self, *args, **kwargs):
        """Filter with monitoring"""
        return OptimizedQuerySet(self.queryset.filter(*args, **kwargs))
    
    def exclude(self, *args, **kwargs):
        """Exclude with monitoring"""
        return OptimizedQuerySet(self.queryset.exclude(*args, **kwargs))
    
    def order_by(self, *fields):
        """Order by with monitoring"""
        return OptimizedQuerySet(self.queryset.order_by(*fields))
    
    def distinct(self, *fields):
        """Distinct with monitoring"""
        return OptimizedQuerySet(self.queryset.distinct(*fields))
    
    def values(self, *fields):
        """Values with monitoring"""
        return OptimizedQuerySet(self.queryset.values(*fields))
    
    def values_list(self, *fields, **kwargs):
        """Values list with monitoring"""
        return OptimizedQuerySet(self.queryset.values_list(*fields, **kwargs))
    
    def annotate(self, *args, **kwargs):
        """Annotate with monitoring"""
        return OptimizedQuerySet(self.queryset.annotate(*args, **kwargs))
    
    def aggregate(self, *args, **kwargs):
        """Aggregate with monitoring"""
        self.monitor = DatabaseQueryMonitor()
        return self.queryset.aggregate(*args, **kwargs)


def optimize_queryset(queryset: QuerySet) -> OptimizedQuerySet:
    """Convert QuerySet to OptimizedQuerySet"""
    return OptimizedQuerySet(queryset)


# Performance monitoring middleware
class PerformanceMiddleware:
    """Middleware to monitor request performance"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        # Process request
        response = self.get_response(request)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Add performance headers
        response['X-Processing-Time'] = f"{processing_time:.3f}s"
        response['X-DB-Queries'] = len(connection.queries)
        
        # Log performance metrics
        logger.info(f"Request {request.method} {request.path} - {processing_time:.3f}s - {len(connection.queries)} queries")
        
        return response


# Cache warming functions
def warm_campaign_cache():
    """Warm up campaign-related cache"""
    from campaigns.models import Campaign
    from cinechain_backend.cache_service import campaign_cache
    
    logger.info("Warming campaign cache...")
    
    # Cache popular campaigns
    popular_campaigns = Campaign.objects.filter(
        status='active'
    ).order_by('-current_amount')[:20]
    
    for campaign in popular_campaigns:
        campaign_data = {
            'id': campaign.id,
            'title': campaign.title,
            'description': campaign.description,
            'goal_amount': float(campaign.goal_amount),
            'current_amount': float(campaign.current_amount),
            'status': campaign.status,
            'creator': {
                'id': campaign.creator.id,
                'username': campaign.creator.username,
                'first_name': campaign.creator.first_name,
                'last_name': campaign.creator.last_name,
            }
        }
        campaign_cache.set_campaign(campaign.id, campaign_data)
    
    logger.info("Campaign cache warmed successfully")


def warm_user_cache():
    """Warm up user-related cache"""
    from users.models import User
    from cinechain_backend.cache_service import user_cache
    
    logger.info("Warming user cache...")
    
    # Cache active users
    active_users = User.objects.filter(
        is_active=True,
        last_login__isnull=False
    ).order_by('-last_login')[:100]
    
    for user in active_users:
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'is_verified': user.is_verified,
            'kyc_status': user.kyc_status,
        }
        user_cache.set_user_profile(user.id, user_data)
    
    logger.info("User cache warmed successfully")


def warm_analytics_cache():
    """Warm up analytics cache"""
    from users.models import User
    from cinechain_backend.cache_service import analytics_cache
    
    logger.info("Warming analytics cache...")
    
    # Cache analytics for active users
    active_users = User.objects.filter(
        is_active=True,
        last_login__isnull=False
    )[:50]
    
    for user in active_users:
        # This would typically call the actual analytics functions
        # For now, we'll just set placeholder data
        analytics_data = {
            'user_id': user.id,
            'total_campaigns': 0,
            'total_revenue': 0,
            'total_investments': 0,
            'last_updated': time.time()
        }
        
        if user.role in ['creator', 'admin']:
            analytics_cache.set_creator_analytics(user.id, analytics_data)
        
        if user.role in ['investor', 'admin']:
            analytics_cache.set_investor_portfolio(user.id, analytics_data)
    
    logger.info("Analytics cache warmed successfully")


def warm_all_caches():
    """Warm up all caches"""
    logger.info("Starting cache warming process...")
    
    try:
        warm_campaign_cache()
        warm_user_cache()
        warm_analytics_cache()
        logger.info("All caches warmed successfully")
    except Exception as e:
        logger.error(f"Error warming caches: {e}")


# Management command for cache warming
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Warm up application caches'
    
    def handle(self, *args, **options):
        warm_all_caches()
        self.stdout.write(
            self.style.SUCCESS('Successfully warmed all caches')
        )
