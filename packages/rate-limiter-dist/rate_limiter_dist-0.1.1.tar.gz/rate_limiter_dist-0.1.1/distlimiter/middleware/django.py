"""
Django middleware for rate limiting.
"""

import time
import asyncio
from typing import Callable, Optional
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from ..core import RateLimiter


class DjangoRateLimitMiddleware:
    """
    Django middleware for rate limiting.
    
    This middleware provides rate limiting functionality for Django applications.
    """
    
    def __init__(self, get_response: Callable):
        """
        Initialize the Django rate limit middleware.
        
        Args:
            get_response: The next middleware in the chain
        """
        self.get_response = get_response
        
        # Get configuration from Django settings
        self.limiter = getattr(settings, 'RATE_LIMITER', None)
        self.key_extractor = getattr(settings, 'RATE_LIMITER_KEY_EXTRACTOR', self._default_key_extractor)
        self.error_message = getattr(settings, 'RATE_LIMITER_ERROR_MESSAGE', 'Rate limit exceeded')
        self.error_status_code = getattr(settings, 'RATE_LIMITER_ERROR_STATUS_CODE', 429)
        self.include_headers = getattr(settings, 'RATE_LIMITER_INCLUDE_HEADERS', True)
        self.exempt_paths = getattr(settings, 'RATE_LIMITER_EXEMPT_PATHS', [])
        self.exempt_methods = getattr(settings, 'RATE_LIMITER_EXEMPT_METHODS', ['GET'])
    
    def _default_key_extractor(self, request: HttpRequest) -> str:
        """
        Default key extractor that uses client IP address.
        
        Args:
            request: The Django request object
            
        Returns:
            The rate limit key
        """
        # Try to get real IP from headers (for proxy setups)
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.META.get('HTTP_X_REAL_IP')
        if real_ip:
            return real_ip
        
        # Fall back to remote address
        return request.META.get('REMOTE_ADDR', 'unknown')
    
    def _is_exempt(self, request: HttpRequest) -> bool:
        """
        Check if the request is exempt from rate limiting.
        
        Args:
            request: The Django request object
            
        Returns:
            True if the request is exempt, False otherwise
        """
        # Check exempt paths
        path = request.path_info.lstrip('/')
        for exempt_path in self.exempt_paths:
            if path.startswith(exempt_path):
                return True
        
        # Check exempt methods
        if request.method in self.exempt_methods:
            return True
        
        return False
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Process the request and apply rate limiting.
        
        Args:
            request: The Django request object
            
        Returns:
            The response
        """
        # Check if rate limiting is enabled
        if not self.limiter:
            return self.get_response(request)
        
        # Check if request is exempt
        if self._is_exempt(request):
            return self.get_response(request)
        
        try:
            # Extract the rate limit key
            key = self.key_extractor(request)
            
            # Check if the request is allowed
            allowed = asyncio.run(self.limiter.allow(key))
            
            if not allowed:
                # Rate limit exceeded
                response = JsonResponse({
                    'error': 'Rate limit exceeded',
                    'message': self.error_message
                }, status=self.error_status_code)
                
                if self.include_headers:
                    # Add rate limit headers
                    stats = asyncio.run(self.limiter.get_stats(key))
                    self._add_rate_limit_headers(response, stats)
                
                return response
            
            # Request is allowed, proceed
            response = self.get_response(request)
            
            if self.include_headers:
                # Add rate limit headers to successful responses
                stats = asyncio.run(self.limiter.get_stats(key))
                self._add_rate_limit_headers(response, stats)
            
            return response
            
        except Exception as e:
            # Log the error and continue
            # In production, you might want to log this properly
            print(f"Rate limiting error: {e}")
            return self.get_response(request)
    
    def _add_rate_limit_headers(self, response: HttpResponse, stats: dict) -> None:
        """
        Add rate limit headers to the response.
        
        Args:
            response: The Django response object
            stats: Rate limit statistics
        """
        algorithm_name = stats.get("algorithm", "unknown")
        
        # Add standard rate limit headers
        response['X-RateLimit-Algorithm'] = algorithm_name
        
        # Add algorithm-specific headers
        if algorithm_name == "TokenBucket":
            response['X-RateLimit-Remaining'] = str(stats.get("tokens_remaining", 0))
            response['X-RateLimit-Capacity'] = str(stats.get("capacity", 0))
            response['X-RateLimit-RefillRate'] = str(stats.get("refill_rate", 0))
        
        elif algorithm_name in ["FixedWindow", "SlidingWindow"]:
            response['X-RateLimit-Remaining'] = str(stats.get("requests_remaining", 0))
            response['X-RateLimit-Limit'] = str(stats.get("max_requests", 0))
            response['X-RateLimit-Window'] = str(stats.get("window_seconds", 0))
        
        elif algorithm_name == "LeakyBucket":
            response['X-RateLimit-Remaining'] = str(stats.get("space_remaining", 0))
            response['X-RateLimit-Capacity'] = str(stats.get("capacity", 0))
            response['X-RateLimit-Rate'] = str(stats.get("rate", 0))
        
        elif algorithm_name == "SlidingLog":
            response['X-RateLimit-Remaining'] = str(stats.get("requests_remaining", 0))
            response['X-RateLimit-Limit'] = str(stats.get("max_requests", 0))
            response['X-RateLimit-Window'] = str(stats.get("window_seconds", 0))
        
        elif algorithm_name == "Hybrid":
            # For hybrid, we'll add headers from both algorithms
            token_stats = stats.get("token_bucket", {})
            window_stats = stats.get("sliding_window", {})
            
            response['X-RateLimit-TokenRemaining'] = str(token_stats.get("tokens_remaining", 0))
            response['X-RateLimit-WindowRemaining'] = str(window_stats.get("requests_remaining", 0))
        
        # Add timestamp
        response['X-RateLimit-Timestamp'] = str(int(stats.get("current_time", time.time())))


def rate_limit(key_extractor: Optional[Callable] = None):
    """
    Decorator for rate limiting specific Django views.
    
    Args:
        key_extractor: Optional custom key extractor for this view
    """
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            # Get rate limiter from settings
            limiter = getattr(settings, 'RATE_LIMITER', None)
            if not limiter:
                return view_func(request, *args, **kwargs)
            
            try:
                # Use custom key extractor or default
                extractor = key_extractor or DjangoRateLimitMiddleware._default_key_extractor
                key = extractor(request)
                
                # Check rate limit
                allowed = asyncio.run(limiter.allow(key))
                
                if not allowed:
                    error_message = getattr(settings, 'RATE_LIMITER_ERROR_MESSAGE', 'Rate limit exceeded')
                    error_status_code = getattr(settings, 'RATE_LIMITER_ERROR_STATUS_CODE', 429)
                    include_headers = getattr(settings, 'RATE_LIMITER_INCLUDE_HEADERS', True)
                    
                    response = JsonResponse({
                        'error': 'Rate limit exceeded',
                        'message': error_message
                    }, status=error_status_code)
                    
                    if include_headers:
                        stats = asyncio.run(limiter.get_stats(key))
                        middleware = DjangoRateLimitMiddleware(lambda r: response)
                        middleware._add_rate_limit_headers(response, stats)
                    
                    return response
                
                # Call the original view
                result = view_func(request, *args, **kwargs)
                
                # Add headers if needed
                include_headers = getattr(settings, 'RATE_LIMITER_INCLUDE_HEADERS', True)
                if include_headers:
                    stats = asyncio.run(limiter.get_stats(key))
                    middleware = DjangoRateLimitMiddleware(lambda r: result)
                    middleware._add_rate_limit_headers(result, stats)
                
                return result
                
            except Exception as e:
                print(f"Rate limiting error in decorator: {e}")
                return view_func(request, *args, **kwargs)
        
        return wrapped_view
    return decorator
