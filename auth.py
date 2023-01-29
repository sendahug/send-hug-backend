# MIT License
#
# Copyright (c) 2020-2023 Send A Hug
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# The provided Software is separate from the idea behind its website. The Send A Hug
# website and its underlying design and ideas are owned by Send A Hug group and
# may not be sold, sub-licensed or distributed in any way. The Software itself may
# be adapted for any purpose and used freely under the given conditions.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import os
from jose import jwt
from urllib.request import urlopen
import http.client
from functools import wraps
from flask import request

# Auth0 Configuration
AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
API_AUDIENCE = os.environ.get("API_AUDIENCE")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
ALGORITHMS = ["RS256"]


# Authentication Error
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Function: get_auth_header
# Description: Gets the request's 'Authorization' header. Checks to see whether
#              said header exists; whether the header is comprised of two
#              parts; and whether the first part is 'bearer'. This serves as
#              preliminary verification that the JWT is in the correct form.
# Parameters: None
# Returns: split_auth_header[1] - The JSON web token.
def get_auth_header():
    # If there's no auth header, raise an error
    if "Authorization" not in request.headers:
        raise AuthError(
            {"code": 401, "description": "Unauthorised. No Authorization header."}, 401
        )

    # Gets the auth header and splits it
    auth_header = request.headers.get("Authorization")
    split_auth_header = auth_header.split(" ")

    # Checks that there are two parts to the header value and that the first
    # part is 'bearer'
    if (split_auth_header[0].lower() != "bearer") or (len(split_auth_header) != 2):
        raise AuthError(
            {
                "code": 401,
                "description": "Unauthorised. Malformed Authorization header.",
            },
            401,
        )

    return split_auth_header[1]


# Function: verify_jwt
# Description: Gets the token and attempts to decode and verify it using the
#              Auth0 JWKS (JSON Web Key Set) JSON. Ensures that the JWT is
#              authentic, still valid and hasn't been tampered with.
# Parameters: token - a JSON Web Token.
# Returns: payload - The payload from the decoded token.
def verify_jwt(token):
    # Gets the JWKS from Auth0
    auth_json = urlopen("https://" + AUTH0_DOMAIN + "/.well-known/jwks.json")
    jwks = json.loads(auth_json.read())

    # Tries to get the token header
    try:
        token_header = jwt.get_unverified_header(token)
    # If there's an error, raise an AuthError
    except Exception:
        raise AuthError(
            {
                "code": 401,
                "description": "Unauthorised. Malformed Authorization header.",
            },
            401,
        )

    rsa_key = {}

    # If the 'kid' key doesn't exist in the token header
    for key in jwks["keys"]:
        if key["kid"] == token_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }

    # Try to decode and validate the token
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer="https://" + AUTH0_DOMAIN + "/",
            )
        # If the signature is invalid
        except jwt.JWTError:
            raise AuthError(
                {"code": 401, "description": "Unauthorised. Your token is invalid."},
                401,
            )
        # If the token expired
        except jwt.ExpiredSignatureError:
            raise AuthError(
                {"code": 401, "description": "Unauthorised. Your token has expired."},
                401,
            )
        # If any claim in the token is invalid
        except jwt.JWTClaimsError:
            raise AuthError(
                {
                    "code": 401,
                    "description": "Unauthorised. Your token contains invalid claims.",
                },
                401,
            )
        # If there's any other error
        except Exception:
            raise AuthError(
                {"code": 401, "description": "Unauthorised. Invalid token."}, 401
            )

    return payload


# Function: check_permissions
# Description: Checks the payload from of the decoded, verified JWT for
#              permissions. Then compares the user's permissions to the
#              required permission to check whether the user is allowed to
#              access the given resource.
# Parameters: permission (list) - The resource's required permissions. Can
#                                 contain either one or two allowed types
#                                 of permissions.
#             payload - The payload from the decoded, verified JWT.
# Returns: True - Boolean confirming the user has the required permission.
def check_permissions(permission, payload):
    # Check whether permissions are included in the token payload
    if "permissions" not in payload:
        raise AuthError(
            {
                "code": 403,
                "description": "Unauthorised. You do not have permission "
                "to perform this action.",
            },
            403,
        )

    # If there are two possibilities for permissions
    if len(permission) == 2:
        # Check whether the user has that permission
        if (
            permission[0] not in payload["permissions"]
            and permission[1] not in payload["permissions"]
        ):
            raise AuthError(
                {
                    "code": 403,
                    "description": "Unauthorised. You do not have permission "
                    "to perform this action.",
                },
                403,
            )
    # If there's only one possibility
    else:
        # Check whether the user has that permission
        if permission[0] not in payload["permissions"]:
            raise AuthError(
                {
                    "code": 403,
                    "description": "Unauthorised. You do not have permission "
                    "to perform this action.",
                },
                403,
            )

    return True


# @requires_auth() Decorator Definition
# Description: Gets the Authorization header, verifies the JWT and checks
#              the user has the required permissions using the functions above.
# Parameters: permission (list) - The resource's required permission(s).
# Returns: @requires_auth decorator.
def requires_auth(permission=[""]):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_auth_header()
            payload = verify_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator


# Function: check_mgmt_api_token
# Description: Checks that the Management API token is valid and still hasn't
#              expired.
# Parameters: None.
# Returns: Either the verified token's payload (payload) or a 'token expired'
#          message if the token expired.
def check_mgmt_api_token():
    token = os.environ.get("MGMT_API_TOKEN")
    token_header = jwt.get_unverified_header(token)

    # Gets the JWKS from Auth0
    auth_json = urlopen("https://" + AUTH0_DOMAIN + "/.well-known/jwks.json")
    jwks = json.loads(auth_json.read())

    # If the 'kid' key doesn't exist in the token header
    for key in jwks["keys"]:
        if key["kid"] == token_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }

    # Try to decode and validate the token
    if rsa_key:
        try:
            jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer="https://" + AUTH0_DOMAIN + "/",
            )
        # If the token expired
        except jwt.ExpiredSignatureError:
            return "token expired"
        # If there's any other error
        except Exception as e:
            print(e)

    return token


# Function: get_management_api_token
# Description: Gets a new Management API token from Auth0, in order to update
#              users' data in their systems.
# Parameters: None.
# Returns: token - The JWT returned by Auth0.
def get_management_api_token():
    # General variables for establishing an HTTPS connection to Auth0
    connection = http.client.HTTPSConnection(AUTH0_DOMAIN)
    headers = {"content-type": "application/x-www-form-urlencoded"}
    data = (
        "grant_type=client_credentials&client_id="
        + CLIENT_ID
        + "&client_secret="
        + CLIENT_SECRET
        + "&audience=https%3A%2F%2F"
        + AUTH0_DOMAIN
        + "%2Fapi%2Fv2%2F"
    )

    # Then add the 'user' role to the user's payload
    connection.request("POST", "/oauth/token", data, headers)
    response = connection.getresponse()
    response_data = response.read()
    token_data = response_data.decode("utf8").replace("'", '"')
    token = json.loads(token_data)["access_token"]

    os.environ["MGMT_API_TOKEN"] = token
