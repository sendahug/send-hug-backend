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

from utils.push_notifications import (
    generate_push_data,
    generate_vapid_claims,
    RawPushData,
)
from utils.validator import Validator, ValidationError


# App testing
class TestHugApp(unittest.TestCase):
    # Setting up the suite
    @classmethod
    def setUpClass(cls):
        cls.validator = Validator(
            {
                "post": {"max": 480, "min": 1},
                "message": {"max": 480, "min": 1},
                "user": {"max": 60, "min": 1},
                "report": {"max": 120, "min": 1},
            }
        )

    # Push notification tests
    # =====================================================
    def test_generate_push_data(self):
        base_data: RawPushData = {"type": "hug", "text": "Meow"}
        push_data = generate_push_data(base_data)

        self.assertEqual(push_data["title"], "New hug")
        self.assertEqual(push_data["body"], "Meow")

    def test_generate_vapid_claims(self):
        vapid_claims = generate_vapid_claims()

        # TODO: Add check for the expiry time
        self.assertEqual(vapid_claims["sub"], "mailto:sendahugcom@gmail.com")

    # Validator tests
    # =====================================================
    # TODO: These tests are really better done with parameterization...
    # but this requires switching to pytest, which is fine but a project in itself
    def test_validator_too_long_post(self):
        too_long_post = "xy" * 450

        with self.assertRaises(ValidationError) as exc:
            self.validator.check_length(data=too_long_post, obj_type="Post")

        self.assertIn(
            "Your Post is too long! Please shorten it and then try again.",
            str(exc.exception),
        )

    def test_validator_too_short_post(self):
        too_short_post = ""

        with self.assertRaises(ValidationError) as exc:
            self.validator.check_length(data=too_short_post, obj_type="Post")

        self.assertIn(
            "Your Post cannot be empty. Please write something and then try again.",
            str(exc.exception),
        )

    def test_validator_too_long_name(self):
        too_long_name = "xy" * 450

        with self.assertRaises(ValidationError) as exc:
            self.validator.check_length(data=too_long_name, obj_type="Display name")

        self.assertIn(
            "Your new display name is too long! Please shorten it and then try again.",
            str(exc.exception),
        )

    def test_validator_too_short_name(self):
        too_short_name = ""

        with self.assertRaises(ValidationError) as exc:
            self.validator.check_length(data=too_short_name, obj_type="Display name")

        self.assertIn(
            "Your display name cannot be empty. "
            "Please write something and then try again.",
            str(exc.exception),
        )

    def test_validator_too_long_report_reason(self):
        too_long_report_reason = "xy" * 450

        with self.assertRaises(ValidationError) as exc:
            self.validator.check_length(data=too_long_report_reason, obj_type="report")

        self.assertIn(
            "Your report reason is too long! Please shorten it and then try again.",
            str(exc.exception),
        )

    def test_validator_too_short_report_reason(self):
        too_short_report_reason = ""

        with self.assertRaises(ValidationError) as exc:
            self.validator.check_length(data=too_short_report_reason, obj_type="report")

        self.assertIn(
            "You cannot send a report without a reason. "
            "Please write something and try to send it again.",
            str(exc.exception),
        )

    def test_too_short(self):
        too_short_text = ""

        with self.assertRaises(ValidationError) as exc:
            self.validator.check_length(data=too_short_text, obj_type="anything")

        self.assertIn(
            "anything cannot be empty. Please write something and try again.",
            str(exc.exception),
        )

    def test_just_right(self):
        post = "hi"
        res = self.validator.check_length(data=post, obj_type="Post")
        self.assertTrue(res)

    def test_correct_string_type_post(self):
        text = "hello"
        res = self.validator.check_type(data=text, obj_type="post text")
        self.assertTrue(res)

    def test_incorrect_type_post(self):
        text = 3

        with self.assertRaises(ValidationError) as exc:
            self.validator.check_type(data=text, obj_type="post text")

        self.assertIn(
            "post text must be of type 'String'. "
            "Please correct the error and try again.",
            str(exc.exception),
        )

    def test_correct_string_type_message(self):
        text = "hello"
        res = self.validator.check_type(data=text, obj_type="message text")
        self.assertTrue(res)

    def test_incorrect_type_message(self):
        text = 3

        with self.assertRaises(ValidationError) as exc:
            self.validator.check_type(data=text, obj_type="message text")

        self.assertIn(
            "message text must be of type 'String'. "
            "Please correct the error and try again.",
            str(exc.exception),
        )

    def test_correct_string_type_name(self):
        text = "hello"
        res = self.validator.check_type(data=text, obj_type="display name")
        self.assertTrue(res)

    def test_incorrect_type_name(self):
        text = 3

        with self.assertRaises(ValidationError) as exc:
            self.validator.check_type(data=text, obj_type="display name")

        self.assertIn(
            "display name must be of type 'String'. "
            "Please correct the error and try again.",
            str(exc.exception),
        )

    def test_correct_string_type_report(self):
        text = "hello"
        res = self.validator.check_type(data=text, obj_type="report reason")
        self.assertTrue(res)

    def test_incorrect_type_report(self):
        text = 3

        with self.assertRaises(ValidationError) as exc:
            self.validator.check_type(data=text, obj_type="report reason")

        self.assertIn(
            "report reason must be of type 'String'. "
            "Please correct the error and try again.",
            str(exc.exception),
        )

    def test_correct_string_type_search(self):
        text = "hello"
        res = self.validator.check_type(data=text, obj_type="search query")
        self.assertTrue(res)

    def test_incorrect_type_search(self):
        text = 3

        with self.assertRaises(ValidationError) as exc:
            self.validator.check_type(data=text, obj_type="search query")

        self.assertIn(
            "search query must be of type 'String'. "
            "Please correct the error and try again.",
            str(exc.exception),
        )

    def test_correct_number_type_id(self):
        obj_id = 3
        res = self.validator.check_type(data=obj_id, obj_type="user ID")
        self.assertTrue(res)

    def test_incorrect_type_id(self):
        obj_id = "h"

        with self.assertRaises(ValidationError) as exc:
            self.validator.check_type(data=obj_id, obj_type="user ID")

        self.assertIn(
            "user ID must be of type 'Integer'. "
            "Please correct the error and try again.",
            str(exc.exception),
        )
