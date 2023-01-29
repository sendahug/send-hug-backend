"""
Push notifications related methods.
"""
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
from typing import Dict, Union, Any
from datetime import datetime, timedelta


def generate_push_data(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Generates the push notification's data from the
    given raw data.
    """
    notification_data = {"title": "New " + data["type"], "body": data["text"]}

    return notification_data


def generate_vapid_claims() -> Dict[str, Union[str, float]]:
    """
    Generates the VAPID claims dictionary.
    """
    expiry_time = datetime.timestamp(datetime.utcnow() + timedelta(hours=12))
    vapid_claims: Dict[str, Union[str, float]] = {
        "sub": "mailto:theobjectivistb@gmail.com",
        "exp": expiry_time,
    }

    return vapid_claims
