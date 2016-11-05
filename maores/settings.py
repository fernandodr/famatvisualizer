"""
Django settings for maores project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*65q63hs*sbnwsg1zb9tjz!#xl3zv^7m^qa7vc$#bq0tt+)(9k'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'famatvisualizer.com',
    'http://django-env.pgt48jkrwg.us-west-2.elasticbeanstalk.com/'
]


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'results',
    'haystack'
)

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
#         'URL': 'http://127.0.0.1:8983/solr'
#         # ...or for multicore...
#         # 'URL': 'http://127.0.0.1:8983/solr/results_search',
#     },
# }


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'maores.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'maores/templates')],
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

WSGI_APPLICATION = 'maores.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases



if True:
    # DATABASES = {
    #     'default': {
    #         'ENGINE': 'django.db.backends.postgresql',
    #         'NAME': os.environ['RDS_DB_NAME'],
    #         'USER': os.environ['RDS_USERNAME'],
    #         'PASSWORD': os.environ['RDS_PASSWORD'],
    #         'HOST': os.environ['RDS_HOSTNAME'],
    #         'PORT': os.environ['RDS_PORT'],
    #     }
    # }
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'famatviz',
            'USER': 'frivera',
            'PASSWORD': 'b-A3GYaO1S',
            'HOST': 'famatviz.cy7xelq2fymc.us-west-2.rds.amazonaws.com:5432',
            'PORT': '5432',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
