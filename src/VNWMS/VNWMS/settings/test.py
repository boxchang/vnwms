# VNWMS/settings/test.py

from .base import *

SECRET_KEY = '+e9tzio&ivf94+ek0$_9l8op)gxc4r+t9pen@dov0j7c4zks%r'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'VNWMS_Test',
        'USER': 'vnwms',
        'PASSWORD': 'vnwms#2025',
        'HOST': '10.13.104.181',
        'PORT': '1433',

        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'SGADA': {
        'ENGINE': 'mssql',
        'NAME': 'PMG_DEVICE',
        'USER': 'scadauser',
        'PASSWORD': 'pmgscada+123',
        'HOST': '10.13.104.181',
        'PORT': '1433',

        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'SAP': {
        'ENGINE': 'mssql',
        'NAME': 'PMG_DEVICE',
        'USER': 'sa',
        'PASSWORD': '!QAw3ed',
        'HOST': '10.13.102.22',
        'PORT': '1433',

        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'MES': {
        'ENGINE': 'mssql',
        'NAME': 'PMGMES',
        'USER': 'scadauser',
        'PASSWORD': 'pmgscada+123',
        'HOST': '10.13.102.22',
        'PORT': '1433',

        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
    'VNWMS': {
        'ENGINE': 'mssql',
        'NAME': 'VNWMS_Test',
        'USER': 'vnwms',
        'PASSWORD': 'vnwms#2025',
        'HOST': '10.13.104.181',
        'PORT': '1433',

        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    },
}