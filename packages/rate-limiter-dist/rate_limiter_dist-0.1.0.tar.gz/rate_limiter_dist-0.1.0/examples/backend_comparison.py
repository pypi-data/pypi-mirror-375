#!/usr/bin/env python3
"""
Backend Comparison Example

This example demonstrates the difference between using the MemoryBackend
and RedisBackend for rate limiting.

MemoryBackend is suitable for:
- Local development
- Testing
- Single-instance applications
- Prototyping

RedisBackend is suitable for:
- Production deployments
- Multi-instance applications
- Distributed systems
- High availability
"""

import asyncio
import time
from distlimiter import RateLimiter
from distlimiter.algorithms import TokenBucket, FixedWindow
from distlimiter.backends import MemoryBackend, RedisBackend


async def test_backend(backend_name: str, backend, algorithm_name: str, algorithm):
    """Test a backend with a specific algorithm."""
    print(f"\n=== {backend_name} with {algorithm_name} ===")
    
    limiter = RateLimiter(
        algorithm=algorithm,
        backend=backend,
        key_prefix=f"test_{backend_name.lower()}"
    )
    
    # Test multiple requests
    for i in range(1, 6):
        start_time = time.time()
        allowed = await limiter.allow(f"user{i}")
        end_time = time.time()
        
        status = "✓" if allowed else "✗"
        response_time = (end_time - start_time) * 1000  # Convert to ms
        
        print(f"Request {i}: {status} - Response time: {response_time:.2f}ms")
        
        if not allowed:
            print(f"  Rate limit exceeded for user{i}")
        
        # Small delay between requests
        await asyncio.sleep(0.1)
    
    # Get stats
    stats = await limiter.get_stats("user1")
    print(f"Stats for user1: {stats}")
    
    # Clean up
    await backend.close()


async def main():
    """Main function to demonstrate both backends."""
    print("🚀 DistLimiter Backend Comparison")
    print("=" * 50)
    
    # Test Memory Backend
    print("\n📦 Testing Memory Backend")
    print("-" * 30)
    
    # Memory backend with Token Bucket
    memory_backend = MemoryBackend(cleanup_interval=30)
    token_bucket = TokenBucket(capacity=3, refill_rate=1)
    await test_backend("Memory", memory_backend, "TokenBucket", token_bucket)
    
    # Memory backend with Fixed Window
    memory_backend2 = MemoryBackend(cleanup_interval=30)
    fixed_window = FixedWindow(max_requests=3, window_seconds=60)
    await test_backend("Memory", memory_backend2, "FixedWindow", fixed_window)
    
    # Test Redis Backend (if available)
    print("\n🔗 Testing Redis Backend")
    print("-" * 30)
    
    try:
        # Redis backend with Token Bucket
        redis_backend = RedisBackend("redis://localhost:6379")
        token_bucket = TokenBucket(capacity=3, refill_rate=1)
        await test_backend("Redis", redis_backend, "TokenBucket", token_bucket)
        
        # Redis backend with Fixed Window
        redis_backend2 = RedisBackend("redis://localhost:6379")
        fixed_window = FixedWindow(max_requests=3, window_seconds=60)
        await test_backend("Redis", redis_backend2, "FixedWindow", fixed_window)
        
    except Exception as e:
        print(f"❌ Redis not available: {e}")
        print("   To test Redis backend:")
        print("   1. Install Redis: brew install redis")
        print("   2. Start Redis: brew services start redis")
    
    print("\n" + "=" * 50)
    print("✅ Backend comparison completed!")
    
    print("\n📊 Summary:")
    print("• Memory Backend: Fast, no external dependencies, single-instance only")
    print("• Redis Backend: Distributed, persistent, multi-instance support")
    print("\n💡 Use Memory Backend for development/testing")
    print("💡 Use Redis Backend for production deployments")


if __name__ == "__main__":
    asyncio.run(main())
