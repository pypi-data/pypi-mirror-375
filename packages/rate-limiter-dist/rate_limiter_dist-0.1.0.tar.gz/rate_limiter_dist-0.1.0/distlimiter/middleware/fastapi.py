"""
FastAPI middleware for rate limiting.
"""

import time
from typing import Callable, Optional
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..core import RateLimiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting.
    
    This middleware integrates rate limiting into FastAPI applications
    by checking rate limits before processing requests.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        limiter: RateLimiter,
        key_extractor: Optional[Callable[[Request], str]] = None,
        error_message: str = "Rate limit exceeded",
        error_status_code: int = 429,
        include_headers: bool = True
    ):
        """
        Initialize the rate limit middleware.
        
        Args:
            app: The ASGI application
            limiter: The rate limiter instance
            key_extractor: Function to extract rate limit key from request
            error_message: Message to return when rate limit is exceeded
            error_status_code: HTTP status code for rate limit errors
            include_headers: Whether to include rate limit headers in response
        """
        super().__init__(app)
        self.limiter = limiter
        self.key_extractor = key_extractor or self._default_key_extractor
        self.error_message = error_message
        self.error_status_code = error_status_code
        self.include_headers = include_headers
    
    def _default_key_extractor(self, request: Request) -> str:
        """
        Default key extractor that uses client IP address.
        
        Args:
            request: The FastAPI request object
            
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
        
        # Fall back to client host
        if request.client:
            return request.client.host
        
        return "unknown"
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and apply rate limiting.
        
        Args:
            request: The FastAPI request object
            call_next: The next middleware/endpoint in the chain
            
        Returns:
            The response
        """
        start_time = time.time()
        
        try:
            # Extract the rate limit key
            key = self.key_extractor(request)
            
            # Check if the request is allowed
            allowed = await self.limiter.allow(key)
            
            if not allowed:
                # Rate limit exceeded
                error_response = {
                    "error": "Rate limit exceeded",
                    "message": self.error_message,
                    "retry_after": None  # Could be calculated based on algorithm
                }
                
                response = JSONResponse(
                    content=error_response,
                    status_code=self.error_status_code
                )
                
                if self.include_headers:
                    # Add rate limit headers
                    stats = await self.limiter.get_stats(key)
                    self._add_rate_limit_headers(response, stats)
                
                return response
            
            # Request is allowed, proceed
            response = await call_next(request)
            
            if self.include_headers:
                # Add rate limit headers to successful responses
                stats = await self.limiter.get_stats(key)
                self._add_rate_limit_headers(response, stats)
            
            return response
            
        except Exception as e:
            # Log the error and return a generic error response
            # In production, you might want to log this properly
            print(f"Rate limiting error: {e}")
            
            error_response = {
                "error": "Internal server error",
                "message": "An error occurred while processing the request"
            }
            
            return JSONResponse(
                content=error_response,
                status_code=500
            )
    
    def _add_rate_limit_headers(self, response: Response, stats: dict) -> None:
        """
        Add rate limit headers to the response.
        
        Args:
            response: The response object
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
