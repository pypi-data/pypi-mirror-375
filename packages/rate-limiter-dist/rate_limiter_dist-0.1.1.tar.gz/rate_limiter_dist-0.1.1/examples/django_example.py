"""
Django integration example for DistLimiter.

This example demonstrates how to integrate rate limiting with Django.
Note: This is a simplified example. In a real Django project, you would
configure this in your settings.py and urls.py files.
"""

import os
import sys
import django
from django.conf import settings
from django.http import JsonResponse
from django.urls import path
from django.core.wsgi import get_wsgi_application
from django.views.decorators.csrf import csrf_exempt

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='your-secret-key-here',
        ROOT_URLCONF=__name__,
        MIDDLEWARE=[
            'distlimiter.middleware.django.DjangoRateLimitMiddleware',
        ],
        # Rate limiter configuration
        RATE_LIMITER=None,  # Will be set below
        RATE_LIMITER_ERROR_MESSAGE='Rate limit exceeded. Please try again later.',
        RATE_LIMITER_ERROR_STATUS_CODE=429,
        RATE_LIMITER_INCLUDE_HEADERS=True,
        RATE_LIMITER_EXEMPT_PATHS=['health/'],
        RATE_LIMITER_EXEMPT_METHODS=['GET'],
    )

# Initialize Django
django.setup()

# Import after Django is configured
from distlimiter import RateLimiter
from distlimiter.algorithms import TokenBucket
from distlimiter.backends import RedisBackend
from distlimiter.middleware.django import rate_limit

# Create rate limiter
backend = RedisBackend("redis://localhost:6379")
limiter = RateLimiter(
    algorithm=TokenBucket(capacity=10, refill_rate=2),  # 10 tokens, 2 per second
    backend=backend,
    key_prefix="django_api"
)

# Set the rate limiter in Django settings
settings.RATE_LIMITER = limiter


# Django views
def root_view(request):
    """Root endpoint."""
    return JsonResponse({
        "message": "Hello World",
        "rate_limited": True
    })


def data_view(request):
    """Example API endpoint."""
    return JsonResponse({
        "data": "This is some protected data",
        "timestamp": time.time()
    })


def user_view(request, user_id):
    """Example endpoint with user-specific rate limiting."""
    return JsonResponse({
        "user_id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com"
    })


@csrf_exempt
def upload_view(request):
    """Example POST endpoint."""
    if request.method == 'POST':
        data = request.body
        return JsonResponse({
            "message": "File uploaded successfully",
            "size": len(data)
        })
    return JsonResponse({"error": "Method not allowed"}, status=405)


def health_view(request):
    """Health check endpoint (exempt from rate limiting)."""
    return JsonResponse({
        "status": "healthy",
        "timestamp": time.time()
    })


# Example of using the decorator for specific endpoints
@rate_limit()
def sensitive_view(request):
    """Endpoint with custom rate limiting."""
    return JsonResponse({
        "message": "This is a sensitive endpoint",
        "rate_limited": True
    })


# Custom key extractor example
def custom_key_extractor(request):
    """Extract rate limit key based on API key header."""
    api_key = request.META.get('HTTP_X_API_KEY')
    if api_key:
        return f"api_key:{api_key}"
    return request.META.get('REMOTE_ADDR', 'unknown')


@rate_limit(key_extractor=custom_key_extractor)
def premium_view(request):
    """Premium endpoint with custom key extraction."""
    return JsonResponse({
        "message": "This is a premium endpoint",
        "rate_limited": True
    })


# URL patterns
urlpatterns = [
    path('', root_view, name='root'),
    path('api/data/', data_view, name='data'),
    path('api/user/<str:user_id>/', user_view, name='user'),
    path('api/upload/', upload_view, name='upload'),
    path('api/sensitive/', sensitive_view, name='sensitive'),
    path('api/premium/', premium_view, name='premium'),
    path('health/', health_view, name='health'),
]


# WSGI application
application = get_wsgi_application()


if __name__ == '__main__':
    import time
    from django.core.management import execute_from_command_line
    
    print("Starting Django example server...")
    print("Server will be available at: http://localhost:8000")
    print("API endpoints:")
    print("- GET  /")
    print("- GET  /api/data/")
    print("- GET  /api/user/<user_id>/")
    print("- POST /api/upload/")
    print("- GET  /api/sensitive/")
    print("- GET  /api/premium/")
    print("- GET  /health/")
    
    # Run Django development server
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
