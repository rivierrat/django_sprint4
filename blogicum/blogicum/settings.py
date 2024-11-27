from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Здесь нет подстановки; вхождение '%s' здесь -- не заполнитель, а случайное
# соседство символов. Строка генерируется кодом
# "".join(secrets.choice(allowed_chars) for i in range(length)),
# где allowed_chars == 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)':
SECRET_KEY = 'django-insecure-xxf282q_3xb688t6t93ksl5!cej9yoaca_d!0a+8%sgf=jjhz#'

DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'blog.apps.BlogConfig',
    'pages.apps.PagesConfig',
    'django_bootstrap5'
]

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'blogicum.urls'

TEMPLATES_DIR = BASE_DIR / 'templates'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
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

WSGI_APPLICATION = 'blogicum.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Samara'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'blog:index'

MEDIA_ROOT = BASE_DIR / 'media'

CSRF_FAILURE_VIEW = 'pages.views.csrf_failure'
