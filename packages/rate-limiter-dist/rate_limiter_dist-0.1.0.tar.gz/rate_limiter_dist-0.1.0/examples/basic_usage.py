"""
Basic usage example for DistLimiter.

This example demonstrates how to use the rate limiter with different algorithms
and backends (Redis and Memory).
"""

import asyncio
import time
from distlimiter import RateLimiter
from distlimiter.algorithms import TokenBucket, FixedWindow, SlidingWindow
from distlimiter.backends import RedisBackend, MemoryBackend


async def token_bucket_example():
    """Example using Token Bucket algorithm with Redis backend."""
    print("=== Token Bucket Example (Redis) ===")
    
    # Create Redis backend
    backend = RedisBackend("redis://localhost:6379")
    
    # Create rate limiter with token bucket
    limiter = RateLimiter(
        algorithm=TokenBucket(capacity=5, refill_rate=1),  # 5 tokens, 1 per second
        backend=backend,
        key_prefix="example"
    )
    
    key = "user123"
    
    # Simulate rapid requests
    for i in range(10):
        allowed = await limiter.allow(key)
        stats = await limiter.get_stats(key)
        
        print(f"Request {i+1}: {'✓' if allowed else '✗'} - Tokens: {stats['tokens_remaining']}")
        
        if i < 4:  # Wait a bit between requests
            await asyncio.sleep(0.1)
    
    await backend.close()


async def token_bucket_memory_example():
    """Example using Token Bucket algorithm with Memory backend."""
    print("\n=== Token Bucket Example (Memory) ===")
    
    # Create Memory backend
    backend = MemoryBackend(cleanup_interval=30)
    
    # Create rate limiter with token bucket
    limiter = RateLimiter(
        algorithm=TokenBucket(capacity=5, refill_rate=1),  # 5 tokens, 1 per second
        backend=backend,
        key_prefix="example"
    )
    
    key = "user123"
    
    # Simulate rapid requests
    for i in range(10):
        allowed = await limiter.allow(key)
        stats = await limiter.get_stats(key)
        
        print(f"Request {i+1}: {'✓' if allowed else '✗'} - Tokens: {stats['tokens_remaining']}")
        
        if i < 4:  # Wait a bit between requests
            await asyncio.sleep(0.1)
    
    await backend.close()


async def fixed_window_example():
    """Example using Fixed Window algorithm."""
    print("\n=== Fixed Window Example ===")
    
    backend = RedisBackend("redis://localhost:6379")
    
    limiter = RateLimiter(
        algorithm=FixedWindow(max_requests=3, window_seconds=10),  # 3 requests per 10 seconds
        backend=backend,
        key_prefix="example"
    )
    
    key = "user456"
    
    # Simulate requests
    for i in range(5):
        allowed = await limiter.allow(key)
        stats = await limiter.get_stats(key)
        
        print(f"Request {i+1}: {'✓' if allowed else '✗'} - Count: {stats['current_count']}/{stats['max_requests']}")
        
        await asyncio.sleep(1)
    
    await backend.close()


async def sliding_window_example():
    """Example using Sliding Window algorithm."""
    print("\n=== Sliding Window Example ===")
    
    backend = RedisBackend("redis://localhost:6379")
    
    limiter = RateLimiter(
        algorithm=SlidingWindow(max_requests=3, window_seconds=10),  # 3 requests per 10 seconds
        backend=backend,
        key_prefix="example"
    )
    
    key = "user789"
    
    # Simulate requests
    for i in range(5):
        allowed = await limiter.allow(key)
        stats = await limiter.get_stats(key)
        
        print(f"Request {i+1}: {'✓' if allowed else '✗'} - Sliding Count: {stats['sliding_count']:.2f}/{stats['max_requests']}")
        
        await asyncio.sleep(1)
    
    await backend.close()


async def main():
    """Run all examples."""
    try:
        # Test with Redis backend
        await token_bucket_example()
        await fixed_window_example()
        await sliding_window_example()
        
        # Test with Memory backend (no Redis required)
        await token_bucket_memory_example()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Try starting Redis: brew services start redis")
        print("💡 Or use Memory backend for testing without Redis")
        
        print("\n=== Examples completed ===")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure Redis is running on localhost:6379")


if __name__ == "__main__":
    asyncio.run(main())
