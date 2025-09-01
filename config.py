# Configuration file for CineChainLanka project
# Copy this file to .env and fill in your actual values

# Django Settings
SECRET_KEY = "django-insecure--3kp&z--j=)kjne%)gxitk!dgv7mussfi*ocz9v8z9=qwt#=bp"
DEBUG = True
ALLOWED_HOSTS = "localhost,127.0.0.1"

# Database Settings
DB_NAME = "cinechain_lanka"
DB_USER = "root"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_PORT = "3306"

# Email Settings
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = "587"
EMAIL_USE_TLS = "True"
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""

# Redis Settings
REDIS_URL = "redis://localhost:6379/0"

# Payment Provider Settings
LANKA_QR_API_KEY = ""
LANKA_QR_API_SECRET = ""
EZ_CASH_API_KEY = ""
EZ_CASH_API_SECRET = ""
FRIMI_API_KEY = ""
FRIMI_API_SECRET = ""

# Blockchain Settings
ETHEREUM_NETWORK = "testnet"
POLYGON_NETWORK = "testnet"
WEB3_PROVIDER_URI = "https://polygon-mumbai.infura.io/v3/YOUR_PROJECT_ID"

# IPFS Settings
IPFS_GATEWAY = "https://ipfs.io/ipfs/"
IPFS_API_ENDPOINT = "https://ipfs.infura.io:5001/api/v0"

# Security Settings
JWT_SECRET_KEY = "your-jwt-secret-key-here"
JWT_ACCESS_TOKEN_LIFETIME = "60"
JWT_REFRESH_TOKEN_LIFETIME = "10080"

# External API Keys
GOOGLE_MAPS_API_KEY = ""
STRIPE_PUBLISHABLE_KEY = ""
STRIPE_SECRET_KEY = ""
PAYPAL_CLIENT_ID = ""
PAYPAL_CLIENT_SECRET = ""

