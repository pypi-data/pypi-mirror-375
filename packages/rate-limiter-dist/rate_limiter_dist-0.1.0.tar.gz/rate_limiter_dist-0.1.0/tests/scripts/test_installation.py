#!/usr/bin/env python3
"""
Simple test script to verify DistLimiter installation.
"""

import asyncio
import sys

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from distlimiter import RateLimiter
        from distlimiter.algorithms import TokenBucket, FixedWindow
        from distlimiter.backends import RedisBackend
        from distlimiter.middleware import RateLimitMiddleware, FlaskRateLimiter, DjangoRateLimitMiddleware
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

async def test_basic_functionality():
    """Test basic functionality with mock backend."""
    print("Testing basic functionality...")
    
    try:
        from distlimiter import RateLimiter
        from distlimiter.algorithms import TokenBucket
        from distlimiter.backends.base import BaseBackend
        
        # Create a simple mock backend
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
        
        # Test rate limiter
        backend = MockBackend()
        algorithm = TokenBucket(capacity=10, refill_rate=1.0)
        limiter = RateLimiter(algorithm=algorithm, backend=backend)
        
        # Test allow method
        allowed = await limiter.allow("test_key")
        assert allowed is True
        
        # Test get_stats method
        stats = await limiter.get_stats("test_key")
        assert isinstance(stats, dict)
        
        print("✓ Basic functionality works")
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("DistLimiter Installation Test")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        sys.exit(1)
    
    # Test basic functionality
    if not asyncio.run(test_basic_functionality()):
        sys.exit(1)
    
    print("\n" + "=" * 40)
    print("✓ All tests passed! DistLimiter is working correctly.")
    print("\nYou can now:")
    print("- Run examples: python examples/basic_usage.py")
    print("- Start FastAPI server: python examples/fastapi_example.py")
    print("- Start Flask server: python examples/flask_example.py")
    print("- Start Django server: python examples/django_example.py")
    print("- Run tests: pytest tests/")

if __name__ == "__main__":
    main()
