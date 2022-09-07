from datetime import timedelta
import hashlib
import time
import jwt
from django.conf.global_settings import SECRET_KEY

# To encrypting functions that encrypt a username, email and current time. The encrypting function is used to encrypt the username, email and current time and returns a token. The decrypting function is used to decrypt the token and returns the username, email and current time.


def encrypt(username, email):
    token = jwt.encode({'username': username, 'email': email,
                       'time': time.time()}, SECRET_KEY, algorithm='HS256')
    return token


def decrypt(token):
    try:
        token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return {'username': token['username'], 'email': token['email'], 'time': token['time']}
    except:
        return {'username': None, 'email': None, 'time': None}


def get_cli_token(username, exp, client):
    exp_time = ""
    if exp == "hour":
        t = timedelta(minutes=60)
        exp_time = int(time.time() + t.total_seconds())
    elif exp == "day":
        t = timedelta(days=1)
        exp_time = int(time.time() + t.total_seconds())
    elif exp == "week":
        t = timedelta(days=7)
        exp_time = int(time.time() + t.total_seconds())
    elif exp == "month":
        t = timedelta(days=30)
        exp_time = int(time.time() + t.total_seconds())
    elif exp == "3month":
        t = timedelta(days=90)
        exp_time = int(time.time() + t.total_seconds())
    elif exp == "year":
        t = timedelta(days=365)
        exp_time = int(time.time() + t.total_seconds())
    token = jwt.encode({'username': username, 'client': client, "exp": exp_time,
                       'time': time.time()}, SECRET_KEY, algorithm='HS256')
    return token


def decode_cli_token(token):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return {'username': data['username'], 'exp': data['exp'], 'time': data['time']}
    except:
        return "Failed"
