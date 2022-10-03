from datetime import timedelta
import hashlib
import time
import jwt
from django.conf.global_settings import SECRET_KEY


def encrypt(username, id):
    token = jwt.encode({'username': username,
                       'id': id}, SECRET_KEY, algorithm='HS256')
    return token


def decrypt(token):
    try:
        token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return {'username': token['username'], 'id': token['id']}
    except:
        return {'username': None, 'id': None}
