from datetime import timedelta
from pathlib import Path

import dj_database_url
from decouple import Csv, config


BASE_DIR = Path(__file__).resolve().parents[2]

SECRET_KEY = config("SECRET_KEY", default="django-insecure-change-me")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "apps.users",
    "apps.notebooks",
    "apps.interactions",
    "apps.documents",
    "apps.chat",
    "apps.core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": dj_database_url.parse(
        config(
            "DATABASE_URL",
            default="postgresql://postgres:postgres123@localhost:5434/pdf_ia_rework_db",
        ),
        conn_max_age=600,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom User Model
# Ver: docs/09_pasos_decisiones.md#fase-2-paso-21 (por qué custom desde Day 1)
AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:5174",
    cast=Csv(),
)
CORS_ALLOW_CREDENTIALS = True

# ═══════════════════════════════════════════════════════════
# Configuración de Groq LLM (Fase 6 Mejora)
# ═══════════════════════════════════════════════════════════

GROQ_CONFIG = {
    "MODEL": config(
        "GROQ_MODEL",
        default="llama-3.1-8b-instant",
        cast=str,
    ),
    "MAX_TOKENS": config(
        "GROQ_MAX_TOKENS",
        default="1024",
        cast=int,
    ),
    "TEMPERATURE": config(
        "GROQ_TEMPERATURE",
        default="0.7",
        cast=float,
    ),
    "API_KEY": config(
        "GROQ_API_KEY",
        default="",
        cast=str,
    ),
}

# Validación de configuración
if not GROQ_CONFIG["API_KEY"] and not DEBUG:
    import warnings
    warnings.warn("GROQ_API_KEY no está configurada en producción")

# ═══════════════════════════════════════════════════════════
# Configuración de Procesamiento de Documentos (Fase 6 Mejora)
# ═══════════════════════════════════════════════════════════

DOCUMENT_CONFIG = {
    # Máximo de caracteres por documento en RAG context
    "MAX_CHARS_PER_DOCUMENT": config(
        "DOCUMENT_MAX_CHARS_PER_DOC",
        default="10000",
        cast=int,
    ),
    # Máximo total de caracteres en contexto RAG
    "MAX_CHARS_TOTAL": config(
        "DOCUMENT_MAX_CHARS_TOTAL",
        default="30000",
        cast=int,
    ),
    # Usar búsqueda semántica para seleccionar fragmentos relevantes
    "ENABLE_SEMANTIC_SEARCH": config(
        "DOCUMENT_ENABLE_SEMANTIC_SEARCH",
        default="True",
        cast=bool,
    ),
    # Tamaño de chunks para chunking inteligente
    "CHUNK_SIZE": config(
        "DOCUMENT_CHUNK_SIZE",
        default="2000",
        cast=int,
    ),
    # Overlap entre chunks para contexto
    "CHUNK_OVERLAP": config(
        "DOCUMENT_CHUNK_OVERLAP",
        default="200",
        cast=int,
    ),
}

# ═══════════════════════════════════════════════════════════
# Configuración de Embeddings (Fase 2 - Búsqueda Semántica)
# ═══════════════════════════════════════════════════════════

EMBEDDING_CONFIG = {
    "DIMENSIONS": 384,
    "MODEL": config(
        "EMBEDDING_MODEL",
        default="tfidf-svd",
        cast=str,
    ),
    "CHUNK_SIZE": config(
        "EMBEDDING_CHUNK_SIZE",
        default="2000",
        cast=int,
    ),
    "CHUNK_OVERLAP": config(
        "EMBEDDING_CHUNK_OVERLAP",
        default="200",
        cast=int,
    ),
    "TOP_K": config(
        "EMBEDDING_TOP_K",
        default="10",
        cast=int,
    ),
}
