from .base import *  # noqa: F403,F401


DEBUG = True
ALLOWED_HOSTS = ["*"]

REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = (  # noqa: F405
    "rest_framework.permissions.AllowAny",
)
