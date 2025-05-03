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

import os
from typing import TypedDict

from python_http_client.client import Response
from sendgrid import SendGridAPIClient  # type: ignore
from sendgrid.helpers.mail import Content, Email, Mail, To  # type: ignore

# TODO: move this to a common utils module and rename
from utils.push_notifications import RawPushData

EmailData = TypedDict("EmailData", {"to": str, "subject": str, "content": str})

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000/")
SG_CLIENT = SendGridAPIClient(api_key=os.environ.get("SENDGRID_KEY"))
DEFAULT_FROM = "notifications@send-hug.com"


class MissingEmailToError(Exception):
    pass


class MissingEmailFromError(Exception):
    pass


class MissingEmailSubjectError(Exception):
    pass


class MissingEmailContentError(Exception):
    pass


class InvalidEmailToError(Exception):
    pass


class InvalidEmailFromError(Exception):
    pass


def generate_email_data(to: str, data: RawPushData) -> EmailData:
    """
    Generates the email notification's data from the
    given raw data.
    """
    notification_data: EmailData = {
        "to": to,
        "subject": f"New {data['type']}",
        "content": f"{data['text']}\n\n{FRONTEND_URL}messages/inbox",
    }

    return notification_data


def send_email(
    to: str, subject: str, content: str, from_email: str = DEFAULT_FROM
) -> Response:
    """
    Function that simplifies the sending of emails for use in notifications or similar
    """
    if not to:
        raise MissingEmailToError("Missing email 'to' field")
    if not from_email:
        raise MissingEmailFromError("Missing email 'from' field")
    if not subject:
        raise MissingEmailSubjectError("Missing email 'subject' field")
    if not content:
        raise MissingEmailContentError("Missing email 'content' field")

    to_address = To(to)
    if not to_address.email:
        raise InvalidEmailToError(f"Invalid email 'to' field: {to}")
    from_address = Email(from_email)
    if not from_address.email:
        raise InvalidEmailFromError(f"Invalid email 'from' field: {from_email}")

    mail = Mail(Email(from_email), To(to), subject, Content("text/plain", content))
    # No types. Le sigh https://github.com/sendgrid/sendgrid-python/issues/956
    response = SG_CLIENT.client.mail.send.post(request_body=mail.get())  # type: ignore

    return response
