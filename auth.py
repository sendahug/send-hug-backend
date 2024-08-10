# MIT License
#
# Copyright (c) 2020-2024 Send A Hug
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

from typing import Any, cast, TypedDict
from datetime import datetime

from functools import wraps
from quart import request
from sqlalchemy import select
from firebase_admin import App  # type: ignore
from firebase_admin.auth import (  # type: ignore
    verify_id_token,
    InvalidIdTokenError,
    ExpiredIdTokenError,
    RevokedIdTokenError,
)

from models import SendADatabase
from config import SAHConfig
from models.schemas.users import User


class RoleData(TypedDict):
    id: int
    name: str
    permissions: list[str]


class UserData(TypedDict):
    id: int
    displayName: str
    role: RoleData
    blocked: bool
    releaseDate: datetime | None
    pushEnabled: bool
    last_notifications_read: datetime | None
    firebaseId: str


# Authentication Error
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_auth_header() -> str:
    """
    Gets the request's 'Authorization' header. Checks to see whether said header
    exists; whether the header is comprised of two parts; and whether the
    first part is 'bearer'. This serves as preliminary verification that
    the JWT is in the correct form.

    returns: The JSON web token.
    """
    # If there's no auth header, raise an error
    if "Authorization" not in request.headers:
        raise AuthError(
            {"code": 401, "description": "Unauthorised. No Authorization header."}, 401
        )

    # Gets the auth header and splits it
    auth_header: str = cast(str, request.headers.get("Authorization"))
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


def validate_token(token: str, app: App):
    """
    Validates the token and returns the decoded payload.
    """
    try:
        token_payload = verify_id_token(token, app)
    except ExpiredIdTokenError:
        raise AuthError(
            {"code": 401, "description": "Unauthorised. Your token has expired."}, 401
        )
    except RevokedIdTokenError:
        raise AuthError(
            {"code": 401, "description": "Unauthorised. Your token has been revoked."},
            401,
        )
    except InvalidIdTokenError:
        raise AuthError(
            {"code": 401, "description": "Unauthorised. Your token is invalid."}, 401
        )
    except Exception as err:
        raise AuthError(
            {
                "code": 401,
                "description": f"Unauthorised. Your token is invalid. Error: {err}",
            },
            401,
        )

    return token_payload


async def get_current_user(
    payload: dict[str, Any], db: SendADatabase
) -> dict[str, Any]:
    """
    Fetches the details of the currently logged in user from the database.

    param payload: The payload from the decoded, verified JWT.
    """
    current_user: User | None = await db.session.scalar(
        select(User).filter(User.firebase_id == payload["uid"])
    )

    # If the user is not found, raise an AuthError
    if current_user is None:
        raise AuthError(
            {
                "code": 401,
                "description": "Unauthorised. User not found.",
            },
            401,
        )

    return current_user.format()


def check_user_permissions(permission: list[str], current_user: dict[str, Any]) -> bool:
    """
    Checks the user's permissions against the required permissions for a given
    resource. If the user doesn't have the required permissions, an AuthError
    is raised.

    param permission: The resource's required permissions.
    param current_user: The details of the currently logged in user from the database.
    """
    if (
        len(permission) == 2
        and permission[0] not in current_user["role"]["permissions"]
        and permission[1] not in current_user["role"]["permissions"]
    ) or (
        len(permission) == 1
        and permission[0] not in current_user["role"]["permissions"]
    ):
        raise AuthError(
            {
                "code": 403,
                "description": "Unauthorised. You do not have permission "
                "to perform this action.",
            },
            403,
        )

    return True


# TODO: Ideally we shouldn't pass the DB in, but right now because the
# whole app initialisation happens within a function, we kind of have to...
def requires_auth(config: SAHConfig, permission=[""]):
    """
    @requires_auth() Decorator Definition
    Gets the Authorization header, verifies the JWT and checks
    the user has the required permissions using the functions above.

    param config: The app config to use (which provides access to the firebase
                  app and the db instance).
    param permission: The resource's required permission(s).
    """

    def requires_auth_decorator(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            token = get_auth_header()
            payload = validate_token(token, config.firebase_app)

            # To create a new user, we just need to check for a valid
            # firebase user.
            if permission[0] == "post:user":
                returned_payload = payload
            else:
                current_user = await get_current_user(payload, config.db)
                returned_payload = {
                    "id": current_user["id"],
                    "displayName": current_user["displayName"],
                    "role": current_user["role"],
                    "blocked": current_user["blocked"],
                    "releaseDate": current_user["releaseDate"],
                    "pushEnabled": current_user["pushEnabled"],
                    "last_notifications_read": current_user["last_notifications_read"],
                    "firebaseId": current_user["firebaseId"],
                }
                check_user_permissions(permission, current_user)

            return await f(returned_payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator
