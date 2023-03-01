"""
Django settings for lnpayroll project.

Generated by 'django-admin startproject' using Django 4.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
from collections import OrderedDict
from decimal import Decimal
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-uf47t)@e40x&-0*ro-@ti3$t75nb+6s8*(uk1sjtsuh0!ksmec"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django_object_actions",
    "constance",
    "constance.backends.database",
    "admin_interface",
    "colorfield",
    "lnpayroll.app.LnPayrollAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "lnpayroll",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "lnpayroll.urls"

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

WSGI_APPLICATION = "lnpayroll.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "dev/dev.db",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = False


# Cache
CACHES = {
    "default": {
        "BACKEND": "shared_memory_dict.caches.django.SharedMemoryCache",
        "LOCATION": "memory",
        "OPTIONS": {"MEMORY_BLOCK_SIZE": 1024},
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# fixtures
FIXTURE_DIRS = [BASE_DIR / "lnpayroll/fixtures"]


# django-admin-interface
X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]


# django-constance
from django.forms import TextInput

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
CONSTANCE_DATABASE_CACHE_BACKEND = "default"
CONSTANCE_ADDITIONAL_FIELDS = {
    "charfield": [
        "django.forms.fields.CharField",
        {"widget": "django.forms.TextInput", "widget_kwargs": {"attrs": {"size": "10"}}},
    ],
}
CONSTANCE_CONFIG = OrderedDict(
    [
        ("BASE_CURRENCY", ("EUR", "Book keeping currency", "charfield")),
        ("MAX_FEE_MSATS", (100_000, "Maximum transaction fee in millisatoshis", int)),
        ("FX_TIMEOUT", (60, "Number of seconds before updating exchange rate", int)),
        ("TX_TIMEOUT", (30, "Number of seconds for transaction timeout", int)),
    ]
)

# LND
LND_MACAROON_PATH = BASE_DIR / "dev/lnd.mac"
LND_CERT_PATH = BASE_DIR / "dev/lnd.cert"
LND_REST_SERVER = "https://umbrel.local:8080"
