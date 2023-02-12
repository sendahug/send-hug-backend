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

from datetime import datetime

DATETIME_PATTERN = "%Y-%m-%d %H:%M:%S.%f"

# test_app data
# ==========================================================
# Sample users data
sample_user_id = str(1)
sample_user_auth0_id = "auth0|5ed34765f0b8e60c8e87ca62"
sample_moderator_id = str(5)
sample_moderator_auth0_id = "auth0|5ede3e7a0793080013259050"
sample_admin_id = str(4)
sample_admin_auth0_id = "auth0|5ed8e3d0def75d0befbc7e50"
blocked_user_id = str(20)

# Item Samples
new_post = {
    "userId": 0,
    "text": "test post",
    "date": "Sun Jun 07 2020 15:57:45",
    "givenHugs": 0,
}

updated_post = {
    "userId": 0,
    "text": "test post",
    "date": "Sun Jun 07 2020 15:57:45",
    "givenHugs": 0,
}

report_post = {
    "user_id": 0,
    "text": "test post",
    "date": "Sun Jun 07 2020 15:57:45",
    "givenHugs": 0,
    "closeReport": 1,
}

new_user = '{\
"id": "auth0|5edf778e56d062001335196e",\
"displayName": "user",\
"receivedH": 0,\
"givenH": 0,\
"loginCount": 0 }'

updated_user = {
    "id": 0,
    "displayName": "",
    "receivedH": 0,
    "givenH": 0,
    "loginCount": 0,
}

updated_unblock_user = {
    "id": 0,
    "displayName": "hello",
    "receivedH": 0,
    "givenH": 0,
    "loginCount": 0,
    "blocked": False,
    "releaseDate": None,
}

updated_display = {
    "id": 0,
    "displayName": "meow",
    "receivedH": 0,
    "givenH": 0,
    "loginCount": 0,
}

new_message = {
    "fromId": 0,
    "forId": 0,
    "messageText": "meow",
    "date": "Sun Jun 07 2020 15:57:45",
}

new_report = {
    "type": "Post",
    "userID": 0,
    "postID": 0,
    "reporter": 0,
    "reportReason": "It is inappropriate",
    "date": "Sun Jun 07 2020 15:57:45",
}

new_user_report = {
    "type": "User",
    "userID": 0,
    "reporter": 0,
    "reportReason": "The user is posting Spam",
    "date": "Sun Jun 07 2022 15:57:45",
}

new_subscription = {
    "endpoint": "https://fcm.googleapis.com/fcm/send/epyhl2GD",
    "expirationTime": None,
    "keys": {"p256dh": "fdsfd", "auth": "dfs"},
}

# test_db_helpers data
# ==========================================================
updated_post_1 = {
    "id": 1,
    "userId": 1,
    "user": "",
    "text": "new test",
    "date": datetime.strptime("2020-06-01 15:05:01.966", DATETIME_PATTERN),
    "givenHugs": 2,
    "sentHugs": ["4"],
}
