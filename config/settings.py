"""
Django settings for config project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,.railway.app,.onrender.com').split(',')

# CSRF 설정 (외부 호스팅용)
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in
    os.getenv('CSRF_TRUSTED_ORIGINS', 'https://*.railway.app,https://*.onrender.com').split(',')
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Third party
    'django_htmx',
    # Local apps
    'kiosk',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
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
if os.getenv('DATABASE_URL'):
    # PostgreSQL (Supabase or other)
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
    }
else:
    # SQLite for local development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# 스태프 인증
STAFF_PASSWORD = os.getenv('STAFF_PASSWORD', 'q51!')

# 뿌리오 알림톡 설정
PPURIO_ACCOUNT = os.getenv('PPURIO_ACCOUNT', '')
PPURIO_API_KEY = os.getenv('PPURIO_API_KEY', '')
PPURIO_SENDER = os.getenv('PPURIO_SENDER', '')  # 발신번호
PPURIO_TEMPLATE_CODE = os.getenv('PPURIO_TEMPLATE_CODE', '')  # 알림톡 템플릿 코드

# 이카운트 ERP 연동
ECOUNT_COM_CODE = os.getenv('ECOUNT_COM_CODE', '664058')
ECOUNT_USER_ID = os.getenv('ECOUNT_USER_ID', 'Q51_KIOSK')
ECOUNT_API_KEY = os.getenv('ECOUNT_API_KEY', '3f5e1f37ae87640ef9627b1364d51e0310')
ECOUNT_ZONE = os.getenv('ECOUNT_ZONE', 'AC')
ECOUNT_SITE_CD = os.getenv('ECOUNT_SITE_CD', '510')       # 부서코드 (퀵오일)
ECOUNT_CUST = os.getenv('ECOUNT_CUST', '00013')            # 거래처코드 (토스페이먼츠)
ECOUNT_CR_CODE = os.getenv('ECOUNT_CR_CODE', '4019')       # 매출계정 (상품매출)
ECOUNT_ACCT_NO = os.getenv('ECOUNT_ACCT_NO', '1089')       # 입금계좌 (외상매출금)
# 매입전표 (멤버십 할인)
ECOUNT_PURCHASE_CUST = os.getenv('ECOUNT_PURCHASE_CUST', '00041')   # 거래처 (개인고객)
ECOUNT_PURCHASE_DR_CODE = os.getenv('ECOUNT_PURCHASE_DR_CODE', '8349')  # 매입계정 (판매촉진비)
ECOUNT_PURCHASE_ACCT_NO = os.getenv('ECOUNT_PURCHASE_ACCT_NO', '2519')  # 출금계좌 (외상매입금)
# 멤버십 할인율/한도
MEMBERSHIP_DISCOUNT_RATE = 0.2   # 20%
MEMBERSHIP_DISCOUNT_MAX = 15000  # 최대 15,000원
