from .base import *

# Dev-specific: DEBUG always True, console email stays
DEBUG = True
ALLOWED_HOSTS = ["*", "localhost", "127.0.0.1"]

# Dev media/static (local files)
MEDIA_URL = "/media/"
