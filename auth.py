import json
from jose import jwt
from urllib.request import urlopen
from functools import wraps
from flask import request

AUTH0_DOMAIN = 'dev-sbac.auth0.com'
API_AUDIENCE = 'sendhug'
ALGORITHMS = ['RS256']

# Authentication Error
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Gets the authorisation header from the request and checks that it's not
# malformed.
def get_auth_header():
    # If there's no auth header, raise an error
    if('Authorization' not in request.headers):
        raise AuthError({
            'code': 401,
            'description': 'Unauthorised. No Authorization header.'
        }, 401)

    # Gets the auth header and splits it
    auth_header = request.headers.get("Authorization")
    split_auth_header = auth_header.split(" ")

    # Checks that there are two parts to the header value and that the first
    # part is 'bearer'
    if((split_auth_header[0].lower() != 'bearer') or (len(split_auth_header) != 2)):
        raise AuthError({
            'code': 401,
            'description': 'Unauthorised. Malformed Authorization header.'
        }, 401)

    return split_auth_header[1]
