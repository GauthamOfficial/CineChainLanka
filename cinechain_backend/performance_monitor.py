"""
Performance monitoring middleware for CineChainLanka
Tracks slow queries, requests, and provides performance metrics
"""

import time
import logging
import psutil
from django.conf import settings
from django.db import connection
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache

logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to monitor and log performance metrics
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.config = getattr(settings, 'PERFORMANCE_MONITORING', {})
        super().__init__(get_response)
    
    def process_request(self, request):
        """Start timing the request"""
        if not self.config.get('ENABLED', True):
            return None
            
        request._start_time = time.time()
        request._query_count_start = len(connection.queries)
    
    def process_response(self, request, response):
        """Log performance metrics for the request"""
        if not self.config.get('ENABLED', True):
            return response
            
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            query_count = len(connection.queries) - getattr(request, '_query_count_start', 0)
            
            # Log slow requests
            if duration > self.config.get('SLOW_REQUEST_THRESHOLD', 1.0):
                logger.warning(
                    f"Slow request: {request.path} took {duration:.2f}s "
                    f"({query_count} queries) - {request.method}"
                )
            
            # Store performance metrics in cache
            self._store_performance_metrics(request, duration, query_count)
        
        return response
    
    def _store_performance_metrics(self, request, duration, query_count):
        """Store performance metrics in cache for analytics"""
        try:
            metrics_key = f"perf_metrics_{request.path.replace('/', '_')}"
            metrics = cache.get(metrics_key, {
                'total_requests': 0,
                'total_duration': 0,
                'total_queries': 0,
                'slow_requests': 0,
                'avg_duration': 0,
                'avg_queries': 0,
            })
            
            metrics['total_requests'] += 1
            metrics['total_duration'] += duration
            metrics['total_queries'] += query_count
            
            if duration > self.config.get('SLOW_REQUEST_THRESHOLD', 1.0):
                metrics['slow_requests'] += 1
            
            metrics['avg_duration'] = metrics['total_duration'] / metrics['total_requests']
            metrics['avg_queries'] = metrics['total_queries'] / metrics['total_requests']
            
            # Store for 1 hour
            cache.set(metrics_key, metrics, 3600)
            
        except Exception as e:
            logger.debug(f"Could not store performance metrics: {e}")