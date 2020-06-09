import json
from jose import jwt
from urllib.request import urlopen
from functools import wraps
from flask import request

# Auth0 Configuration
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
    if((split_auth_header[0].lower() != 'bearer') or
       (len(split_auth_header) != 2)):
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

    # Tries to get the token header
    try:
        token_header = jwt.get_unverified_header(token)
    # If there's an error, raise an AuthError
    except Exception as e:
        raise AuthError({
            'code': 401,
            'description': 'Unauthorised. Malformed Authorization header.'
        }, 401)

    rsa_key = {}

    # If the 'kid' key doesn't exist in the token header
    for key in jwks['keys']:
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
                'code': 401,
                'description': 'Unauthorised. Your token is invalid.'
            }, 401)
        # If the token expired
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 401,
                'description': 'Unauthorised. Your token has expired.'
            }, 401)
        # If any claim in the token is invalid
        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 401,
                'description': 'Unauthorised. Your token contains invalid \
                                claims.'
            }, 401)
        # If there's any other error
        except Exception as e:
            raise AuthError({
                'code': 401,
                'description': 'Unauthorised. Invalid token.'
            }, 401)

    return payload


#  Checks the user has permission to access an endpoint
def check_permissions(permission, payload):
    # Check whether permissions are included in the token payload
    if('permissions' not in payload):
        raise AuthError({
            'code': 403,
            'description': 'Unauthorised. You do not have permission to \
                            perform this action.'
        }, 403)

    # If there are two possibilities for permissions
    if(len(permission) == 2):
        # Check whether the user has that permission
        if(permission[0] not in payload['permissions'] and
           permission[1] not in payload['permissions']):
            raise AuthError({
                'code': 403,
                'description': 'Unauthorised. You do not have permission to \
                                perform this action.'
            }, 403)
    # If there's only one possibility
    else:
        # Check whether the user has that permission
        if(permission[0] not in payload['permissions']):
            raise AuthError({
                'code': 403,
                'description': 'Unauthorised. You do not have permission to \
                                perform this action.'
            }, 403)

    return True


# requires_auth decorator
def requires_auth(permission=['']):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_auth_header()
            payload = verify_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
