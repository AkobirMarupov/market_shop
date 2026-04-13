from pathlib import Path
from datetime import timedelta
from decouple import config
import os
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# .env faylini yuklash
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Endi os.getenv orqali ma'lumotlarni o'qiymiz
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-%j!a*!vl&b@%+-%hmtsgz@zzu!r#=3tks$=4s7(h3xen=i=cmg'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []



AUTH_USER_MODEL = "account.User"


# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'rest_framework_simplejwt.token_blacklist',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]



LOCAL_APPS = [
    'account',
    'common',
    'product',
    'usage',
    'shop_bot'
]

EXTERNAL_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'drf_yasg',
    'jazzmin'
]


INSTALLED_APPS = LOCAL_APPS + EXTERNAL_APPS + DJANGO_APPS



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/


STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Frontend ilova URL manzili (emaildagi tasdiqlash havolasi uchun)
FRONTEND_URL = "https://Marketol.com"



SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization header. Example: Bearer <your_token>',
        },
    },
    'USE_SESSION_AUTH': False,
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}



SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),  
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),  
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}




JAZZMIN_SETTINGS = {
    "site_title": "Market Admin",
    "site_header": "Market",
    "site_brand": "Market Pro",
    "site_logo": "apple.jpg",
    "site_logo_classes": "img-circle elevation-3", 
    "welcome_sign": "Xush kelibsiz!",
    "copyright": "Market Dash � 2026",
    
    "user_avatar": None, 

    "topmenu_links": [
        {"name": "Asosiy", "url": "admin:index", "permissions": ["auth.view_user"], "icon": "fas fa-home"},
        {"name": "Foydalanuvchilar", "model": "users.User", "icon": "fas fa-user-friends"},
        {"name": "Sozlamalar", "url": "/admin/settings/", "icon": "fas fa-cog"},
    ],

    "show_sidebar": True,
    "navigation_expanded": True,
    
    "icons": {
        "auth": "fas fa-shield-alt",
        "users.User": "fas fa-user-gradient", 
        "auth.Group": "fas fa-users-cog",
        "common.BaseModel": "fas fa-database text-warning",
    },
    
    "default_icon_parents": "fas fa-chevron-right",
    "default_icon_children": "fas fa-circle text-info", 

    "changeform_format": "horizontal_tabs",
    "language_chooser": True,

}