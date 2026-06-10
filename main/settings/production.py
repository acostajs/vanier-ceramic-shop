from .base import *
import os

ALLOWED_HOSTS.append(".hf.space")

DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"

# Storage
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Cloudinary
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.getenv("CLOUDINARY_API_KEY"),
    "API_SECRET": os.getenv("CLOUDINARY_SECRET_KEY"),
}

MEDIA_URL = "/media/"

# Security
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if not SECRET_KEY or SECRET_KEY == "django-insecure-fallback-key-for-local-dev-only":
    raise ValueError("DJANGO_SECRET_KEY must be set to a secure value in production!")

if (
    not CLOUDINARY_STORAGE["CLOUD_NAME"]
    or not CLOUDINARY_STORAGE["API_KEY"]
    or not CLOUDINARY_STORAGE["API_SECRET"]
):
    raise ValueError(
        "Cloudinary credentials (CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_SECRET_KEY) must be set in production!"
    )
