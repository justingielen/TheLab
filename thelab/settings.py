from pathlib import Path
import os
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env(
    # Set default values and casting
    DEBUG=(bool, False)
)

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# Determine environment
DJANGO_ENV = env('DJANGO_ENV', default='development')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = DJANGO_ENV == 'development'

# Allowed hosts (depending) on environment)
if DJANGO_ENV == 'development':
    ALLOWED_HOSTS = ['127.0.0.1','localhost']
elif DJANGO_ENV == 'staging':
    ALLOWED_HOSTS = ['justingielen.pythonanywhere.com']
else:
    ALLOWED_HOSTS = ['your-production-domain.com']

AUTH_USER_MODEL = 'thelab.User'

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.history.HistoryPanel',
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # all auth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'crispy_forms',
    'crispy_bootstrap5',
    'debug_toolbar',
    'thelab',
    'common', # for dealing with deprecation in django-scheduler
    'page',
    'schedule', # Django-scheduler
    'djangobower', # Django-scheduler
    'events',
    'phonenumber_field'
]

# Authentication backend configuration
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Allauth settings
SITE_ID = 1

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False  # Since we'll generate usernames
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_UNIQUE_EMAIL = True

# Identity Platform Settings
GOOGLE_IDENTITY_PLATFORM = {
    'PROJECT_ID': env('GOOGLE_CLOUD_PROJECT_ID'),
    'API_KEY': env('GOOGLE_MAPS_API_KEY'),
    'AUTH_DOMAIN': env('GOOGLE_AUTH_DOMAIN'),
}

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': env('GOOGLE_CLIENT_ID'),
            'secret': env('GOOGLE_CLIENT_SECRET'),
            'key': ''
        }
    }
}

GOOGLE_REDIRECT_URL = env('GOOGLE_REDIRECT_URI')
LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'login'

PHONENUMBER_DEFAULT_REGION = 'US'

# Google Maps API
GOOGLE_MAPS_API_KEY = env('GOOGLE_MAPS_API_KEY')

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.zoho.com'
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_TIMEOUT = 10  # Timeout in seconds
EMAIL_HOST_USER = env('EMAIL_HOST_USER')  # Defined in .env
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD') 
FROM_EMAIL_JUSTIN = env('FROM_EMAIL_JUSTIN')  # Defined in .env
DEFAULT_FROM_EMAIL=FROM_EMAIL_JUSTIN # I added this line
EMAIL_JUSTIN_PASSWORD = env('EMAIL_JUSTIN_PASSWORD')  # Defined in .env
FROM_EMAIL_ADMIN = env('FROM_EMAIL_ADMIN')  # Defined in .env
EMAIL_ADMIN_PASSWORD = env('EMAIL_ADMIN_PASSWORD')
FROM_EMAIL_SUPPORT=env('FROM_EMAIL_SUPPORT')
EMAIL_SUPPORT_PASSWORD=env('EMAIL_SUPPORT_PASSWORD')

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware', 
]

ROOT_URLCONF = 'thelab.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'thelab','templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # custom context processors
                'thelab.context_processors.user_profile_processor',
            ],
        },
    },
]

INTERNAL_IPS = [
    '127.0.0.1',
]

WSGI_APPLICATION = 'thelab.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'EST'

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'

# Define the directory where collectstatic will copy static files for deployment
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# BOWER IS OFFICIALLY DEPRECATED!!! USE NPM for managing frontend dependencies
# Django-scheduler (from github) section -----------------------
# STATICFILES_FINDERS = [ # this causes static file problems
#     'djangobower.finders.BowerFinder'
# ]
BOWER_COMPONENTS_ROOT = os.path.join(BASE_DIR,'components/')
BOWER_INSTALLED_APPS=(
    'jquery',
    'jquery-ui',
    'bootstrap'
)
# Django-scheduler section -----------------------

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_TEMPLATE_PACK = "bootstrap5"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

STRIPE_PUBLIC_KEY = ''
STRIPE_SECRET_KEY = ''
STRIPE_WEBHOOK_SECRET = ''