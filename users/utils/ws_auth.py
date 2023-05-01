from datetime import timedelta
import hashlib
import time
import jwt
from django.conf.global_settings import SECRET_KEY
from users.models import UserProfile


def encrypt(user: UserProfile):
    t = timedelta(minutes=10)
    exp_time = int(time.time() + t.total_seconds())
    payload = {
        "user": user.user.id,
        "created_at": time.time(),
        "exp": exp_time
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def is_token_valid(token):
    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    user = payload["user"]
    exp = payload["exp"]
    if UserProfile.objects.filter(user=user).exists():
        return True
    return False


def getUser(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = payload["user"]
        if UserProfile.objects.filter(user=user).exists():
            return UserProfile.objects.get(user=user)
        return None
    except:
        return None
