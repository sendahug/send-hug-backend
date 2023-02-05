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

from typing import Union, Optional, Literal

from .filter import WordFilter


# Validation Error
class ValidationError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Validator
class Validator:
    constraints: dict[str, dict[str, int]] = {}
    word_filter: WordFilter = WordFilter()

    # INIT
    def __init__(self, types: dict[str, dict[str, int]]):
        self.constraints = types

    # Checks the length according to the given types
    def check_length(self, data: str, obj_type: str):
        """
        Checks the length of the data according to the object type.

        param data: The string to check
        param obj_type: The type of object to test by
        """
        too_long_error = "Your {} is too long! Please shorten it and then try again."
        too_short_error = (
            "Your {} cannot be empty. Please write something and then try again."
        )
        error_message: Optional[str] = None

        if obj_type.lower() in [self.constraints.keys()]:
            # Check if the item is too long
            if len(data) > self.constraints[obj_type.lower()]["max"]:
                error_message = too_long_error.format(obj_type)
            # Check if the item is empty
            elif len(data) < self.constraints[obj_type.lower()]["min"]:
                error_message = too_short_error.format(obj_type)

        elif obj_type.lower() == "display name":
            # Check if the name is too long
            if len(data) > self.constraints["user"]["max"]:
                error_message = too_long_error.format("new display name")
            # Check if the name is empty
            elif len(data) < self.constraints["user"]["min"]:
                error_message = too_short_error.format("display name")

        elif obj_type.lower() == "report":
            # Check if the report reason is too long
            if len(data) > self.constraints["report"]["max"]:
                error_message = too_long_error.format("report reason")
            # Check if the report reason is empty
            elif len(data) < self.constraints["report"]["min"]:
                error_message = (
                    "You cannot send a report without a reason. "
                    "Please write something and try to send it again."
                )

        else:
            # Check if the data is empty
            if len(data) < 1:
                error_message = (
                    f"{obj_type} cannot be empty. "
                    "Please write something and try again."
                )

        # if anything failed validation, raise an error
        if error_message:
            raise ValidationError(
                {
                    "code": 400,
                    "description": error_message,
                },
                400,
            )

        return True

    # Checks the type of the given item
    def check_type(self, data: Union[str, int], obj_type: str):
        """
        Checks the type of the data matches the expected type.

        param data: The item to check
        param obj_type: The type of object to test by
        """
        text_types = [
            "post text",
            "message text",
            "display name",
            "report reason",
            "search query",
        ]
        error_message = (
            "{} must be of type '{}'. Please correct the error and try again."
        )

        # If the type is one of the free text types, check that it's a
        # string
        if obj_type.lower() in text_types and type(data) is not str:
            # If it's not a string, raise a validation error
            raise ValidationError(
                {
                    "code": 400,
                    "description": error_message.format(obj_type, "String"),
                },
                400,
            )

        # If the type is one of the ID types, check that it's an integer
        elif "id" in obj_type.lower():
            # Try to convert the data to int
            try:
                int(data)
            # If there's a problem, it's not an integer,
            except Exception:
                # Raise a validation error
                raise ValidationError(
                    {
                        "code": 400,
                        "description": error_message.format(obj_type, "Integer"),
                    },
                    400,
                )

        return True

    def validate_post_or_message(self, text: str, type: Literal["post", "message"]):
        """
        Validates a post/message
        """
        blacklist_check = self.word_filter.blacklisted(text)

        # If there's no blacklisted word, check the length and type
        if blacklist_check.is_blacklisted is False:
            # Check the length and type of the post's text
            self.check_length(text, type)
            self.check_type(text, f"{type} text")
        # If there's a blacklisted word / phrase, alert the user
        else:
            num_issues = len(blacklist_check.badword_indexes)
            raise ValidationError(
                {
                    "code": 400,
                    "description": f"Your text contains {str(num_issues)}"
                    " forbidden term(s). The following word(s) is/"
                    f"are not allowed: {blacklist_check.forbidden_words}."
                    f"Please fix your {type}'s text and try again.",
                },
                400,
            )
