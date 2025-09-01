"""
Test settings for CineChainLanka project
"""
import os
from pathlib import Path
from .settings import *

# Use SQLite for testing (faster than MySQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Use in-memory database for fastest tests
    }
}

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Use console email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

# Use faster hashing for tests
HASH_SALT = 'test-salt'

# Disable CSRF for API tests
MIDDLEWARE = [m for m in MIDDLEWARE if 'csrf' not in m.lower()]

# Test-specific settings
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Media files for testing
MEDIA_ROOT = BASE_DIR / 'test_media'

# Static files for testing
STATIC_ROOT = BASE_DIR / 'test_static'

# Create test directories
os.makedirs(MEDIA_ROOT, exist_ok=True)
os.makedirs(STATIC_ROOT, exist_ok=True)

# Disable Redis for testing
REDIS_URL = None

# Test payment methods configuration
PAYMENT_TEST_MODE = True

