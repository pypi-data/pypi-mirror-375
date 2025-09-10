"""
Flask middleware for rate limiting.
"""

import time
from typing import Callable, Optional
from flask import Flask, request, jsonify, g
from functools import wraps

from ..core import RateLimiter


class FlaskRateLimiter:
    """
    Flask rate limiting middleware.
    
    This class provides rate limiting functionality for Flask applications
    through decorators and middleware patterns.
    """
    
    def __init__(
        self,
        app: Optional[Flask] = None,
        limiter: Optional[RateLimiter] = None,
        key_extractor: Optional[Callable] = None,
        error_message: str = "Rate limit exceeded",
        error_status_code: int = 429,
        include_headers: bool = True
    ):
        """
        Initialize the Flask rate limiter.
        
        Args:
            app: The Flask application
            limiter: The rate limiter instance
            key_extractor: Function to extract rate limit key from request
            error_message: Message to return when rate limit is exceeded
            error_status_code: HTTP status code for rate limit errors
            include_headers: Whether to include rate limit headers in response
        """
        self.limiter = limiter
        self.key_extractor = key_extractor or self._default_key_extractor
        self.error_message = error_message
        self.error_status_code = error_status_code
        self.include_headers = include_headers
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize the rate limiter with a Flask app."""
        self.app = app
        
        # Register before_request handler
        app.before_request(self._before_request)
        
        # Register after_request handler
        app.after_request(self._after_request)
        
        # Register error handler for rate limit errors
        app.register_error_handler(429, self._rate_limit_error_handler)
    
    def _default_key_extractor(self, request) -> str:
        """
        Default key extractor that uses client IP address.
        
        Args:
            request: The Flask request object
            
        Returns:
            The rate limit key
        """
        # Try to get real IP from headers (for proxy setups)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to remote address
        return request.remote_addr or "unknown"
    
    def _before_request(self):
        """Handle rate limiting before each request."""
        if not self.limiter:
            return
        
        try:
            # Extract the rate limit key
            key = self.key_extractor(request)
            
            # Check if the request is allowed
            import asyncio
            allowed = asyncio.run(self.limiter.allow(key))
            
            if not allowed:
                # Rate limit exceeded
                response = jsonify({
                    "error": "Rate limit exceeded",
                    "message": self.error_message
                })
                response.status_code = self.error_status_code
                
                if self.include_headers:
                    # Add rate limit headers
                    stats = asyncio.run(self.limiter.get_stats(key))
                    self._add_rate_limit_headers(response, stats)
                
                return response
            
            # Store key for after_request
            g.rate_limit_key = key
            
        except Exception as e:
            # Log the error and continue
            # In production, you might want to log this properly
            print(f"Rate limiting error: {e}")
    
    def _after_request(self, response):
        """Add rate limit headers after each request."""
        if not self.limiter or not self.include_headers:
            return response
        
        try:
            # Get the key from g (set in before_request)
            key = getattr(g, 'rate_limit_key', None)
            if key:
                import asyncio
                stats = asyncio.run(self.limiter.get_stats(key))
                self._add_rate_limit_headers(response, stats)
        except Exception as e:
            print(f"Error adding rate limit headers: {e}")
        
        return response
    
    def _rate_limit_error_handler(self, error):
        """Handle rate limit errors."""
        response = jsonify({
            "error": "Rate limit exceeded",
            "message": self.error_message,
            "retry_after": 60  # Suggest retry after 60 seconds
        })
        response.status_code = self.error_status_code
        return response
    
    def _add_rate_limit_headers(self, response, stats: dict) -> None:
        """
        Add rate limit headers to the response.
        
        Args:
            response: The Flask response object
            stats: Rate limit statistics
        """
        algorithm_name = stats.get("algorithm", "unknown")
        
        # Add standard rate limit headers
        response.headers["X-RateLimit-Algorithm"] = algorithm_name
        
        # Add algorithm-specific headers
        if algorithm_name == "TokenBucket":
            response.headers["X-RateLimit-Remaining"] = str(stats.get("tokens_remaining", 0))
            response.headers["X-RateLimit-Capacity"] = str(stats.get("capacity", 0))
            response.headers["X-RateLimit-RefillRate"] = str(stats.get("refill_rate", 0))
        
        elif algorithm_name in ["FixedWindow", "SlidingWindow"]:
            response.headers["X-RateLimit-Remaining"] = str(stats.get("requests_remaining", 0))
            response.headers["X-RateLimit-Limit"] = str(stats.get("max_requests", 0))
            response.headers["X-RateLimit-Window"] = str(stats.get("window_seconds", 0))
        
        elif algorithm_name == "LeakyBucket":
            response.headers["X-RateLimit-Remaining"] = str(stats.get("space_remaining", 0))
            response.headers["X-RateLimit-Capacity"] = str(stats.get("capacity", 0))
            response.headers["X-RateLimit-Rate"] = str(stats.get("rate", 0))
        
        elif algorithm_name == "SlidingLog":
            response.headers["X-RateLimit-Remaining"] = str(stats.get("requests_remaining", 0))
            response.headers["X-RateLimit-Limit"] = str(stats.get("max_requests", 0))
            response.headers["X-RateLimit-Window"] = str(stats.get("window_seconds", 0))
        
        elif algorithm_name == "Hybrid":
            # For hybrid, we'll add headers from both algorithms
            token_stats = stats.get("token_bucket", {})
            window_stats = stats.get("sliding_window", {})
            
            response.headers["X-RateLimit-TokenRemaining"] = str(token_stats.get("tokens_remaining", 0))
            response.headers["X-RateLimit-WindowRemaining"] = str(window_stats.get("requests_remaining", 0))
        
        # Add timestamp
        response.headers["X-RateLimit-Timestamp"] = str(int(stats.get("current_time", time.time())))
    
    def limit(self, key_extractor: Optional[Callable] = None):
        """
        Decorator for rate limiting specific endpoints.
        
        Args:
            key_extractor: Optional custom key extractor for this endpoint
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not self.limiter:
                    return f(*args, **kwargs)
                
                try:
                    # Use custom key extractor or default
                    extractor = key_extractor or self.key_extractor
                    key = extractor(request)
                    
                    # Check rate limit
                    import asyncio
                    allowed = asyncio.run(self.limiter.allow(key))
                    
                    if not allowed:
                        response = jsonify({
                            "error": "Rate limit exceeded",
                            "message": self.error_message
                        })
                        response.status_code = self.error_status_code
                        
                        if self.include_headers:
                            stats = asyncio.run(self.limiter.get_stats(key))
                            self._add_rate_limit_headers(response, stats)
                        
                        return response
                    
                    # Call the original function
                    result = f(*args, **kwargs)
                    
                    # Add headers if needed
                    if self.include_headers:
                        stats = asyncio.run(self.limiter.get_stats(key))
                        if isinstance(result, tuple):
                            response = result[0]
                            self._add_rate_limit_headers(response, stats)
                        else:
                            # Convert to response if needed
                            response = jsonify(result)
                            self._add_rate_limit_headers(response, stats)
                            return response
                    
                    return result
                    
                except Exception as e:
                    print(f"Rate limiting error in decorator: {e}")
                    return f(*args, **kwargs)
            
            return decorated_function
        return decorator
