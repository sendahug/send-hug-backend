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

from typing import Any
import json


# Get New Notifications Route Tests ('/notifications', GET)
# -------------------------------------------------------
# Attempt to get user notifications without auth header
def test_get_notifications_no_auth(app_client, test_db, user_headers):
    response = app_client.get("/notifications")
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get user notifications with malformed auth header
def test_get_notifications_malformed_auth(app_client, test_db, user_headers):
    response = app_client.get("/notifications", headers=user_headers["malformed"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get user notifications with a user's JWT (silent refresh)
def test_get_silent_notifications_as_user(
    app_client, test_db, user_headers, dummy_users_data
):
    pre_user_query = app_client.get(
        f"/users/all/{dummy_users_data['user']['auth0']}", headers=user_headers["user"]
    )
    pre_user_data = json.loads(pre_user_query.data)["user"]
    response = app_client.get(
        "/notifications?silentRefresh=true", headers=user_headers["user"]
    )
    response_data = json.loads(response.data)
    post_user_query = app_client.get(
        f"/users/all/{dummy_users_data['user']['auth0']}", headers=user_headers["user"]
    )
    post_user_data = json.loads(post_user_query.data)["user"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert len(response_data["notifications"]) == 11
    assert (
        pre_user_data["last_notifications_read"]
        == post_user_data["last_notifications_read"]
    )


# Attempt to get user notifications with a user's JWT (non-silent refresh)
def test_get_non_silent_notifications_as_user(
    app_client, test_db, user_headers, dummy_users_data
):
    pre_user_query = app_client.get(
        f"/users/all/{dummy_users_data['user']['auth0']}", headers=user_headers["user"]
    )
    pre_user_data = json.loads(pre_user_query.data)["user"]
    response = app_client.get(
        "/notifications?silentRefresh=false", headers=user_headers["user"]
    )
    response_data = json.loads(response.data)
    post_user_query = app_client.get(
        f"/users/all/{dummy_users_data['user']['auth0']}", headers=user_headers["user"]
    )
    post_user_data = json.loads(post_user_query.data)["user"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert len(response_data["notifications"]) == 11
    assert (
        pre_user_data["last_notifications_read"]
        != post_user_data["last_notifications_read"]
    )


# Attempt to get user notifications with a mod's JWT (silent refresh)
def test_get_silent_notifications_as_mod(
    app_client, test_db, user_headers, dummy_users_data
):
    pre_user_query = app_client.get(
        f"/users/all/{dummy_users_data['moderator']['auth0']}",
        headers=user_headers["moderator"],
    )
    pre_user_data = json.loads(pre_user_query.data)["user"]
    response = app_client.get(
        "/notifications?silentRefresh=true", headers=user_headers["moderator"]
    )
    response_data = json.loads(response.data)
    post_user_query = app_client.get(
        f"/users/all/{dummy_users_data['moderator']['auth0']}",
        headers=user_headers["moderator"],
    )
    post_user_data = json.loads(post_user_query.data)["user"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert len(response_data["notifications"]) == 4
    assert (
        pre_user_data["last_notifications_read"]
        == post_user_data["last_notifications_read"]
    )


# Attempt to get user notifications with a mod's JWT (non-silent refresh)
def test_get_non_silent_notifications_as_mod(
    app_client, test_db, user_headers, dummy_users_data
):
    pre_user_query = app_client.get(
        f"/users/all/{dummy_users_data['moderator']['auth0']}",
        headers=user_headers["moderator"],
    )
    pre_user_data = json.loads(pre_user_query.data)["user"]
    response = app_client.get(
        "/notifications?silentRefresh=false", headers=user_headers["moderator"]
    )
    response_data = json.loads(response.data)
    post_user_query = app_client.get(
        f"/users/all/{dummy_users_data['moderator']['auth0']}",
        headers=user_headers["moderator"],
    )
    post_user_data = json.loads(post_user_query.data)["user"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert len(response_data["notifications"]) == 4
    assert (
        pre_user_data["last_notifications_read"]
        != post_user_data["last_notifications_read"]
    )


# Attempt to get user notifications with an admin's JWT (silently)
def test_get_silent_notifications_as_admin(
    app_client, test_db, user_headers, dummy_users_data
):
    pre_user_query = app_client.get(
        f"/users/all/{dummy_users_data['admin']['auth0']}",
        headers=user_headers["admin"],
    )
    pre_user_data = json.loads(pre_user_query.data)["user"]
    response = app_client.get(
        "/notifications?silentRefresh=true", headers=user_headers["admin"]
    )
    response_data = json.loads(response.data)
    post_user_query = app_client.get(
        f"/users/all/{dummy_users_data['admin']['auth0']}",
        headers=user_headers["admin"],
    )
    post_user_data = json.loads(post_user_query.data)["user"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert len(response_data["notifications"]) == 9
    assert (
        pre_user_data["last_notifications_read"]
        == post_user_data["last_notifications_read"]
    )


# Attempt to get user notifications with an admin's JWT (non-silently)
def test_get_non_silent_notifications_as_admin(
    app_client, test_db, user_headers, dummy_users_data
):
    pre_user_query = app_client.get(
        f"/users/all/{dummy_users_data['admin']['auth0']}",
        headers=user_headers["admin"],
    )
    pre_user_data = json.loads(pre_user_query.data)["user"]
    response = app_client.get(
        "/notifications?silentRefresh=false", headers=user_headers["admin"]
    )
    response_data = json.loads(response.data)
    post_user_query = app_client.get(
        f"/users/all/{dummy_users_data['admin']['auth0']}",
        headers=user_headers["admin"],
    )
    post_user_data = json.loads(post_user_query.data)["user"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert len(response_data["notifications"]) == 9
    assert (
        pre_user_data["last_notifications_read"]
        != post_user_data["last_notifications_read"]
    )


# Add New Push Subscription Route Tests ('/notifications', POST)
# -------------------------------------------------------
# Attempt to create push subscription without auth header
def test_post_subscription_no_auth(
    app_client, test_db, user_headers, dummy_request_data
):
    response = app_client.post(
        "/notifications", data=json.dumps(dummy_request_data["new_subscription"])
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to create push subscription with malformed auth header
def test_post_subscription_malformed_auth(
    app_client, test_db, user_headers, dummy_request_data
):
    response = app_client.post(
        "/notifications",
        data=json.dumps(dummy_request_data["new_subscription"]),
        headers=user_headers["malformed"],
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to create push subscription with a user's JWT
def test_post_subscription_as_user(
    app_client, test_db, user_headers, dummy_request_data
):
    response = app_client.post(
        "/notifications",
        data=json.dumps(dummy_request_data["new_subscription"]),
        headers=user_headers["user"],
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["subscribed"] == "shirb"
    assert response_data["subId"] == 11


# Attempt to create push subscription with a moderator's JWT
def test_post_subscription_as_mod(
    app_client, test_db, user_headers, dummy_request_data
):
    response = app_client.post(
        "/notifications",
        data=json.dumps(dummy_request_data["new_subscription"]),
        headers=user_headers["moderator"],
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["subscribed"] == "user52"
    assert response_data["subId"] == 11


# Attempt to create push subscription with an admin's JWT
def test_post_subscription_as_admin(
    app_client, test_db, user_headers, dummy_request_data
):
    response = app_client.post(
        "/notifications",
        data=json.dumps(dummy_request_data["new_subscription"]),
        headers=user_headers["admin"],
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["subscribed"] == "user14"
    assert response_data["subId"] == 11


# Attempt to create push subscription with an admin's JWT
def test_post_subscription_empty_data_as_admin(app_client, test_db, user_headers):
    response = app_client.post(
        "/notifications",
        data=None,
        headers=user_headers["admin"],
    )
    response_data = response.data

    assert response_data == bytes("", encoding="utf-8")
    assert response.status_code == 204


# Update Push Subscription Route Tests ('/notifications/<sub_id>', PATCH)
# -------------------------------------------------------
# Attempt to update push subscription without auth header
def test_update_subscription_no_auth(
    app_client, test_db, user_headers, dummy_request_data
):
    # Create the subscription
    app_client.post(
        "/notifications",
        data=json.dumps(dummy_request_data["new_subscription"]),
        headers=user_headers["user"],
    )
    # Then update it
    updated_subscription: dict[str, Any] = {**dummy_request_data["new_subscription"]}
    updated_subscription["id"] = 11
    response = app_client.patch(
        "/notifications/11", data=json.dumps(dummy_request_data["new_subscription"])
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to update push subscription with malformed auth header
def test_update_subscription_malformed_auth(
    app_client, test_db, user_headers, dummy_request_data
):
    # Create the subscription
    app_client.post(
        "/notifications",
        data=json.dumps(dummy_request_data["new_subscription"]),
        headers=user_headers["user"],
    )
    # Then update it
    updated_subscription: dict[str, Any] = {**dummy_request_data["new_subscription"]}
    updated_subscription["id"] = 11
    response = app_client.patch(
        "/notifications/11",
        data=json.dumps(dummy_request_data["new_subscription"]),
        headers=user_headers["malformed"],
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to update push subscription with a user's JWT
def test_update_subscription_as_user(
    app_client, test_db, user_headers, dummy_request_data
):
    # Create the subscription
    app_client.post(
        "/notifications",
        data=json.dumps(dummy_request_data["new_subscription"]),
        headers=user_headers["user"],
    )
    # Then update it
    updated_subscription: dict[str, Any] = {**dummy_request_data["new_subscription"]}
    updated_subscription["id"] = 11
    response = app_client.patch(
        "/notifications/11",
        data=json.dumps(dummy_request_data["new_subscription"]),
        headers=user_headers["user"],
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["subscribed"] == "shirb"
    assert response_data["subId"] == 11


# Attempt to create push subscription with a moderator's JWT
def test_update_subscription_as_mod(
    app_client, test_db, user_headers, dummy_request_data
):
    # Create the subscription
    app_client.post(
        "/notifications",
        data=json.dumps(dummy_request_data["new_subscription"]),
        headers=user_headers["moderator"],
    )
    # Then update it
    updated_subscription: dict[str, Any] = {**dummy_request_data["new_subscription"]}
    updated_subscription["id"] = 11
    response = app_client.patch(
        "/notifications/11",
        data=json.dumps(dummy_request_data["new_subscription"]),
        headers=user_headers["moderator"],
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["subscribed"] == "user52"
    assert response_data["subId"] == 11


# Attempt to create push subscription with an admin's JWT
def test_update_subscription_as_admin(
    app_client, test_db, user_headers, dummy_request_data
):
    # Create the subscription
    app_client.post(
        "/notifications",
        data=json.dumps(dummy_request_data["new_subscription"]),
        headers=user_headers["admin"],
    )
    # Then update it
    updated_subscription: dict[str, Any] = {**dummy_request_data["new_subscription"]}
    updated_subscription["id"] = 11
    response = app_client.patch(
        "/notifications/11",
        data=json.dumps(dummy_request_data["new_subscription"]),
        headers=user_headers["admin"],
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["subscribed"] == "user14"
    assert response_data["subId"] == 11


# Attempt to create push subscription with an admin's JWT
def test_update_subscription_empty_data_as_admin(app_client, test_db, user_headers):
    response = app_client.patch(
        "/notifications/1",
        data=None,
        headers=user_headers["admin"],
    )
    response_data = response.data

    assert response_data == bytes("", encoding="utf-8")
    assert response.status_code == 204
