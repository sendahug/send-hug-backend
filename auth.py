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


# Verifies the authenticity of the JWT
def verify_jwt(token):
    # Gets the JWKS from Auth0
    auth_json = urlopen('https://' + AUTH0_DOMAIN + '/.well-known/jwks.json')
    jwks = json.loads(auth_json.read())

    # Gets the token header
    token_header = jwt.get_unverified_header(token)
    rsa_key = {}

    # If the 'kid' key doesn't exist in the token header
    for key in jwks['key']:
        if(key['kid'] == token_header['kid']):
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }

    # Try to decode and validate the token
    if(rsa_key):
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer="https://" + AUTH0_DOMAIN + "/"
            )
        # If the signature is invalid
        except jwt.JWTError:
            raise AuthError({
                'code': 403,
                'description': 'Unauthorised. Your token is invalid.'
            }, 403)
        # If the token expired
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 403,
                'description': 'Unauthorised. Your token has expired.'
            }, 403)
        # If any claim in the token is invalid
        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 403,
                'description': 'Unauthorised. Your token contains invalid claims.'
            }, 403)
        # If there's any other error
        except Exception as e:
            raise AuthError({
                'code': 403,
                'description': 'Unauthorised. Invalid token.'
            }, 403)

    return payload
