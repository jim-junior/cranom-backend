import jwt
import time
from datetime import timedelta
from django.conf import settings


def get_gh_auth_token():
    t = timedelta(minutes=10)

    keystring = settings.GH_PRIVATE_KEY
    # print(keystring)
    payload = {
        # issued at time, 60 seconds in the past to allow for clock drift
        "iat": int(time.time()) - 60,
        # JWT expiration time (10 minute maximum)
        "exp": int(time.time() + t.total_seconds()),
        # GitHub App's identifier
        "iss": "234648"
    }

    token = jwt.encode(payload, keystring, algorithm='RS256')
    return token
