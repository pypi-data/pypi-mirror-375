"""
FastAPI integration example for DistLimiter.

This example demonstrates how to integrate rate limiting with FastAPI.
"""

import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

from distlimiter import RateLimiter
from distlimiter.algorithms import TokenBucket
from distlimiter.backends import RedisBackend
from distlimiter.middleware import RateLimitMiddleware
from distlimiter.admin import create_admin_app


# Create FastAPI app
app = FastAPI(
    title="DistLimiter FastAPI Example",
    description="Example FastAPI application with rate limiting",
    version="1.0.0"
)

# Create rate limiter
backend = RedisBackend("redis://localhost:6379")
limiter = RateLimiter(
    algorithm=TokenBucket(capacity=10, refill_rate=2),  # 10 tokens, 2 per second
    backend=backend,
    key_prefix="api"
)

# Add rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    limiter=limiter,
    error_message="Too many requests. Please try again later.",
    include_headers=True
)

# Create admin API
admin_app = create_admin_app(limiter)
app.mount("/admin", admin_app)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Hello World", "rate_limited": True}


@app.get("/api/data")
async def get_data():
    """Example API endpoint."""
    return {
        "data": "This is some protected data",
        "timestamp": asyncio.get_event_loop().time()
    }


@app.get("/api/user/{user_id}")
async def get_user(user_id: str):
    """Example endpoint with user-specific rate limiting."""
    return {
        "user_id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com"
    }


@app.post("/api/upload")
async def upload_file(request: Request):
    """Example POST endpoint."""
    body = await request.body()
    return {
        "message": "File uploaded successfully",
        "size": len(body)
    }


@app.exception_handler(429)
async def rate_limit_exception_handler(request: Request, exc):
    """Custom handler for rate limit exceptions."""
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": "You have exceeded the rate limit. Please try again later.",
            "retry_after": 60  # Suggest retry after 60 seconds
        }
    )


if __name__ == "__main__":
    print("Starting FastAPI example server...")
    print("Main API: http://localhost:8000")
    print("Admin API: http://localhost:8000/admin")
    print("API Docs: http://localhost:8000/docs")
    print("Admin Docs: http://localhost:8000/admin/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
