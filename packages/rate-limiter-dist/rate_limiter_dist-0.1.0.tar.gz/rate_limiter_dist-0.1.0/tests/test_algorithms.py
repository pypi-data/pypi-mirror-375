"""
Tests for rate limiting algorithms.
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

from distlimiter.algorithms import (
    TokenBucket, LeakyBucket, FixedWindow, 
    SlidingWindow, SlidingLog, Hybrid
)
from distlimiter.backends.base import BaseBackend


class MockBackend(BaseBackend):
    """Mock backend for testing."""
    
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
        # Simple mock implementation for basic testing
        if "token_bucket" in script.lower():
            return '{"allowed": true, "tokens_remaining": 4, "tokens_consumed": 1, "last_refill": 1234567890.0}'
        elif "fixed_window" in script.lower():
            return '{"allowed": true, "current_count": 1, "max_requests": 10, "window_seconds": 60}'
        elif "sliding_window" in script.lower():
            return '{"allowed": true, "current_count": 1, "previous_count": 0, "sliding_count": 1.0, "max_requests": 10, "window_seconds": 60, "weight": 0.5}'
        elif "sliding_log" in script.lower():
            return '{"allowed": true, "current_count": 1, "max_requests": 10, "window_seconds": 60, "cutoff_time": 1234567890.0}'
        elif "leaky_bucket" in script.lower():
            return '{"allowed": true, "water_level": 1, "capacity": 10, "rate": 1.0, "last_leak_time": 1234567890.0}'
        else:
            return '{"allowed": false}'


@pytest.mark.asyncio
async def test_token_bucket_initialization():
    """Test TokenBucket initialization."""
    # Valid initialization
    tb = TokenBucket(capacity=10, refill_rate=1.0)
    assert tb.capacity == 10
    assert tb.refill_rate == 1.0
    
    # Invalid capacity
    with pytest.raises(ValueError):
        TokenBucket(capacity=0, refill_rate=1.0)
    
    # Invalid refill rate
    with pytest.raises(ValueError):
        TokenBucket(capacity=10, refill_rate=0)


@pytest.mark.asyncio
async def test_fixed_window_initialization():
    """Test FixedWindow initialization."""
    # Valid initialization
    fw = FixedWindow(max_requests=100, window_seconds=60)
    assert fw.max_requests == 100
    assert fw.window_seconds == 60
    
    # Invalid max_requests
    with pytest.raises(ValueError):
        FixedWindow(max_requests=0, window_seconds=60)
    
    # Invalid window_seconds
    with pytest.raises(ValueError):
        FixedWindow(max_requests=100, window_seconds=0)


@pytest.mark.asyncio
async def test_sliding_window_initialization():
    """Test SlidingWindow initialization."""
    # Valid initialization
    sw = SlidingWindow(max_requests=100, window_seconds=60)
    assert sw.max_requests == 100
    assert sw.window_seconds == 60
    
    # Invalid max_requests
    with pytest.raises(ValueError):
        SlidingWindow(max_requests=0, window_seconds=60)
    
    # Invalid window_seconds
    with pytest.raises(ValueError):
        SlidingWindow(max_requests=100, window_seconds=0)


@pytest.mark.asyncio
async def test_leaky_bucket_initialization():
    """Test LeakyBucket initialization."""
    # Valid initialization
    lb = LeakyBucket(rate=5.0)
    assert lb.rate == 5.0
    assert lb.capacity == 10  # Default capacity
    
    # Valid initialization with custom capacity
    lb = LeakyBucket(rate=5.0, capacity=20)
    assert lb.rate == 5.0
    assert lb.capacity == 20
    
    # Invalid rate
    with pytest.raises(ValueError):
        LeakyBucket(rate=0)


@pytest.mark.asyncio
async def test_sliding_log_initialization():
    """Test SlidingLog initialization."""
    # Valid initialization
    sl = SlidingLog(max_requests=50, window_seconds=60)
    assert sl.max_requests == 50
    assert sl.window_seconds == 60
    
    # Invalid max_requests
    with pytest.raises(ValueError):
        SlidingLog(max_requests=0, window_seconds=60)
    
    # Invalid window_seconds
    with pytest.raises(ValueError):
        SlidingLog(max_requests=50, window_seconds=0)


@pytest.mark.asyncio
async def test_hybrid_initialization():
    """Test Hybrid initialization."""
    # Valid initialization
    tb = TokenBucket(capacity=10, refill_rate=1.0)
    sw = SlidingWindow(max_requests=100, window_seconds=60)
    hybrid = Hybrid(token_bucket=tb, sliding_window=sw)
    
    assert hybrid.token_bucket == tb
    assert hybrid.sliding_window == sw
    
    # Invalid token_bucket
    with pytest.raises(ValueError):
        Hybrid(token_bucket="invalid", sliding_window=sw)
    
    # Invalid sliding_window
    with pytest.raises(ValueError):
        Hybrid(token_bucket=tb, sliding_window="invalid")


@pytest.mark.asyncio
async def test_token_bucket_allow():
    """Test TokenBucket allow method."""
    backend = MockBackend()
    tb = TokenBucket(capacity=10, refill_rate=1.0)
    
    allowed, stats = await tb.allow(backend, "test_key")
    
    assert allowed is True
    assert "tokens_remaining" in stats
    assert "tokens_consumed" in stats


@pytest.mark.asyncio
async def test_fixed_window_allow():
    """Test FixedWindow allow method."""
    backend = MockBackend()
    fw = FixedWindow(max_requests=10, window_seconds=60)
    
    allowed, stats = await fw.allow(backend, "test_key")
    
    assert allowed is True
    assert "current_count" in stats
    assert "max_requests" in stats


@pytest.mark.asyncio
async def test_sliding_window_allow():
    """Test SlidingWindow allow method."""
    backend = MockBackend()
    sw = SlidingWindow(max_requests=10, window_seconds=60)
    
    allowed, stats = await sw.allow(backend, "test_key")
    
    assert allowed is True
    assert "sliding_count" in stats
    assert "max_requests" in stats


@pytest.mark.asyncio
async def test_leaky_bucket_allow():
    """Test LeakyBucket allow method."""
    backend = MockBackend()
    lb = LeakyBucket(rate=5.0)
    
    allowed, stats = await lb.allow(backend, "test_key")
    
    assert allowed is True
    assert "water_level" in stats
    assert "capacity" in stats


@pytest.mark.asyncio
async def test_sliding_log_allow():
    """Test SlidingLog allow method."""
    backend = MockBackend()
    sl = SlidingLog(max_requests=10, window_seconds=60)
    
    allowed, stats = await sl.allow(backend, "test_key")
    
    assert allowed is True
    assert "current_count" in stats
    assert "max_requests" in stats


@pytest.mark.asyncio
async def test_hybrid_allow():
    """Test Hybrid allow method."""
    backend = MockBackend()
    tb = TokenBucket(capacity=10, refill_rate=1.0)
    sw = SlidingWindow(max_requests=100, window_seconds=60)
    hybrid = Hybrid(token_bucket=tb, sliding_window=sw)
    
    allowed, stats = await hybrid.allow(backend, "test_key")
    
    assert "token_bucket" in stats
    assert "sliding_window" in stats


@pytest.mark.asyncio
async def test_get_parameters():
    """Test get_parameters method for all algorithms."""
    algorithms = [
        TokenBucket(capacity=10, refill_rate=1.0),
        FixedWindow(max_requests=100, window_seconds=60),
        SlidingWindow(max_requests=100, window_seconds=60),
        LeakyBucket(rate=5.0),
        SlidingLog(max_requests=50, window_seconds=60),
    ]
    
    for algorithm in algorithms:
        params = algorithm.get_parameters()
        assert isinstance(params, dict)
        assert len(params) > 0


@pytest.mark.asyncio
async def test_get_stats():
    """Test get_stats method for all algorithms."""
    backend = MockBackend()
    algorithms = [
        TokenBucket(capacity=10, refill_rate=1.0),
        FixedWindow(max_requests=100, window_seconds=60),
        SlidingWindow(max_requests=100, window_seconds=60),
        LeakyBucket(rate=5.0),
        SlidingLog(max_requests=50, window_seconds=60),
    ]
    
    for algorithm in algorithms:
        stats = await algorithm.get_stats(backend, "test_key")
        assert isinstance(stats, dict)
        assert len(stats) > 0
