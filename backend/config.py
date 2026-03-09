import os

SECRET_KEY = os.environ.get("SECRET_KEY", "market-house-super-secret-key-2024")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-market-house-secret-key-2024")
JWT_ACCESS_TOKEN_EXPIRES_HOURS = 24
DEBUG = True
