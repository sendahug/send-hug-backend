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

import json
from typing import Any

import pytest
from sqlalchemy import and_, false, select

from models import Notification


# Get New Notifications Route Tests ('/notifications', GET)
# -------------------------------------------------------
# Attempt to get user notifications without auth header
@pytest.mark.asyncio(scope="session")
async def test_get_notifications_no_auth(app_client, test_db):
    response = await app_client.get("/notifications")
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get user notifications with malformed auth header
@pytest.mark.asyncio(scope="session")
async def test_get_notifications_malformed_auth(app_client, test_db, user_headers):
    response = await app_client.get("/notifications", headers=user_headers["malformed"])
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get user notifications with a user's JWT
@pytest.mark.parametrize(
    "user, notification_count, total_pages",
    [
        ("user", 11, 1),
        ("moderator", 4, 1),
        ("admin", 20, 2),
    ],
)
@pytest.mark.asyncio(scope="session")
async def test_get_notifications(
    app_client, test_db, user_headers, user, notification_count, total_pages
):
    response = await app_client.get("/notifications", headers=user_headers[user])
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert len(response_data["notifications"]) == notification_count
    assert response_data["current_page"] == 1
    assert response_data["total_pages"] == total_pages


@pytest.mark.parametrize(
    "notification_count, read_status",
    [
        (10, "true"),
        (18, "false"),
    ],
)
@pytest.mark.asyncio(scope="session")
async def test_get_notifications_read_status(
    app_client, test_db, user_headers, notification_count, read_status
):
    response = await app_client.get(
        f"/notifications?readStatus={read_status}", headers=user_headers["admin"]
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert len(response_data["notifications"]) == notification_count


# Update Notifications Route Tests ('/notifications', PATCH)
# -------------------------------------------------------
# Attempt to update notifications without auth header
@pytest.mark.asyncio(scope="session")
async def test_update_notifications_no_auth(
    app_client, test_db, user_headers, dummy_request_data
):
    response = await app_client.patch(
        "/notifications", data=json.dumps(dummy_request_data["updated_notifications"])
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to update notifications with malformed auth header
@pytest.mark.asyncio(scope="session")
async def test_update_notifications_malformed_auth(
    app_client, test_db, user_headers, dummy_request_data
):
    response = await app_client.patch(
        "/notifications",
        data=json.dumps(dummy_request_data["updated_notifications"]),
        headers=user_headers["malformed"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to update notifications with a user's JWT
@pytest.mark.parametrize(
    "notification_ids, user",
    [([46, 70, 71], "user"), ([73, 80], "moderator"), ([2, 3, 4, 5], "admin")],
)
@pytest.mark.asyncio(scope="session")
async def test_update_notifications(
    app_client, test_db, user_headers, dummy_request_data, notification_ids, user
):
    dummy_request_data["updated_notifications"]["notification_ids"] = notification_ids
    response = await app_client.patch(
        "/notifications",
        data=json.dumps(dummy_request_data["updated_notifications"]),
        headers=user_headers[user],
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["updated"] == notification_ids
    assert response_data["read"] is True


# Attempt to update notifications with an admin's JWT
@pytest.mark.asyncio(scope="session")
async def test_update_all_notifications_as_admin(
    app_client, test_db, user_headers, dummy_request_data
):
    updated_ids = "all"
    dummy_request_data["updated_notifications"]["notification_ids"] = updated_ids
    response = await app_client.patch(
        "/notifications",
        data=json.dumps(dummy_request_data["updated_notifications"]),
        headers=user_headers["admin"],
    )
    response_data = await response.get_json()

    post_update = await test_db.paginate(
        select(Notification).where(
            and_(Notification.read == false(), Notification.for_id == 4)
        ),
        current_page=1,
    )

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["updated"] == "all"
    assert response_data["read"] is True
    assert post_update.total_items == 0


# Attempt to update notifications with invalid payload
@pytest.mark.asyncio(scope="session")
async def test_update_notifications_invalid_payload(app_client, test_db, user_headers):
    notifications_data = {"notifications": [], "mark_me": "read"}
    response = await app_client.patch(
        "/notifications",
        data=json.dumps(notifications_data),
        headers=user_headers["admin"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 400


# Attempt to update notifications with someone else's notifications
@pytest.mark.asyncio(scope="session")
async def test_update_notifications_another_users_notifications(
    app_client, test_db, user_headers, dummy_request_data
):
    notification_ids = [2, 3, 4, 5, 73]
    dummy_request_data["updated_notifications"]["notification_ids"] = notification_ids
    response = await app_client.patch(
        "/notifications",
        data=json.dumps(dummy_request_data["updated_notifications"]),
        headers=user_headers["admin"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 403


# Add New Push Subscription Route Tests ('/push_subscriptions', POST)
# -------------------------------------------------------
# Attempt to create push subscription without auth header
@pytest.mark.asyncio(scope="session")
async def test_post_subscription_no_auth(
    app_client, test_db, user_headers, dummy_request_data
):
    response = await app_client.post(
        "/push_subscriptions", data=json.dumps(dummy_request_data["new_subscription"])
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to create push subscription with malformed auth header
@pytest.mark.asyncio(scope="session")
async def test_post_subscription_malformed_auth(
    app_client, test_db, user_headers, dummy_request_data
):
    response = await app_client.post(
        "/push_subscriptions",
        data=json.dumps(dummy_request_data["new_subscription"]),
        headers=user_headers["malformed"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to create push subscription with a user's JWT
@pytest.mark.asyncio(scope="session")
async def test_post_subscription_as_user(
    app_client, test_db, user_headers, dummy_request_data
):
    response = await app_client.post(
        "/push_subscriptions",
        data=json.dumps(dummy_request_data["new_subscription"]),
        headers=user_headers["user"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["subscribed"] == "shirb"


# Attempt to create push subscription with a moderator's JWT
@pytest.mark.asyncio(scope="session")
async def test_post_subscription_as_mod(
    app_client, test_db, user_headers, dummy_request_data
):
    response = await app_client.post(
        "/push_subscriptions",
        data=json.dumps(dummy_request_data["new_subscription"]),
        headers=user_headers["moderator"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["subscribed"] == "user52"


# Attempt to create push subscription with an admin's JWT
@pytest.mark.asyncio(scope="session")
async def test_post_subscription_as_admin(
    app_client, test_db, user_headers, dummy_request_data
):
    response = await app_client.post(
        "/push_subscriptions",
        data=json.dumps(dummy_request_data["new_subscription"]),
        headers=user_headers["admin"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["subscribed"] == "user14"


# Attempt to create push subscription with an admin's JWT
@pytest.mark.asyncio(scope="session")
async def test_post_subscription_empty_data_as_admin(app_client, test_db, user_headers):
    response = await app_client.post(
        "/push_subscriptions",
        data=None,
        headers=user_headers["admin"],
    )
    response_data = await response.data

    assert response_data == bytes("", encoding="utf-8")
    assert response.status_code == 204


# Update Push Subscription Route Tests ('/push_subscriptions/<sub_id>', PATCH)
# -------------------------------------------------------
# Attempt to update push subscription without auth header
@pytest.mark.asyncio(scope="session")
async def test_update_subscription_no_auth(
    app_client, test_db, user_headers, dummy_request_data
):
    # Create the subscription
    await app_client.post(
        "/push_subscriptions",
        data=json.dumps(dummy_request_data["new_subscription"]),
        headers=user_headers["user"],
    )
    # Then update it
    updated_subscription: dict[str, Any] = {**dummy_request_data["new_subscription"]}
    updated_subscription["id"] = 1
    response = await app_client.patch(
        "/push_subscriptions/1", data=json.dumps(dummy_request_data["new_subscription"])
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to update push subscription with malformed auth header
@pytest.mark.asyncio(scope="session")
async def test_update_subscription_malformed_auth(
    app_client, test_db, user_headers, dummy_request_data
):
    # Create the subscription
    await app_client.post(
        "/push_subscriptions",
        data=json.dumps(dummy_request_data["new_subscription"]),
        headers=user_headers["user"],
    )
    # Then update it
    updated_subscription: dict[str, Any] = {**dummy_request_data["new_subscription"]}
    updated_subscription["id"] = 1
    response = await app_client.patch(
        "/push_subscriptions/1",
        data=json.dumps(dummy_request_data["new_subscription"]),
        headers=user_headers["malformed"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to update push subscription with a user's JWT
@pytest.mark.asyncio(scope="session")
async def test_update_subscription_as_user(
    app_client, test_db, user_headers, dummy_request_data
):
    updated_subscription: dict[str, Any] = {**dummy_request_data["new_subscription"]}
    updated_subscription["id"] = 1
    response = await app_client.patch(
        "/push_subscriptions/1",
        data=json.dumps(dummy_request_data["new_subscription"]),
        headers=user_headers["user"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["subscribed"] == "shirb"
    assert response_data["subId"] == 1


# Attempt to create push subscription with a moderator's JWT
@pytest.mark.asyncio(scope="session")
async def test_update_subscription_as_mod(
    app_client, test_db, user_headers, dummy_request_data
):
    updated_subscription: dict[str, Any] = {**dummy_request_data["new_subscription"]}
    updated_subscription["id"] = 2
    response = await app_client.patch(
        "/push_subscriptions/2",
        data=json.dumps(dummy_request_data["new_subscription"]),
        headers=user_headers["moderator"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["subscribed"] == "user52"
    assert response_data["subId"] == 2


# Attempt to create push subscription with an admin's JWT
@pytest.mark.asyncio(scope="session")
async def test_update_subscription_as_admin(
    app_client, test_db, user_headers, dummy_request_data
):
    updated_subscription: dict[str, Any] = {**dummy_request_data["new_subscription"]}
    updated_subscription["id"] = 3
    response = await app_client.patch(
        "/push_subscriptions/3",
        data=json.dumps(dummy_request_data["new_subscription"]),
        headers=user_headers["admin"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["subscribed"] == "user14"
    assert response_data["subId"] == 3


# Attempt to create push subscription with an admin's JWT
@pytest.mark.asyncio(scope="session")
async def test_update_subscription_empty_data_as_admin(
    app_client, test_db, user_headers
):
    response = await app_client.patch(
        "/push_subscriptions/1",
        data=None,
        headers=user_headers["admin"],
    )
    response_data = await response.data

    assert response_data == bytes("", encoding="utf-8")
    assert response.status_code == 204
