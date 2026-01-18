import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings.development")

from .base import *

if "production" in os.getenv("DJANGO_SETTINGS_MODULE", ""):
    from .production import *
else:
    from .development import *
