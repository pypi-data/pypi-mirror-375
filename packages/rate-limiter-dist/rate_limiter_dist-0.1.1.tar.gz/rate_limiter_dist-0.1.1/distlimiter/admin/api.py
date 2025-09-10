"""
Admin API for rate limiting management.

This module provides a FastAPI application for managing rate limiting rules
and monitoring usage statistics.
"""

import json
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from ..core import RateLimiter
from ..algorithms import (
    TokenBucket, LeakyBucket, FixedWindow, 
    SlidingWindow, SlidingLog, Hybrid
)


class RuleCreate(BaseModel):
    """Model for creating rate limiting rules."""
    key: str = Field(..., description="Rate limit key (e.g., user ID, IP address)")
    algorithm: str = Field(..., description="Algorithm type")
    parameters: Dict[str, Any] = Field(..., description="Algorithm parameters")
    ttl: Optional[int] = Field(3600, description="Time to live in seconds")


class RuleResponse(BaseModel):
    """Model for rate limiting rule responses."""
    key: str
    algorithm: str
    parameters: Dict[str, Any]
    ttl: int
    created_at: float


class StatsResponse(BaseModel):
    """Model for rate limiting statistics."""
    key: str
    algorithm: str
    stats: Dict[str, Any]
    timestamp: float


def create_admin_app(limiter: RateLimiter) -> FastAPI:
    """
    Create the admin API application.
    
    Args:
        limiter: The rate limiter instance to manage
        
    Returns:
        FastAPI application for admin operations
    """
    app = FastAPI(
        title="DistLimiter Admin API",
        description="Admin API for managing rate limiting rules and monitoring usage",
        version="1.0.0"
    )
    
    # Store the limiter instance
    app.state.limiter = limiter
    
    def get_limiter() -> RateLimiter:
        """Dependency to get the rate limiter instance."""
        return app.state.limiter
    
    @app.post("/rules", response_model=RuleResponse)
    async def create_rule(
        rule: RuleCreate,
        limiter: RateLimiter = Depends(get_limiter)
    ):
        """
        Create or update a rate limiting rule.
        
        This endpoint allows creating custom rate limiting rules for specific keys.
        Note: This is a simplified implementation. In a real system, you might want
        to store rules in a database and dynamically create limiters.
        """
        try:
            # Validate algorithm type
            algorithm_map = {
                "token_bucket": TokenBucket,
                "leaky_bucket": LeakyBucket,
                "fixed_window": FixedWindow,
                "sliding_window": SlidingWindow,
                "sliding_log": SlidingLog,
                "hybrid": Hybrid
            }
            
            if rule.algorithm not in algorithm_map:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported algorithm: {rule.algorithm}"
                )
            
            # For now, we'll just validate the parameters
            # In a real implementation, you might create a new limiter instance
            # or update the existing one with new rules
            
            return RuleResponse(
                key=rule.key,
                algorithm=rule.algorithm,
                parameters=rule.parameters,
                ttl=rule.ttl,
                created_at=time.time()
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to create rule: {str(e)}"
            )
    
    @app.get("/rules", response_model=List[RuleResponse])
    async def list_rules(limiter: RateLimiter = Depends(get_limiter)):
        """
        List all active rate limiting rules.
        
        This endpoint returns information about the current rate limiter configuration.
        """
        try:
            # Get current limiter information
            info = await limiter.get_algorithm_info()
            
            # Create a rule response for the current configuration
            rule = RuleResponse(
                key="*",  # Wildcard for all keys
                algorithm=info["name"],
                parameters=info["parameters"],
                ttl=limiter.default_ttl,
                created_at=time.time()
            )
            
            return [rule]
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list rules: {str(e)}"
            )
    
    @app.delete("/rules/{key}")
    async def delete_rule(
        key: str,
        limiter: RateLimiter = Depends(get_limiter)
    ):
        """
        Delete a rate limiting rule and reset its state.
        
        Args:
            key: The rate limit key to delete
        """
        try:
            # Reset the rate limit for the key
            await limiter.reset(key)
            
            return {"message": f"Rule for key '{key}' deleted successfully"}
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete rule: {str(e)}"
            )
    
    @app.get("/stats/{key}", response_model=StatsResponse)
    async def get_stats(
        key: str,
        limiter: RateLimiter = Depends(get_limiter)
    ):
        """
        Get rate limiting statistics for a specific key.
        
        Args:
            key: The rate limit key to get stats for
        """
        try:
            stats = await limiter.get_stats(key)
            
            return StatsResponse(
                key=key,
                algorithm=stats["algorithm"],
                stats=stats,
                timestamp=stats["timestamp"]
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get stats: {str(e)}"
            )
    
    @app.get("/health")
    async def health_check(limiter: RateLimiter = Depends(get_limiter)):
        """
        Health check endpoint.
        
        Returns the current status of the rate limiter.
        """
        try:
            info = await limiter.get_algorithm_info()
            
            return {
                "status": "healthy",
                "algorithm": info["name"],
                "backend": info["backend"],
                "timestamp": time.time()
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Health check failed: {str(e)}"
            )
    
    @app.get("/info")
    async def get_info(limiter: RateLimiter = Depends(get_limiter)):
        """
        Get detailed information about the rate limiter configuration.
        """
        try:
            info = await limiter.get_algorithm_info()
            
            return {
                "limiter_info": info,
                "supported_algorithms": [
                    "token_bucket", "leaky_bucket", "fixed_window",
                    "sliding_window", "sliding_log", "hybrid"
                ],
                "timestamp": time.time()
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get info: {str(e)}"
            )
    
    return app


# Import time module for timestamps
import time
