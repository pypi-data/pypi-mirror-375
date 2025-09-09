"""
Test settings for django-currency-converter-erapi
"""

SECRET_KEY = 'test-secret-key-for-currency-converter'

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'currency_converter_erapi',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache',
    }
}

USE_TZ = True

# Currency converter settings for testing
CURRENCY_CACHE_TIMEOUT = 60  # Short timeout for tests
CURRENCY_API_KEY = None  # Use free tier for tests

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'currency_converter_erapi': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
