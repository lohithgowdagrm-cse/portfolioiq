"""Base settings for PortfolioIQ."""
import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR points to backend/ directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from workspace root or backend
env_path = BASE_DIR.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "insecure-dev-secret-key-portfolioiq-test")
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0").split(",") if h.strip()]

# Application definition
DJANGO_APPS = [
    "daphne",  # ASGI server must be first
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "channels",
    "drf_spectacular",
]

LOCAL_APPS = [
    "apps.accounts.apps.AccountsConfig",
    "apps.instruments.apps.InstrumentsConfig",
    "apps.portfolios.apps.PortfoliosConfig",
    "apps.transactions.apps.TransactionsConfig",
    "apps.market_data.apps.MarketDataConfig",
    "apps.analytics.apps.AnalyticsConfig",
    "apps.risk.apps.RiskConfig",
    "apps.options.apps.OptionsConfig",
    "apps.alerts.apps.AlertsConfig",
    "apps.audit.apps.AuditConfig",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "common.middleware.audit_middleware.AuditLogMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Custom User Model
AUTH_USER_MODEL = "accounts.User"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework Configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "common.pagination.standard.StandardResultsSetPagination",
    "PAGE_SIZE": 25,
    "EXCEPTION_HANDLER": "common.exceptions.handlers.custom_exception_handler",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%SZ",
}

# SimpleJWT Settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("ACCESS_TOKEN_LIFETIME_MINUTES", "60"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("REFRESH_TOKEN_LIFETIME_DAYS", "7"))),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# OpenAPI / Spectacular settings
SPECTACULAR_SETTINGS = {
    "TITLE": "PortfolioIQ API",
    "DESCRIPTION": "Real-Time Portfolio & Risk Analytics Engine REST API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}

# Celery Configuration
CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "periodic-market-data-ingestion": {
        "task": "apps.market_data.tasks.fetch_market_prices",
        "schedule": 60.0,  # every 60 seconds
    },
    "periodic-risk-alert-evaluation": {
        "task": "apps.alerts.tasks.process_alerts_task",
        "schedule": 120.0,  # every 2 minutes
    },
    "nightly-portfolio-snapshots": {
        "task": "apps.portfolios.tasks.generate_daily_snapshot_task",
        "schedule": crontab(hour=23, minute=55),
    },
    "nightly-risk-analytics": {
        "task": "apps.risk.tasks.calculate_daily_risk_task",
        "schedule": crontab(hour=23, minute=58),
    },
}

# Channels & Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
try:
    import redis
    r = redis.from_url(REDIS_URL)
    r.ping()
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [REDIS_URL],
            },
        },
    }
except Exception:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer"
        }
    }

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    origin.strip() for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    ).split(",") if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True
