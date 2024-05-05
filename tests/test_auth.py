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

import pytest
from firebase_admin.auth import (  # type: ignore
    InvalidIdTokenError,
    ExpiredIdTokenError,
    RevokedIdTokenError,
    TokenSignError,
)

from auth import (
    AuthError,
    get_current_user,
    check_user_permissions,
    validate_token,
)
from models import SendADatabase
from config import SAHConfig


# Auth testing
@pytest.mark.parametrize(
    "error, error_message",
    [
        (
            ExpiredIdTokenError("error", "error"),
            "Unauthorised. Your token has expired.",
        ),
        (RevokedIdTokenError("error"), "Unauthorised. Your token has been revoked."),
        (InvalidIdTokenError("error", "error"), "Unauthorised. Your token is invalid."),
        (TokenSignError, "Unauthorised. Your token is invalid. Error: "),
    ],
)
def test_verify_jwt_error(mocker, error, error_message, test_config: SAHConfig):
    mocker.patch("auth.verify_id_token", side_effect=error)

    with pytest.raises(AuthError) as exc:
        validate_token(token="hi", app=test_config.firebase_app)

    assert error_message in str(exc.value)


@pytest.mark.asyncio(scope="session")
async def test_get_current_user_error(test_db: SendADatabase):
    with pytest.raises(AuthError) as exc:
        await get_current_user(
            {
                "uid": "auth0|12345",
            },
            test_db,
        )

    assert "Unauthorised. User not found." in str(exc.value)


@pytest.mark.asyncio(scope="session")
async def test_get_current_user(dummy_users_data, test_db: SendADatabase):
    user = await get_current_user(
        {"uid": dummy_users_data["user"]["firebase_id"]}, test_db
    )

    assert user["id"] == int(dummy_users_data["user"]["internal"])


def test_check_user_permissions_one_perm():
    res = check_user_permissions(
        ["read:user"],
        {
            "id": 1,
            "role": {
                "name": "user",
                "permissions": ["read:user", "read:post", "patch:post"],
            },
        },
    )
    assert res is True


def test_check_user_permissions_two_perms():
    res = check_user_permissions(
        ["read:user", "read:all-users"],
        {
            "id": 1,
            "role": {
                "name": "user",
                "permissions": ["read:user", "read:post", "patch:post"],
            },
        },
    )
    assert res is True


@pytest.mark.parametrize(
    "required_perms, user_perms",
    [
        (["read:user"], ["read:post", "patch:post"]),
        (["read:user", "read:all-users"], ["read:post", "patch:post"]),
    ],
)
def test_check_user_permissions_error(required_perms, user_perms):
    with pytest.raises(AuthError) as exc:
        check_user_permissions(
            required_perms,
            {"id": 1, "role": {"name": "user", "permissions": user_perms}},
        )

    assert "Unauthorised. You do not have permission to perform this action." in str(
        exc.value
    )
