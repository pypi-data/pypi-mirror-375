"""
Rate limiting algorithms package.
"""

from .base import BaseAlgorithm

# Conditional imports based on installation
try:
    from .token_bucket import TokenBucket
except ImportError:
    TokenBucket = None

try:
    from .leaky_bucket import LeakyBucket
except ImportError:
    LeakyBucket = None

try:
    from .fixed_window import FixedWindow
except ImportError:
    FixedWindow = None

try:
    from .sliding_window import SlidingWindow
except ImportError:
    SlidingWindow = None

try:
    from .sliding_log import SlidingLog
except ImportError:
    SlidingLog = None

try:
    from .hybrid import Hybrid
except ImportError:
    Hybrid = None

__all__ = [
    "BaseAlgorithm",
    "TokenBucket",
    "LeakyBucket",
    "FixedWindow",
    "SlidingWindow",
    "SlidingLog",
    "Hybrid",
]
