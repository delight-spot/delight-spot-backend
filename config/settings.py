"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os
import environ
from datetime import timedelta
import dj_database_url
import sentry_sdk


env = environ.Env()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = ['192.168.0.42','10.0.2.2', 'localhost']

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Application definition

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework.authtoken",
    # "corsheaders",
    'rest_framework_simplejwt',
    'drf_yasg',
]

CUSTOM_APPS = [
    "common.apps.CommonConfig",
    "users.apps.UsersConfig",
    "stores.apps.StoresConfig",
    "reviews.apps.ReviewsConfig",
    "bookings.apps.BookingsConfig",
    "userGroup.apps.UsergroupConfig",
    "notice.apps.NoticeConfig",
]

SYSTEM_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

INSTALLED_APPS = CUSTOM_APPS + THIRD_PARTY_APPS + SYSTEM_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",

    "whitenoise.middleware.WhiteNoiseMiddleware",
    # 'django.middleware.security.SecurityMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

if DEBUG:

    DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
    }

else:

    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600)
    }

    # DATABASES = {
    #     'default': {
    #         'ENGINE': 'django.db.backends.mysql',
    #         'NAME': 'delight-spot-db',
    #         'USER': 'jth',
    #         'PASSWORD': 'jth',
    #         'HOST': 'delight-spot-database',  # docker-compose.yml 파일에서 설정한 데이터베이스 서비스 이름
    #         'PORT': '3306',
    #     }
    # }


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

LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

if not DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'



# if not DEBUG:
#     STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
#     STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "users.User"
# USERNAME_FIELD = 'email'  # email을 기본 로그인 필드로 설정

PAGE_SIZE = 10

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        "config.authentication.JWTAuthentication",
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

REST_USE_JWT = True

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2), # access token이 유효한 기간
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7), # refresh token이 유효한 기간
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'TOKEN_USER_CLASS': 'user.User',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
# ]

# CSRF 설정 추가
# Django의 CSRF 보호 기능이 요청의 출처를 신뢰할 수 없다고 판단
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:3000', 
    'http://localhost:3000',
]


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

if not DEBUG:
    sentry_sdk.init(
    dsn="https://203c9333b857d37c32e703024ef63b2a@o4507617701003264.ingest.us.sentry.io/4507617709522944",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)