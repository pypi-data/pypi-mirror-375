"""
DistLimiter - A distributed API rate-limiting library for Python.

This library provides multiple rate-limiting algorithms with Redis backend
for distributed state management across multiple nodes.
"""

from .core import RateLimiter
from .algorithms.base import BaseAlgorithm
from .backends.base import BaseBackend
from .backends.redis import RedisBackend
from .backends.memory import MemoryBackend

# Algorithm imports - these will be available based on installation
try:
    from .algorithms.token_bucket import TokenBucket
except ImportError:
    TokenBucket = None

try:
    from .algorithms.leaky_bucket import LeakyBucket
except ImportError:
    LeakyBucket = None

try:
    from .algorithms.fixed_window import FixedWindow
except ImportError:
    FixedWindow = None

try:
    from .algorithms.sliding_window import SlidingWindow
except ImportError:
    SlidingWindow = None

try:
    from .algorithms.sliding_log import SlidingLog
except ImportError:
    SlidingLog = None

try:
    from .algorithms.hybrid import Hybrid
except ImportError:
    Hybrid = None

# Middleware imports
try:
    from .middleware.fastapi import RateLimitMiddleware
except ImportError:
    RateLimitMiddleware = None

try:
    from .middleware.flask import FlaskRateLimiter
except ImportError:
    FlaskRateLimiter = None

try:
    from .middleware.django import DjangoRateLimitMiddleware, rate_limit
except ImportError:
    DjangoRateLimitMiddleware = None
    rate_limit = None

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "RateLimiter",
    "BaseAlgorithm",
    "BaseBackend",
    "RedisBackend",
    "MemoryBackend",
    "TokenBucket",
    "LeakyBucket",
    "FixedWindow",
    "SlidingWindow",
    "SlidingLog",
    "Hybrid",
    "RateLimitMiddleware",      # FastAPI
    "FlaskRateLimiter",         # Flask
    "DjangoRateLimitMiddleware", # Django
    "rate_limit",               # Django decorator
]
