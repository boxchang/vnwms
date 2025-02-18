"""
Django settings for VNWMS project.

Generated by 'django-admin startproject' using Django 2.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from django.contrib.messages import constants as messages
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.urls import reverse_lazy

# 因設定檔移入下一層，所以需修改BASE_DIR
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'ezah+g6e0w@mekz2bs_fqk_*&lgcn$g_*39%%vus5_y6kka7(x'
#
# # SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
#
ALLOWED_HOSTS = ['*']
#ALLOWED_HOSTS = ['localhost', '0.0.0.0:8000']

# Application definition

INSTALLED_APPS = [
    'warehouse',
    'users',
    'bases',
    'crispy_forms',
    'ckeditor',
    'ckeditor_uploader',
    'bootstrap_datepicker_plus',
    'rest_framework',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

CKEDITOR_BASEPATH = "/static/ckeditor/ckeditor/"
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = 'pillow'

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'VNWMS.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'warehouse.context_processors.warehouse_items',
            ],
        },
    },
]

WSGI_APPLICATION = 'VNWMS.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
#
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'zh-hant'

TIME_ZONE = 'Asia/Taipei'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')

STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

MEDIA_URL = '/media/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static"), ]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_UPLOAD_SLUGIFY_FILENAME = False

#GLOBAL_SETTINGS = {'STATUS_LIST': {'WAIT': 1, 'ON-GOING': 2}, 'FORM_TYPE': {'PROJECT': 1, 'REQUEST': 2}}

#LOGIN_REDIRECT_URL = reverse_lazy('manage')

AUTH_USER_MODEL = 'users.CustomUser'

AUTHENTICATION_BACKENDS = ['users.backends.EmpNoBackend']

# TIME= 240*60  #four hours  or your time
TIME = 10*60*60  # 20 mins
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = TIME  # change expired session
SESSION_IDLE_TIMEOUT = TIME  # logout

LOGIN_URL = '/users/login/'

DEFAULT_STATUS = 'Wait'


CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl',
                       'Language']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert',
             'items': ['Flash', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak', 'Iframe']},
            '/',
            {'name': 'styles', 'items': [
                'Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['Maximize', 'ShowBlocks']},
            {'name': 'about', 'items': ['About']},
            {'name': 'yourcustomtools', 'items': [
                'CodeSnippet',
                'Youtube',
                'Image',
            ]},
        ],
        'width': '100%',
        'height': 300,
        'toolbarCanCollapse': False,
        'removePlugins': 'stylesheetparser',
        'extraPlugins': ','.join(['codesnippet', 'youtube']),
    },
    'special': {
        'toolbar': 'Special',
        'toolbar_Special': [
            ['Bold', 'CodeSnippet', 'ImageButton', ]
        ],
        'width': '100%',
        'height': 300,
        'extraPlugins': ','.join(['codesnippet', 'youtube']),
    }
}


MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

LANGUAGES = [
    ('en', 'English'),
    ('zh-hant', '繁體中文'),
    ('zh-hans', '简体中文'),
    ('vi', 'Tiếng Việt'),

]

LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]

FILE_LIST_DIRECTORY = 'Z:\\'

