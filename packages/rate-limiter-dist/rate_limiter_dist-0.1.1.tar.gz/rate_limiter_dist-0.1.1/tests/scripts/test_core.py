#!/usr/bin/env python3
"""
Simple test script to verify core DistLimiter functionality without Redis.
"""

import asyncio
import sys
from unittest.mock import AsyncMock, MagicMock

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from distlimiter import RateLimiter
        from distlimiter.algorithms import TokenBucket, FixedWindow, SlidingWindow
        from distlimiter.backends.base import BaseBackend
        from distlimiter.backends.memory import MemoryBackend
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

async def test_algorithms():
    """Test algorithm initialization and basic functionality."""
    print("Testing algorithms...")
    
    try:
        from distlimiter.algorithms import TokenBucket, FixedWindow, SlidingWindow, LeakyBucket, SlidingLog
        
        # Test TokenBucket
        tb = TokenBucket(capacity=10, refill_rate=1.0)
        assert tb.capacity == 10
        assert tb.refill_rate == 1.0
        print("✓ TokenBucket initialization")
        
        # Test FixedWindow
        fw = FixedWindow(max_requests=100, window_seconds=60)
        assert fw.max_requests == 100
        assert fw.window_seconds == 60
        print("✓ FixedWindow initialization")
        
        # Test SlidingWindow
        sw = SlidingWindow(max_requests=100, window_seconds=60)
        assert sw.max_requests == 100
        assert sw.window_seconds == 60
        print("✓ SlidingWindow initialization")
        
        # Test LeakyBucket
        lb = LeakyBucket(rate=5.0)
        assert lb.rate == 5.0
        print("✓ LeakyBucket initialization")
        
        # Test SlidingLog
        sl = SlidingLog(max_requests=50, window_seconds=60)
        assert sl.max_requests == 50
        assert sl.window_seconds == 60
        print("✓ SlidingLog initialization")
        
        return True
        
    except Exception as e:
        print(f"✗ Algorithm test failed: {e}")
        return False

async def test_rate_limiter():
    """Test RateLimiter with mock backend and memory backend."""
    print("Testing RateLimiter...")
    
    try:
        from distlimiter import RateLimiter
        from distlimiter.algorithms import TokenBucket
        from distlimiter.backends.base import BaseBackend
        from distlimiter.backends.memory import MemoryBackend
        
        # Test with Memory Backend
        memory_backend = MemoryBackend(cleanup_interval=30)
        algorithm = TokenBucket(capacity=10, refill_rate=1.0)
        limiter = RateLimiter(algorithm=algorithm, backend=memory_backend)
        
        # Test allow method
        allowed = await limiter.allow("test_key")
        assert allowed is True
        
        # Test get_stats method
        stats = await limiter.get_stats("test_key")
        assert "tokens_remaining" in stats
        
        await memory_backend.close()
        
        # Test with Mock Backend (fallback)
        class MockBackend(BaseBackend):
            def __init__(self):
                self.data = {}
            
            async def get(self, key: str):
                return self.data.get(key)
            
            async def set(self, key: str, value: str, ttl=None):
                self.data[key] = value
            
            async def delete(self, key: str):
                if key in self.data:
                    del self.data[key]
            
            async def execute_lua(self, script: str, keys: list, args: list):
                return '{"allowed": true, "tokens_remaining": 4, "tokens_consumed": 1, "last_refill": 1234567890.0}'
        
        # Test RateLimiter with mock backend
        backend = MockBackend()
        limiter = RateLimiter(algorithm=algorithm, backend=backend)
        
        # Test allow method
        allowed = await limiter.allow("test_key")
        assert allowed is True
        
        # Test get_stats method
        stats = await limiter.get_stats("test_key")
        assert isinstance(stats, dict)
        
        print("✓ RateLimiter functionality")
        return True
        
    except Exception as e:
        print(f"✗ RateLimiter test failed: {e}")
        return False

async def test_middleware_imports():
    """Test middleware imports."""
    print("Testing middleware imports...")
    
    try:
        from distlimiter.middleware import RateLimitMiddleware, FlaskRateLimiter, DjangoRateLimitMiddleware
        print("✓ All middleware imports successful")
        return True
    except ImportError as e:
        print(f"✗ Middleware import failed: {e}")
        return False

def main():
    """Run all tests."""
    print("DistLimiter Core Functionality Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        sys.exit(1)
    
    # Test algorithms
    if not asyncio.run(test_algorithms()):
        sys.exit(1)
    
    # Test rate limiter
    if not asyncio.run(test_rate_limiter()):
        sys.exit(1)
    
    # Test middleware imports
    if not asyncio.run(test_middleware_imports()):
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✓ All core functionality tests passed!")
    print("\nCore components working:")
    print("- Algorithm implementations")
    print("- RateLimiter class")
    print("- Backend interface")
    print("- Middleware imports")
    print("\nTo test with Redis:")
    print("1. Start Redis: brew services start redis")
    print("2. Run examples: python examples/basic_usage.py")

if __name__ == "__main__":
    main()
