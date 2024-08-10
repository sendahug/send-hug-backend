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

from utils.filter import WordFilter
from utils.push_notifications import (
    RawPushData,
    generate_push_data,
    generate_vapid_claims,
)
from utils.validator import ValidationError, Validator


@pytest.fixture(scope="class")
def test_validator():
    yield Validator(
        {
            "post": {"max": 480, "min": 1},
            "message": {"max": 480, "min": 1},
            "user": {"max": 60, "min": 1},
            "report": {"max": 120, "min": 1},
        }
    )


# Push notification tests
# =====================================================
def test_generate_push_data():
    base_data: RawPushData = {"type": "hug", "text": "Meow"}
    push_data = generate_push_data(base_data)

    assert push_data["title"] == "New hug"
    assert push_data["body"] == "Meow"


def test_generate_vapid_claims():
    vapid_claims = generate_vapid_claims()

    # TODO: Add check for the expiry time
    assert vapid_claims["sub"] == "mailto:sendahugcom@gmail.com"


# Validator tests
# =====================================================
@pytest.mark.parametrize(
    "text, obj_type, error_str",
    [
        (
            "xy" * 450,
            "Post",
            "Your Post is too long! Please shorten it and then try again.",
        ),
        (
            "",
            "Post",
            "Your Post cannot be empty. Please write something and then try again.",
        ),
        (
            "xy" * 450,
            "Display name",
            "Your new display name is too long! Please shorten it and then try again.",
        ),
        (
            "",
            "Display name",
            "Your display name cannot be empty. Please write "
            "something and then try again.",
        ),
        (
            "xy" * 450,
            "report",
            "Your report reason is too long! Please shorten it and then try again.",
        ),
        (
            "",
            "report",
            "You cannot send a report without a reason. Please write something "
            "and try to send it again.",
        ),
        (
            "",
            "anything",
            "anything cannot be empty. Please write something and try again.",
        ),
    ],
)
def test_validator_errors(test_validator, text, obj_type, error_str):
    with pytest.raises(ValidationError) as exc:
        test_validator.check_length(data=text, obj_type=obj_type)

    assert error_str in str(exc.value)


@pytest.mark.parametrize("text, obj_type", [("hi", "Post"), ("hello", "post text")])
def test_just_right(test_validator, text, obj_type):
    res = test_validator.check_length(data=text, obj_type=obj_type)
    assert res is True


@pytest.mark.parametrize(
    "data, obj_type, item_in_error, type_in_error",
    [
        (3, "post text", "post text", "String"),
        (3, "message text", "message text", "String"),
        (3, "display name", "display name", "String"),
        (3, "report reason", "report reason", "String"),
        (3, "search query", "search query", "String"),
        ("h", "user ID", "user ID", "Integer"),
    ],
)
def test_incorrect_type(test_validator, data, obj_type, item_in_error, type_in_error):
    with pytest.raises(ValidationError) as exc:
        test_validator.check_type(data=data, obj_type=obj_type)

    assert (
        f"{item_in_error} must be of type '{type_in_error}'. "
        "Please correct the error and try again."
    ) in str(exc.value)


@pytest.mark.parametrize(
    "data, obj_type",
    [
        ("hello", "post text"),
        ("hello", "message text"),
        ("hello", "display name"),
        ("hello", "report reason"),
        ("hello", "search query"),
        (3, "user ID"),
    ],
)
def test_correct_type(test_validator, data, obj_type):
    res = test_validator.check_type(data=data, obj_type=obj_type)
    assert res is True


# Validator tests
# =====================================================
def test_wordfilter_blacklisted():
    word_filter = WordFilter()
    blacklisted_result = word_filter.blacklisted("hi there", filtered_words=["hi"])

    assert blacklisted_result.is_blacklisted is True
    assert blacklisted_result.forbidden_words == "hi"
    assert len(blacklisted_result.badword_indexes) == 1
    assert blacklisted_result.badword_indexes[0].badword == "hi"
    assert blacklisted_result.badword_indexes[0].index == 0


def test_wordfilter_multiple_filters():
    word_filter = WordFilter()
    blacklisted_result = word_filter.blacklisted(
        "hi there", filtered_words=["hi", "bye"]
    )

    assert blacklisted_result.is_blacklisted is True
    assert blacklisted_result.forbidden_words == "hi"
    assert len(blacklisted_result.badword_indexes) == 1
    assert blacklisted_result.badword_indexes[0].badword == "hi"
    assert blacklisted_result.badword_indexes[0].index == 0


def test_wordfilter_multiple_filters_in_string():
    word_filter = WordFilter()
    blacklisted_result = word_filter.blacklisted(
        "hello how are you", filtered_words=["how", "you"]
    )

    assert blacklisted_result.is_blacklisted is True
    assert blacklisted_result.forbidden_words == "how,you"
    assert len(blacklisted_result.badword_indexes) == 2
    assert blacklisted_result.badword_indexes[0].badword == "how"
    assert blacklisted_result.badword_indexes[0].index == 6
    assert blacklisted_result.badword_indexes[1].badword == "you"
    assert blacklisted_result.badword_indexes[1].index == 14
