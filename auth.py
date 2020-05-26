import json
from jose import jwt
from urllib.request import urlopen
from functools import wraps
from flask import request, abort

AUTH0_DOMAIN = 'dev-sbac.auth0.com'
API_AUDIENCE = 'sendhug'
ALGORITHMS = ['RS256']

# Authentication Error
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code
