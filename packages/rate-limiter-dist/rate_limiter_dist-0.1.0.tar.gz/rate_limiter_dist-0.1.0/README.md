# DistLimiter

A distributed API rate-limiting library for Python that supports multiple rate-limiting algorithms with Redis backend.

## Features

- **Multiple Algorithms**: Token Bucket, Leaky Bucket, Fixed Window, Sliding Window, Sliding Log, and Hybrid
- **Multiple Backends**: Redis (distributed) and Memory (local) backends
- **Memory Efficient**: Optimized data structures and automatic cleanup
- **Modular Installation**: Install only the algorithms you need
- **Framework Support**: FastAPI, Flask, and Django middleware
- **Admin API**: Runtime rule configuration and monitoring
- **Extensible**: Plugin architecture for custom backends

## Installation

### Basic Installation
```bash
pip install distlimiter
```

### Framework-Specific Installation
```bash
# Install with Flask support
pip install distlimiter[flask]

# Install with Django support
pip install distlimiter[django]

# Install with all frameworks
pip install distlimiter[flask,django]
```

### Development Installation
```bash
# Clone the repository
git clone https://github.com/satyam-kr/distlimiter.git
cd distlimiter

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

## Quick Start

### 1. Install
```bash
pip install distlimiter[flask,django]
```

### 2. Start Redis
```bash
# macOS
brew services start redis

# Linux
sudo systemctl start redis-server

# Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### 3. Basic Usage

#### With Redis Backend (Production)
```python
import asyncio
from distlimiter import RateLimiter
from distlimiter.algorithms import TokenBucket
from distlimiter.backends import RedisBackend

async def main():
    # Create Redis backend for distributed rate limiting
    backend = RedisBackend("redis://localhost:6379")
    
    # Create rate limiter with token bucket algorithm
    limiter = RateLimiter(
        algorithm=TokenBucket(capacity=10, refill_rate=1),
        backend=backend,
        key_prefix="api"
    )
    
    # Check if request is allowed
    key = "user123"
    allowed = await limiter.allow(key)
    
    if allowed:
        print("Request allowed")
    else:
        print("Rate limit exceeded")

asyncio.run(main())
```

#### With Memory Backend (Development/Testing)
```python
import asyncio
from distlimiter import RateLimiter
from distlimiter.algorithms import TokenBucket
from distlimiter.backends import MemoryBackend

async def main():
    # Create Memory backend for local development
    backend = MemoryBackend(cleanup_interval=60)
    
    # Create rate limiter with token bucket algorithm
    limiter = RateLimiter(
        algorithm=TokenBucket(capacity=10, refill_rate=1),
        backend=backend,
        key_prefix="api"
    )
    
    # Check if request is allowed
    key = "user123"
    allowed = await limiter.allow(key)
    
    if allowed:
        print("Request allowed")
    else:
        print("Rate limit exceeded")

asyncio.run(main())
```

### 4. Test Everything
```bash
python tests/run_tests.py
```

### FastAPI Integration

```python
from fastapi import FastAPI, Request
from distlimiter.middleware import RateLimitMiddleware
from distlimiter.algorithms import TokenBucket
from distlimiter.backends import RedisBackend

app = FastAPI()

# Create rate limiter
backend = RedisBackend("redis://localhost:6379")
limiter = RateLimiter(
    algorithm=TokenBucket(capacity=100, refill_rate=10),
    backend=backend,
    key_prefix="api"
)

# Add middleware
app.add_middleware(RateLimitMiddleware, limiter=limiter)

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

### Flask Integration

```python
from flask import Flask
from distlimiter.middleware import FlaskRateLimiter
from distlimiter.algorithms import TokenBucket
from distlimiter.backends import RedisBackend

app = Flask(__name__)

# Create rate limiter
backend = RedisBackend("redis://localhost:6379")
limiter = RateLimiter(
    algorithm=TokenBucket(capacity=100, refill_rate=10),
    backend=backend,
    key_prefix="api"
)

# Initialize Flask rate limiter
flask_limiter = FlaskRateLimiter(
    app=app,
    limiter=limiter,
    error_message="Too many requests. Please try again later."
)

@app.route("/")
def root():
    return {"message": "Hello World"}

# Use decorator for specific endpoints
@app.route("/api/sensitive")
@flask_limiter.limit()
def sensitive_endpoint():
    return {"message": "This is a sensitive endpoint"}
```

### Django Integration

```python
# settings.py
from distlimiter import RateLimiter
from distlimiter.algorithms import TokenBucket
from distlimiter.backends import RedisBackend

# Create rate limiter
backend = RedisBackend("redis://localhost:6379")
RATE_LIMITER = RateLimiter(
    algorithm=TokenBucket(capacity=100, refill_rate=10),
    backend=backend,
    key_prefix="api"
)

# Rate limiter settings
RATE_LIMITER_ERROR_MESSAGE = "Rate limit exceeded. Please try again later."
RATE_LIMITER_ERROR_STATUS_CODE = 429
RATE_LIMITER_INCLUDE_HEADERS = True
RATE_LIMITER_EXEMPT_PATHS = ['health/']
RATE_LIMITER_EXEMPT_METHODS = ['GET']

# Add middleware
MIDDLEWARE = [
    'distlimiter.middleware.django.DjangoRateLimitMiddleware',
    # ... other middleware
]

# views.py
from distlimiter.middleware.django import rate_limit

@rate_limit()
def sensitive_view(request):
    return JsonResponse({"message": "This is a sensitive endpoint"})
```

### Admin API

```python
from fastapi import FastAPI
from distlimiter.admin import create_admin_app

app = FastAPI()

# Create admin API
admin_app = create_admin_app(limiter)
app.mount("/admin", admin_app)

# Now you can access:
# POST /admin/rules - Create/update rules
# GET /admin/rules - List all rules
# DELETE /admin/rules/{key} - Remove rule
# GET /admin/stats/{key} - View usage stats
```

## Supported Algorithms

### Token Bucket
Burst-friendly algorithm that refills at a steady rate.

```python
from distlimiter.algorithms import TokenBucket

# 10 tokens capacity, 1 token per second refill rate
algorithm = TokenBucket(capacity=10, refill_rate=1)
```

### Leaky Bucket
Enforces constant rate and smooths bursts.

```python
from distlimiter.algorithms import LeakyBucket

# 5 requests per second
algorithm = LeakyBucket(rate=5)
```

### Fixed Window Counter
Simple counter that resets every window.

```python
from distlimiter.algorithms import FixedWindow

# 100 requests per minute
algorithm = FixedWindow(max_requests=100, window_seconds=60)
```

### Sliding Window Counter
More accurate than fixed window, avoids burst at boundary.

```python
from distlimiter.algorithms import SlidingWindow

# 100 requests per minute
algorithm = SlidingWindow(max_requests=100, window_seconds=60)
```

### Sliding Log
Stores individual timestamps, precise but memory-heavy (optimized).

```python
from distlimiter.algorithms import SlidingLog

# 50 requests per minute
algorithm = SlidingLog(max_requests=50, window_seconds=60)
```

### Hybrid Token + Sliding Window
Combination for burst + fairness control.

```python
from distlimiter.algorithms import Hybrid

# Token bucket: 20 tokens, 2 per second
# Sliding window: 100 requests per minute
algorithm = Hybrid(
    token_bucket=TokenBucket(capacity=20, refill_rate=2),
    sliding_window=SlidingWindow(max_requests=100, window_seconds=60)
)
```

## Configuration

### Environment Variables
Copy `env.example` to `.env` and configure:
```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_SSL=false

# Rate Limiter Configuration
RATE_LIMITER_KEY_PREFIX=distlimiter
RATE_LIMITER_DEFAULT_TTL=3600
```

### Backend Comparison

| Feature | Memory Backend | Redis Backend |
|---------|----------------|---------------|
| **Use Case** | Development, Testing | Production, Distributed |
| **Dependencies** | None | Redis server |
| **Performance** | Very Fast | Fast |
| **Persistence** | No (in-memory) | Yes |
| **Multi-Instance** | No | Yes |
| **Setup** | Zero configuration | Requires Redis |
| **Memory Usage** | Low | Low |
| **Scalability** | Single instance | Multi-instance |

### Backend Configuration

#### Memory Backend
```python
from distlimiter.backends import MemoryBackend

# Basic usage
backend = MemoryBackend()

# With custom cleanup interval
backend = MemoryBackend(cleanup_interval=60)  # Cleanup every 60 seconds
```

#### Redis Backend
```python
from distlimiter.backends import RedisBackend

# Basic connection
backend = RedisBackend("redis://localhost:6379")

# With custom settings
backend = RedisBackend(
    "redis://localhost:6379",
    max_connections=20,
    key_prefix="myapp",
    default_ttl=3600
)

# Production with SSL
backend = RedisBackend(
    "rediss://username:password@redis.example.com:6379",
    ssl=True,
    ssl_cert_reqs="required"
)
```

### Rate Limiter Configuration

```python
from distlimiter import RateLimiter

limiter = RateLimiter(
    algorithm=TokenBucket(capacity=10, refill_rate=1),
    backend=backend,
    key_prefix="api",
    default_ttl=3600,
    key_extractor=lambda request: request.client.host
)
```

## API Reference

### RateLimiter

```python
class RateLimiter:
    def __init__(
        self,
        algorithm: BaseAlgorithm,
        backend: BaseBackend,
        key_prefix: str = "distlimiter",
        default_ttl: int = 3600,
        key_extractor: Optional[Callable] = None
    )
    
    async def allow(self, key: str) -> bool
    async def get_stats(self, key: str) -> Dict[str, Any]
    async def reset(self, key: str) -> None
```

### Algorithms

All algorithms inherit from `BaseAlgorithm` and implement:

```python
class BaseAlgorithm(ABC):
    @abstractmethod
    async def allow(self, backend: BaseBackend, key: str) -> Tuple[bool, Dict[str, Any]]
    
    @abstractmethod
    async def get_stats(self, backend: BaseBackend, key: str) -> Dict[str, Any]
```

### Backends

All backends inherit from `BaseBackend` and implement:

```python
class BaseBackend(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[str]
    
    @abstractmethod
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None
    
    @abstractmethod
    async def delete(self, key: str) -> None
    
    @abstractmethod
    async def execute_lua(self, script: str, keys: List[str], args: List[str]) -> Any
```

## Testing

### Quick Test
```bash
# Run comprehensive test suite
python tests/run_tests.py
```

### Individual Tests
```bash
# Installation test
python tests/scripts/test_installation.py

# Core functionality test
python tests/scripts/test_core.py

# Unit tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=distlimiter -v
```

### Redis Integration Tests
```bash
# Start Redis (macOS)
brew services start redis

# Start Redis (Linux)
sudo systemctl start redis-server

# Start Redis (Docker)
docker run -d -p 6379:6379 redis:7-alpine

# Run examples
python examples/basic_usage.py
python examples/backend_comparison.py
```

## Development

### Project Structure

```
distlimiter/
├── distlimiter/                    # Main package
│   ├── __init__.py                # Package exports
│   ├── core.py                    # RateLimiter class
│   ├── algorithms/                # Rate limiting algorithms
│   │   ├── __init__.py
│   │   ├── base.py               # Base algorithm interface
│   │   ├── token_bucket.py       # Token bucket algorithm
│   │   ├── leaky_bucket.py       # Leaky bucket algorithm
│   │   ├── fixed_window.py       # Fixed window counter
│   │   ├── sliding_window.py     # Sliding window counter
│   │   ├── sliding_log.py        # Sliding log algorithm
│   │   └── hybrid.py             # Hybrid algorithm
│   ├── backends/                  # Storage backends
│   │   ├── __init__.py
│   │   ├── base.py               # Base backend interface
│   │   ├── redis.py              # Redis backend
│   │   └── memory.py             # Memory backend
│   ├── middleware/                # Framework middleware
│   │   ├── __init__.py
│   │   ├── fastapi.py            # FastAPI middleware
│   │   ├── flask.py              # Flask middleware
│   │   └── django.py             # Django middleware
│   └── admin/                     # Admin API
│       ├── __init__.py
│       └── api.py                # Admin endpoints
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_algorithms.py        # Algorithm tests
│   ├── run_tests.py              # Comprehensive test runner
│   └── scripts/                  # Test scripts
│       ├── test_installation.py  # Installation test
│       ├── test_core.py          # Core functionality test
│       ├── TEST_RESULTS.md       # Test results
│       └── REDIS_SETUP.md        # Redis setup guide
├── examples/                      # Usage examples
│   ├── basic_usage.py            # Basic usage example
│   ├── backend_comparison.py     # Backend comparison example
│   ├── fastapi_example.py        # FastAPI integration
│   ├── flask_example.py          # Flask integration
│   └── django_example.py         # Django integration
├── pyproject.toml                # Project configuration
├── README.md                     # This file
├── requirements-dev.txt          # Development dependencies
├── docker-compose.yml            # Docker setup
├── Dockerfile                    # Container configuration
├── .gitignore                    # Git ignore rules
├── env.example                   # Environment variables template
└── LICENSE                       # MIT License
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
