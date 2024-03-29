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

from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError, JOSEError
import pytest

from auth import verify_jwt, check_permissions, AuthError, get_rsa_key


# Auth testing
def test_unverified_header_error():
    with pytest.raises(AuthError) as exc:
        get_rsa_key(token="ehjflsahegjls.34839pqhfk.0kfjhsdlugh")

    assert "Unauthorised. Malformed Authorization header." in str(exc.value)


def test_no_permissions():
    with pytest.raises(AuthError) as exc:
        check_permissions(
            permission=["read:user"],
            payload={
                "sub": "auth0|12345",
                "aud": [
                    "sendhug",
                ],
            },
        )

    assert "Unauthorised. You do not have permission to perform this action." in str(
        exc.value
    )


def test_multiple_permissions_error():
    with pytest.raises(AuthError) as exc:
        check_permissions(
            permission=["read:user", "write:user"],
            payload={
                "sub": "auth0|12345",
                "aud": [
                    "sendhug",
                ],
                "permissions": ["do:stuff", "read:stuff"],
            },
        )

    assert "Unauthorised. You do not have permission to perform this action." in str(
        exc.value
    )


@pytest.mark.parametrize(
    "error, error_message",
    [
        (ExpiredSignatureError, "Unauthorised. Your token has expired."),
        (JWTClaimsError, "Unauthorised. Your token contains invalid claims."),
        (JWTError, "Unauthorised. Your token is invalid."),
        (JOSEError, "Unauthorised. Invalid token."),
    ],
)
def test_verify_jwt_error(mocker, error, error_message):
    mocker.patch("auth.get_rsa_key", return_value={"kid": ""})
    mocker.patch("jose.jwt.decode", side_effect=error)

    with pytest.raises(AuthError) as exc:
        verify_jwt(token="hi")

    assert error_message in str(exc.value)
