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

# Validation Error
class ValidationError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Validator
class Validator:
    constraints = {}

    # INIT
    def __init__(self, types):
        self.constraints = types

    # Checks the length according to the given types
    def check_length(self, data, objType):
        too_long_error = "Your {} is too long! Please shorten it and then try again."
        too_short_error = (
            "Your {} cannot be empty. Please write something and then try again."
        )

        if objType.lower() in [self.constraints.keys()]:
            # Check if the item is too long; if it is, abort
            if len(data) > self.constraints[objType.lower()]["max"]:
                raise ValidationError(
                    {"code": 400, "description": too_long_error.format(objType)},
                    400,
                )
            # Check if the item is empty; if it is, abort
            elif len(data) < self.constraints[objType.lower()]["min"]:
                raise ValidationError(
                    {"code": 400, "description": too_short_error.format(objType)},
                    400,
                )

        elif objType.lower() == "display name":
            # Check if the name is too long; if it is, abort
            if len(data) > self.constraints["user"]["max"]:
                raise ValidationError(
                    {
                        "code": 400,
                        "description": too_long_error.format("new display name"),
                    },
                    400,
                )
            # Check if the name is empty; if it is, abort
            elif len(data) < self.constraints["user"]["min"]:
                raise ValidationError(
                    {
                        "code": 400,
                        "description": too_short_error.format("display name"),
                    },
                    400,
                )

        elif objType.lower() == "report":
            # Check if the report reason is too long; if it is, abort
            if len(data) > self.constraints["report"]["max"]:
                raise ValidationError(
                    {
                        "code": 400,
                        "description": too_long_error.format("report reason"),
                    },
                    400,
                )
            # Check if the report reason is empty; if it is, abort
            elif len(data) < self.constraints["report"]["min"]:
                raise ValidationError(
                    {
                        "code": 400,
                        "description": "You cannot send a report without a reason. \
                                    Please write something and try to send it \
                                    again.",
                    },
                    400,
                )

        else:
            # Check if the data is empty
            if len(data) < 1:
                raise ValidationError(
                    {
                        "code": 400,
                        "description": f"{objType} cannot be empty. Please write \
                                    something and try again.",
                    },
                    400,
                )

        return True

    # Checks the type of the given item
    def check_type(self, data, objType):
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
        if objType.lower() in text_types:
            # If it's not a string, raise a validation error
            if type(data) is not str:
                raise ValidationError(
                    {
                        "code": 400,
                        "description": error_message.format(objType, "String"),
                    },
                    400,
                )

        # If the type is one of the ID types, check that it's an integer
        elif "id" in objType.lower():
            # Try to convert the data to int
            try:
                int(data)
            # If there's a problem, it's not an integer,
            except Exception:
                # Raise a validation error
                raise ValidationError(
                    {
                        "code": 400,
                        "description": error_message.format(objType, "Integer"),
                    },
                    400,
                )

        return True
