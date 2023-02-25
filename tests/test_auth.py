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

import unittest
from unittest.mock import patch

from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError, JOSEError

from auth import verify_jwt, check_permissions, AuthError, get_rsa_key


# Auth testing
class TestHugApp(unittest.TestCase):
    def test_unverified_header_error(self):
        with self.assertRaises(AuthError) as exc:
            get_rsa_key(token="ehjflsahegjls.34839pqhfk.0kfjhsdlugh")

        self.assertIn(
            "Unauthorised. Malformed Authorization header.", str(exc.exception)
        )

    def test_no_permissions(self):
        with self.assertRaises(AuthError) as exc:
            check_permissions(
                permission=["read:user"],
                payload={
                    "sub": "auth0|12345",
                    "aud": [
                        "sendhug",
                    ],
                },
            )

        self.assertIn(
            "Unauthorised. You do not have permission to perform this action.",
            str(exc.exception),
        )

    def test_multiple_permissions_error(self):
        with self.assertRaises(AuthError) as exc:
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

        self.assertIn(
            "Unauthorised. You do not have permission to perform this action.",
            str(exc.exception),
        )

    @patch("auth.get_rsa_key", return_value={"kid": ""})
    @patch("jose.jwt.decode", side_effect=ExpiredSignatureError)
    def test_verify_jwt_expired_signature(self, get_header_mock, verify_mock):
        with self.assertRaises(AuthError) as exc:
            verify_jwt(token="hi")

        self.assertIn("Unauthorised. Your token has expired.", str(exc.exception))

    @patch("auth.get_rsa_key", return_value={"kid": ""})
    @patch("jose.jwt.decode", side_effect=JWTClaimsError)
    def test_verify_jwt_claims_error(self, get_header_mock, verify_mock):
        with self.assertRaises(AuthError) as exc:
            verify_jwt(token="hi")

        self.assertIn(
            "Unauthorised. Your token contains invalid claims.", str(exc.exception)
        )

    @patch("auth.get_rsa_key", return_value={"kid": ""})
    @patch("jose.jwt.decode", side_effect=JWTError)
    def test_verify_jwt_error(self, get_header_mock, verify_mock):
        with self.assertRaises(AuthError) as exc:
            verify_jwt(token="hi")

        self.assertIn("Unauthorised. Your token is invalid.", str(exc.exception))

    @patch("auth.get_rsa_key", return_value={"kid": ""})
    @patch("jose.jwt.decode", side_effect=JOSEError)
    def test_verify_another_error(self, get_header_mock, verify_mock):
        with self.assertRaises(AuthError) as exc:
            verify_jwt(token="hi")

        self.assertIn("Unauthorised. Invalid token.", str(exc.exception))
