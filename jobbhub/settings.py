from pathlib import Path
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS',["*"], default='localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'honeypot',          # form honeypot fields
    'admin_honeypot',    # fake /admin/ login trap
    'accounts',
    'jobs',
    'applications',
    'subscriptions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',        # ← CSRF validates first
    'honeypot.middleware.HoneypotMiddleware',            # ← honeypot checks after
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'jobbhub.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'subscriptions.context_processors.user_subscription',
            ],
        },
    },
]

WSGI_APPLICATION = 'jobbhub.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'accounts.CustomUser'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Kampala'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'uploads'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# File upload limits
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB

# ─── HONEYPOT SETTINGS ─────────────────────────────────────────────────────
# django-honeypot: hidden field name. Use something that looks real to fool bots.
HONEYPOT_FIELD_NAME = 'phonenumber'
# Must be empty — any bot that fills it in gets blocked.
HONEYPOT_VALUE = ''
# ── PAYMENT GATEWAYS ───────────────────────────────────────────────────────

# Stripe
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY', default='pk_test_placeholder')
STRIPE_SECRET_KEY      = config('STRIPE_SECRET_KEY',      default='sk_test_placeholder')
STRIPE_WEBHOOK_SECRET  = config('STRIPE_WEBHOOK_SECRET',  default='whsec_placeholder')

# MTN Mobile Money
MTN_MOMO_BASE_URL         = config('MTN_MOMO_BASE_URL',         default='https://sandbox.momodeveloper.mtn.com')
MTN_MOMO_SUBSCRIPTION_KEY = config('MTN_MOMO_SUBSCRIPTION_KEY', default='')
MTN_MOMO_API_USER         = config('MTN_MOMO_API_USER',         default='')
MTN_MOMO_API_KEY          = config('MTN_MOMO_API_KEY',          default='')
MTN_MOMO_ENVIRONMENT      = config('MTN_MOMO_ENVIRONMENT',      default='sandbox')
MTN_MOMO_CURRENCY         = config('MTN_MOMO_CURRENCY',         default='UGX')
MTN_MOMO_CALLBACK_URL     = config('MTN_MOMO_CALLBACK_URL',     default='http://localhost:8000/subscriptions/mtn/callback/')

# Airtel Money
AIRTEL_BASE_URL       = config('AIRTEL_BASE_URL',       default='https://openapiuat.airtel.africa')
AIRTEL_CLIENT_ID      = config('AIRTEL_CLIENT_ID',      default='')
AIRTEL_CLIENT_SECRET  = config('AIRTEL_CLIENT_SECRET',  default='')
AIRTEL_ENVIRONMENT    = config('AIRTEL_ENVIRONMENT',    default='sandbox')
AIRTEL_CURRENCY       = config('AIRTEL_CURRENCY',       default='UGX')
AIRTEL_CALLBACK_URL   = config('AIRTEL_CALLBACK_URL',   default='http://localhost:8000/subscriptions/airtel/callback/')
