# Production settings
import os


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': "wnypdbwz",
        'USER': "wnypdbwz",
        'PASSWORD': "xaE6lWJwxA6zhtIFKT1i-ETj7IVV380D",
        'HOST': "rosie.db.elephantsql.com",
        'PORT': "5432",
    }
}


FLUTTERWAVE_PUBLIC_KEY = os.getenv("FLUTTERWAVE_PUBLIC_KEY")
FLUTTERWAVE_SECRET = os.getenv("FLUTTERWAVE_SECRET")
FLUTTERWAVE_ENDPOINT = "https://api.flutterwave.com/v3"
FLUTTERWAVE_HASH = os.getenv("FLUTTERWAVE_HASH")
FLUTTERWAVE_ENCRYPTION_KEY = os.getenv("FLUTTERWAVE_ENCRYPTION_KEY")

GITHUB_SECRET_HASH = os.getenv("GITHUB_SECRET_HASH")

# Kpack settings
KPACK_URL = "https://kpack.io"
KPACK_DOCKER_REGISTRY = "jimjuniorb/"


# PLatform settings
APP_DEPLOYMENTS_DOMAIN = "cranomapp.ml"


ANYMAIL = {
    # (exact settings here depend on your ESP...)
    "MAILGUN_API_KEY": os.getenv("MAILGUN_API_KEY"),
    "MAILGUN_SENDER_DOMAIN": os.getenv("MAILGUN_SENDER_DOMAIN"),
}

# if you don't already have this in settings
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")
# ditto (default from-email for Django errors)
SERVER_EMAIL = os.getenv("SERVER_EMAIL")

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": ["redis://:99fed4stqjcTSLEKsUOjI2hJsU0TKX0o@redis-19117.c12.us-east-1-4.ec2.cloud.redislabs.com:19117/0"],
        },
    },
}


GITHUB_CLIENT_SECRET = "e30dc34163cd902899338dd706b5edbd45a02de3"

GH_PRIVATE_KEY = os.getenv("GH_PRIVATE_KEY")
