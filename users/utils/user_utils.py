import datetime
import hashlib
import time
import jwt
from django.conf.global_settings import SECRET_KEY

# To encrypting functions that encrypt a username, email and current time. The encrypting function is used to encrypt the username, email and current time and returns a token. The decrypting function is used to decrypt the token and returns the username, email and current time.


def encrypt(username, email):
    token = jwt.encode({'username': username, 'email': email,
                       'time': time.time()}, SECRET_KEY, algorithm='HS256')
    return token.decode('utf-8')


def decrypt(token):
    token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    return {'username': token['username'], 'email': token['email'], 'time': token['time']}
