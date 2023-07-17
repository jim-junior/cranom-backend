import jwt
import time
from datetime import timedelta
from django.conf import settings
from pathlib import Path
import os
from cryptography.hazmat.backends import default_backend


def get_gh_auth_token():
    t = timedelta(minutes=8)
    paretdir = Path(__file__).resolve().parent
    pemfilelocation = os.path.join(paretdir, "utils/private-key.pem")
    print(pemfilelocation)

    #pemfileContent = settings.GH_PRIVATE_KEY
    pemfile = open(pemfilelocation, "r")
    keystring = pemfile.read().encode()
    private_key = default_backend().load_pem_private_key(keystring, None)

    payload = {
        # issued at time, 60 seconds in the past to allow for clock drift
        "iat": int(time.time()),
        # JWT expiration time (10 minute maximum)
        "exp": int(time.time() + t.total_seconds()),
        # GitHub App's identifier
        "iss": 261133
    }

    token = jwt.encode(payload, private_key, algorithm='RS256')

    return token
