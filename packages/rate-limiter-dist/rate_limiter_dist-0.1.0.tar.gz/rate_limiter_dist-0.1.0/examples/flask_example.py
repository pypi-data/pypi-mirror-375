"""
Flask integration example for DistLimiter.

This example demonstrates how to integrate rate limiting with Flask.
"""

from flask import Flask, request, jsonify
from distlimiter import RateLimiter, FlaskRateLimiter
from distlimiter.algorithms import TokenBucket
from distlimiter.backends import RedisBackend

# Create Flask app
app = Flask(__name__)

# Create rate limiter
backend = RedisBackend("redis://localhost:6379")
limiter = RateLimiter(
    algorithm=TokenBucket(capacity=10, refill_rate=2),  # 10 tokens, 2 per second
    backend=backend,
    key_prefix="flask_api"
)

# Initialize Flask rate limiter
flask_limiter = FlaskRateLimiter(
    app=app,
    limiter=limiter,
    error_message="Too many requests. Please try again later.",
    include_headers=True
)


@app.route('/')
def root():
    """Root endpoint."""
    return jsonify({
        "message": "Hello World",
        "rate_limited": True
    })


@app.route('/api/data')
def get_data():
    """Example API endpoint."""
    return jsonify({
        "data": "This is some protected data",
        "timestamp": time.time()
    })


@app.route('/api/user/<user_id>')
def get_user(user_id):
    """Example endpoint with user-specific rate limiting."""
    return jsonify({
        "user_id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com"
    })


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Example POST endpoint."""
    data = request.get_data()
    return jsonify({
        "message": "File uploaded successfully",
        "size": len(data)
    })


# Example of using the decorator for specific endpoints
@app.route('/api/sensitive')
@flask_limiter.limit()
def sensitive_endpoint():
    """Endpoint with custom rate limiting."""
    return jsonify({
        "message": "This is a sensitive endpoint",
        "rate_limited": True
    })


# Custom key extractor example
def custom_key_extractor(request):
    """Extract rate limit key based on API key header."""
    api_key = request.headers.get('X-API-Key')
    if api_key:
        return f"api_key:{api_key}"
    return request.remote_addr


@app.route('/api/premium')
@flask_limiter.limit(key_extractor=custom_key_extractor)
def premium_endpoint():
    """Premium endpoint with custom key extraction."""
    return jsonify({
        "message": "This is a premium endpoint",
        "rate_limited": True
    })


if __name__ == '__main__':
    import time
    print("Starting Flask example server...")
    print("Server will be available at: http://localhost:5000")
    print("API endpoints:")
    print("- GET  /")
    print("- GET  /api/data")
    print("- GET  /api/user/<user_id>")
    print("- POST /api/upload")
    print("- GET  /api/sensitive")
    print("- GET  /api/premium")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
