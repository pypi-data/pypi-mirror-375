# Redis Setup Guide for DistLimiter

## 🚀 Quick Start

### 1. **Install Redis**

**macOS (Homebrew):**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
```

**Docker:**
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

### 2. **Verify Redis is Running**
```bash
redis-cli ping
# Should return: PONG
```

### 3. **Test DistLimiter with Redis**
```bash
python examples/basic_usage.py
```

## 🔧 Configuration Options

### **Environment Variables**
Create a `.env` file in your project root:
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

### **Direct Configuration**
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
```

### **Docker Compose**
Use the provided `docker-compose.yml`:
```bash
docker-compose up -d
```

## 🌐 Redis URL Formats

### **Local Development**
```python
# Default local Redis
backend = RedisBackend("redis://localhost:6379")

# With database selection
backend = RedisBackend("redis://localhost:6379/1")

# With password
backend = RedisBackend("redis://:password@localhost:6379")
```

### **Production**
```python
# Redis Cloud
backend = RedisBackend("redis://username:password@redis-cloud.com:12345")

# AWS ElastiCache
backend = RedisBackend("redis://my-cluster.xxxxx.cache.amazonaws.com:6379")

# Google Cloud Memorystore
backend = RedisBackend("redis://10.0.0.1:6379")
```

### **SSL/TLS**
```python
# With SSL
backend = RedisBackend("rediss://localhost:6379")

# With custom SSL settings
backend = RedisBackend(
    "rediss://localhost:6379",
    ssl=True,
    ssl_cert_reqs=None
)
```

## 🔍 Monitoring Redis

### **Redis CLI Commands**
```bash
# Monitor Redis operations
redis-cli monitor

# Check memory usage
redis-cli info memory

# List all keys
redis-cli keys "*"

# Check specific distlimiter keys
redis-cli keys "distlimiter:*"

# Get key info
redis-cli ttl "distlimiter:tokenbucket:user123"
```

### **Redis Desktop Clients**
- **RedisInsight** (Official GUI)
- **Redis Desktop Manager**
- **Another Redis Desktop Manager**

## 🧪 Testing with Redis

### **1. Start Redis**
```bash
# macOS
brew services start redis

# Linux
sudo systemctl start redis-server

# Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### **2. Run Examples**
```bash
# Basic usage
python examples/basic_usage.py

# FastAPI example
python examples/fastapi_example.py

# Flask example
python examples/flask_example.py

# Django example
python examples/django_example.py
```

### **3. Test Admin API**
```bash
# Start FastAPI example
python examples/fastapi_example.py

# Access admin API
curl http://localhost:8000/admin/health
curl http://localhost:8000/admin/info
```

## 🔒 Security Considerations

### **Production Redis Setup**
1. **Use strong passwords**
2. **Enable SSL/TLS**
3. **Restrict network access**
4. **Use Redis ACLs**
5. **Regular backups**

### **Example Production Configuration**
```python
backend = RedisBackend(
    "rediss://username:strong_password@redis.example.com:6379",
    max_connections=50,
    key_prefix="prod:distlimiter",
    default_ttl=3600,
    ssl=True,
    ssl_cert_reqs="required"
)
```

## 📊 Performance Tuning

### **Redis Configuration**
```bash
# /etc/redis/redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### **Connection Pooling**
```python
backend = RedisBackend(
    "redis://localhost:6379",
    max_connections=20,  # Adjust based on load
    retry_on_timeout=True,
    socket_keepalive=True
)
```

## 🚨 Troubleshooting

### **Common Issues**

1. **Connection Refused**
   ```bash
   # Check if Redis is running
   redis-cli ping
   
   # Start Redis if needed
   brew services start redis
   ```

2. **Memory Issues**
   ```bash
   # Check memory usage
   redis-cli info memory
   
   # Clear all keys (development only)
   redis-cli flushall
   ```

3. **Performance Issues**
   ```bash
   # Monitor Redis operations
   redis-cli monitor
   
   # Check slow queries
   redis-cli slowlog get 10
   ```

### **Debug Mode**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# This will show Redis operations
backend = RedisBackend("redis://localhost:6379")
```

## 📚 Additional Resources

- [Redis Documentation](https://redis.io/documentation)
- [Redis Commands](https://redis.io/commands)
- [Redis Configuration](https://redis.io/topics/config)
- [Redis Security](https://redis.io/topics/security)
