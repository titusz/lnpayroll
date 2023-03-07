import environ
from collections import OrderedDict
from decimal import Decimal
from pathlib import Path
from django.utils.translation import gettext_lazy as _
from django.conf.locale.en import formats as en_formats

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

LND_CERT = env("LND_CERT", default="/lnd/tls.cert")
LND_MACAROON = env("LND_MACAROON", default="/lnd/data/chain/bitcoin/mainnet/admin.macaroon")
LND_REST_URL = env("LND_REST_URL", default="https://umbrel.local:8080")
LNPAYROLL_DATA_DIR = env("LNPAYROL_DATA_DIR", default=BASE_DIR / "data")
LNPAYROLL_DB_URI = env("LNPAYROLL_DB_URI", default=f"sqlite:////{BASE_DIR}/data/lnpayroll.sqlite")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", default="insecure-development-key")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG", default=True)


ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = ["http://umbrel.local", "https://*.ngrok.io"]


# Application definition

INSTALLED_APPS = [
    "import_export",
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
    "whitenoise.middleware.WhiteNoiseMiddleware",
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

DATABASES = {"default": env.db(default=LNPAYROLL_DB_URI)}


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
USE_TZ = True
en_formats.DATETIME_FORMAT = "Y-m-d H:i:s"
en_formats.DATE_FORMAT = "Y-m-d"


# Cache
CACHES = {
    "default": {
        "BACKEND": "shared_memory_dict.caches.django.SharedMemoryCache",
        "LOCATION": "memory",
        "OPTIONS": {"MEMORY_BLOCK_SIZE": 4096},
    }
}


STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# fixtures
FIXTURE_DIRS = [BASE_DIR / "lnpayroll/fixtures"]


# django-admin-interface
X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]


# django-constance
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
        ("PASS_TROUGH_FEE_SATS", (1, "Fee that is always accepted irrespective of PPM")),
        ("MAX_FEE_PPM", (500, "Maximum transaction fee in PPM", int)),
        ("FX_TIMEOUT", (60, "Number of seconds before updating exchange rate", int)),
        ("TX_TIMEOUT", (30, "Number of seconds for transaction timeout", int)),
        ("EXPORT_EXCHANGE_VALUE", ("LND", "Value for `Exchange` export field", str)),
        ("EXPORT_TRADE_GROUP_VALUE", ("", "Value for `Trade-Group` export field", str)),
    ]
)
