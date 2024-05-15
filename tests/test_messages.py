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

import pytest


# Get User's Messages Tests ('/messages', GET)
# -------------------------------------------------------
# Attempt to get a user's messages without auth header
@pytest.mark.asyncio(scope="session")
async def test_get_user_messages_no_auth(app_client, test_db, user_headers):
    response = await app_client.get("/messages?userID=1")
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get a user's messages with malformed auth header
@pytest.mark.asyncio(scope="session")
async def test_get_user_messages_malformed_auth(app_client, test_db, user_headers):
    response = await app_client.get(
        "/messages?userID=1", headers=user_headers["malformed"]
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get a user's inbox with a user's JWT
@pytest.mark.asyncio(scope="session")
async def test_get_user_inbox_as_user(
    app_client, test_db, user_headers, dummy_users_data
):
    response = await app_client.get(
        f"/messages?userID={dummy_users_data['user']['internal']}",
        headers=user_headers["user"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["current_page"] == 1
    assert response_data["total_pages"] == 1
    assert len(response_data["messages"]) == 5


# Attempt to get a user's outbox with a user's JWT
@pytest.mark.asyncio(scope="session")
async def test_get_user_outbox_as_user(
    app_client, test_db, user_headers, dummy_users_data
):
    response = await app_client.get(
        f"/messages?type=outbox&userID={dummy_users_data['user']['internal']}",
        headers=user_headers["user"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["current_page"] == 1
    assert response_data["total_pages"] == 1
    assert len(response_data["messages"]) == 2


# Attempt to get a user's threads mailbox with a user's JWT
@pytest.mark.asyncio(scope="session")
async def test_get_user_threads_as_user(
    app_client, test_db, user_headers, dummy_users_data
):
    response = await app_client.get(
        f"/messages?type=threads&userID={dummy_users_data['user']['internal']}",
        headers=user_headers["user"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["current_page"] == 1
    assert response_data["total_pages"] == 1
    assert len(response_data["messages"]) == 4


# Attempt to get another user's messages with a user's JWT
@pytest.mark.asyncio(scope="session")
async def test_get_another_users_messages_as_user(
    app_client, test_db, user_headers, dummy_users_data
):
    response = await app_client.get(
        f"/messages?userID={dummy_users_data['moderator']['internal']}",
        headers=user_headers["user"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to get a user's inbox with a moderator's JWT
@pytest.mark.asyncio(scope="session")
async def test_get_user_inbox_as_mod(
    app_client, test_db, user_headers, dummy_users_data
):
    response = await app_client.get(
        f"/messages?userID={dummy_users_data['moderator']['internal']}",
        headers=user_headers["moderator"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["current_page"] == 1
    assert response_data["total_pages"] == 1
    assert len(response_data["messages"]) == 5


# Attempt to get a user's outbox with a moderator's JWT
@pytest.mark.asyncio(scope="session")
async def test_get_user_outbox_as_mod(
    app_client, test_db, user_headers, dummy_users_data
):
    response = await app_client.get(
        f"/messages?type=outbox&userID={dummy_users_data['moderator']['internal']}",
        headers=user_headers["moderator"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["current_page"] == 1
    assert response_data["total_pages"] == 1
    assert len(response_data["messages"]) == 1


# Attempt to get a user's threads mailbox with a moderator's JWT
@pytest.mark.asyncio(scope="session")
async def test_get_user_threads_as_mod(
    app_client, test_db, user_headers, dummy_users_data
):
    response = await app_client.get(
        f"/messages?type=threads&userID={dummy_users_data['moderator']['internal']}",
        headers=user_headers["moderator"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["current_page"] == 1
    assert response_data["total_pages"] == 1
    assert len(response_data["messages"]) == 3


#  Attempt to get another user's messages with a moderator's JWT
@pytest.mark.asyncio(scope="session")
async def test_get_another_users_messages_as_mod(
    app_client, test_db, user_headers, dummy_users_data
):
    response = await app_client.get(
        f"/messages?userID={dummy_users_data['admin']['internal']}",
        headers=user_headers["moderator"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to get a user's inbox with an admin's JWT
@pytest.mark.asyncio(scope="session")
async def test_get_user_inbox_as_admin(
    app_client, test_db, user_headers, dummy_users_data
):
    response = await app_client.get(
        f"/messages?userID={dummy_users_data['admin']['internal']}",
        headers=user_headers["admin"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["current_page"] == 1
    assert response_data["total_pages"] == 1
    assert len(response_data["messages"]) == 2


# Attempt to get a user's outbox with an admin's JWT
@pytest.mark.asyncio(scope="session")
async def test_get_user_outbox_as_admin(
    app_client, test_db, user_headers, dummy_users_data
):
    response = await app_client.get(
        f"/messages?type=outbox&userID={dummy_users_data['admin']['internal']}",
        headers=user_headers["admin"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["current_page"] == 1
    assert response_data["total_pages"] == 1
    assert len(response_data["messages"]) == 4


# Attempt to get a user's threads mailbox with an admin's JWT
@pytest.mark.asyncio(scope="session")
async def test_get_user_threads_as_admin(
    app_client, test_db, user_headers, dummy_users_data
):
    response = await app_client.get(
        f"/messages?type=threads&userID={dummy_users_data['admin']['internal']}",
        headers=user_headers["admin"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["current_page"] == 1
    assert response_data["total_pages"] == 1
    assert len(response_data["messages"]) == 2


# Attempt to get another user's messages with an admin's JWT
@pytest.mark.asyncio(scope="session")
async def test_get_another_users_messages_as_admin(
    app_client, test_db, user_headers, dummy_users_data
):
    response = await app_client.get(
        f"/messages?userID={dummy_users_data['user']['internal']}",
        headers=user_headers["admin"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to get a user's messages with no ID (with admin's JWT)
@pytest.mark.asyncio(scope="session")
async def test_get_no_id_user_messages_as_admin(app_client, test_db, user_headers):
    response = await app_client.get("/messages", headers=user_headers["admin"])
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 400


# Attempt to get other users' messaging thread (with admin's JWT)
@pytest.mark.asyncio(scope="session")
async def get_other_users_thread_as_admin(app_client, test_db, user_headers):
    response = await app_client.get(
        "/messages?userID=4&type=thread&threadID=2",
        headers=user_headers["admin"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to get other users' messaging thread (with admin's JWT)
@pytest.mark.asyncio(scope="session")
async def get_nonexistent_thread_as_admin(
    app_client, test_db, user_headers, dummy_users_data
):
    response = await app_client.get(
        f"/messages?userID={dummy_users_data['admin']['internal']}"
        "&type=thread&threadID=200",
        headers=user_headers["admin"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 404


@pytest.mark.asyncio(scope="session")
async def test_threadas_message_count_shows_user_count(
    app_client, test_db, user_headers, dummy_users_data
):
    admin_response = await app_client.get(
        f"/messages?type=threads&userID={dummy_users_data['admin']['internal']}",
        headers=user_headers["admin"],
    )
    admin_response_data = await admin_response.get_json()

    user_response = await app_client.get(
        f"/messages?type=threads&userID={dummy_users_data['user']['internal']}",
        headers=user_headers["user"],
    )
    user_response_data = await user_response.get_json()

    thread_3_admin = [
        thread for thread in admin_response_data["messages"] if thread["id"] == 3
    ]
    thread_3_user = [
        thread for thread in user_response_data["messages"] if thread["id"] == 3
    ]

    assert thread_3_admin[0]["numMessages"] != thread_3_user[0]["numMessages"]


# Create Message Route Tests ('/message', POST)
# -------------------------------------------------------
# Attempt to create a message with no authorisation header
@pytest.mark.asyncio(scope="session")
async def test_send_message_no_auth(
    app_client, test_db, user_headers, dummy_request_data
):
    response = await app_client.post(
        "/messages", data=json.dumps(dummy_request_data["new_message"])
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to create a message with a malformed auth header
@pytest.mark.asyncio(scope="session")
async def test_send_message_malformed_auth(
    app_client, test_db, user_headers, dummy_request_data
):
    response = await app_client.post(
        "/messages",
        headers=user_headers["malformed"],
        data=json.dumps(dummy_request_data["new_message"]),
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to create a message with a user's JWT
@pytest.mark.asyncio(scope="session")
async def test_send_message_as_user(
    app_client,
    test_db,
    user_headers,
    dummy_users_data,
    dummy_request_data,
):
    message = dummy_request_data["new_message"]
    message["fromId"] = int(dummy_users_data["user"]["internal"])
    message["forId"] = dummy_users_data["moderator"]["internal"]
    response = await app_client.post(
        "/messages", headers=user_headers["user"], data=json.dumps(message)
    )
    response_data = await response.get_json()
    response_message = response_data["message"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_message["messageText"] == message["messageText"]


# Attempt to create a message from another user (with a user's JWT)
@pytest.mark.asyncio(scope="session")
async def test_send_message_from_another_user_as_user(
    app_client,
    test_db,
    user_headers,
    dummy_users_data,
    dummy_request_data,
):
    message = dummy_request_data["new_message"]
    message["fromId"] = int(dummy_users_data["admin"]["internal"])
    message["forId"] = dummy_users_data["moderator"]["internal"]
    response = await app_client.post(
        "/messages", headers=user_headers["user"], data=json.dumps(message)
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to create a message with a moderator's JWT
@pytest.mark.asyncio(scope="session")
async def test_send_message_as_mod(
    app_client,
    test_db,
    user_headers,
    dummy_users_data,
    dummy_request_data,
):
    message = dummy_request_data["new_message"]
    message["fromId"] = int(dummy_users_data["moderator"]["internal"])
    message["forId"] = dummy_users_data["admin"]["internal"]
    response = await app_client.post(
        "/messages", headers=user_headers["moderator"], data=json.dumps(message)
    )
    response_data = await response.get_json()
    response_message = response_data["message"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_message["messageText"] == message["messageText"]


# Attempt to create a message from another user (with a moderator's JWT)
@pytest.mark.asyncio(scope="session")
async def test_send_message_from_another_user_as_mod(
    app_client,
    test_db,
    user_headers,
    dummy_users_data,
    dummy_request_data,
):
    message = dummy_request_data["new_message"]
    message["fromId"] = int(dummy_users_data["admin"]["internal"])
    message["forId"] = dummy_users_data["user"]["internal"]
    response = await app_client.post(
        "/messages", headers=user_headers["moderator"], data=json.dumps(message)
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to create a message with an admin's JWT
@pytest.mark.asyncio(scope="session")
async def test_send_message_as_admin(
    app_client,
    test_db,
    user_headers,
    dummy_users_data,
    dummy_request_data,
):
    message = dummy_request_data["new_message"]
    message["fromId"] = int(dummy_users_data["admin"]["internal"])
    message["forId"] = dummy_users_data["moderator"]["internal"]
    response = await app_client.post(
        "/messages", headers=user_headers["admin"], data=json.dumps(message)
    )
    response_data = await response.get_json()
    response_message = response_data["message"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_message["messageText"] == message["messageText"]


# Attempt to create a message from another user (with an admin's JWT)
@pytest.mark.asyncio(scope="session")
async def test_send_message_from_another_user_as_admin(
    app_client,
    test_db,
    user_headers,
    dummy_users_data,
    dummy_request_data,
):
    message = dummy_request_data["new_message"]
    message["fromId"] = int(dummy_users_data["user"]["internal"])
    message["forId"] = dummy_users_data["moderator"]["internal"]
    response = await app_client.post(
        "/messages", headers=user_headers["admin"], data=json.dumps(message)
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to send a message from a user (when there's no thread)
@pytest.mark.asyncio(scope="session")
async def test_send_message_existing_thread_as_user(
    app_client,
    test_db,
    user_headers,
    dummy_users_data,
    dummy_request_data,
):
    message = dummy_request_data["new_message"]
    message["fromId"] = int(dummy_users_data["blocked"]["internal"])
    message["forId"] = dummy_users_data["admin"]["internal"]
    response = await app_client.post(
        "/messages", headers=user_headers["blocked"], data=json.dumps(message)
    )
    response_data = await response.get_json()
    response_message = response_data["message"]
    new_thread = await app_client.get(
        "/messages?userID=20&type=thread&threadID=7", headers=user_headers["blocked"]
    )
    new_thread_data = await new_thread.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_message["messageText"] == message["messageText"]
    assert response_message["threadID"] == 7
    assert len(new_thread_data["messages"]) == 2


@pytest.mark.asyncio(scope="session")
async def test_send_message_create_thread(
    app_client,
    test_db,
    user_headers,
    dummy_users_data,
    dummy_request_data,
):
    message = {**dummy_request_data["new_message"]}
    message["fromId"] = int(dummy_users_data["admin"]["internal"])
    message["forId"] = 9
    response = await app_client.post(
        "/messages", headers=user_headers["admin"], data=json.dumps(message)
    )
    response_data = await response.get_json()
    response_message = response_data["message"]
    new_thread = await app_client.get(
        f"/messages?userID={dummy_users_data['admin']['internal']}"
        "&type=thread&threadID=9",
        headers=user_headers["admin"],
    )
    new_thread_data = await new_thread.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_message["messageText"] == message["messageText"]
    assert response_message["threadID"] == 9
    assert len(new_thread_data["messages"]) == 1


# Delete Message Route Tests ('/message/<message_id>', DELETE)
# -------------------------------------------------------
# Attempt to delete a message with no authorisation header
@pytest.mark.asyncio(scope="session")
async def test_delete_message_no_auth(app_client, test_db, user_headers):
    response = await app_client.delete("/messages/inbox/1")
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to delete a message with a malformed auth header
@pytest.mark.asyncio(scope="session")
async def test_delete_message_malformed_auth(app_client, test_db, user_headers):
    response = await app_client.delete(
        "/messages/inbox/1", headers=user_headers["malformed"]
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to delete a message with a user's JWT
@pytest.mark.asyncio(scope="session")
async def test_delete_message_as_user(app_client, test_db, user_headers):
    response = await app_client.delete(
        "/messages/inbox/3", headers=user_headers["user"]
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == 3


# Attempt to delete another user's message (with a user's JWT)
@pytest.mark.asyncio(scope="session")
async def test_delete_message_from_another_user_as_user(
    app_client, test_db, user_headers
):
    response = await app_client.delete(
        "/messages/inbox/7", headers=user_headers["user"]
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to delete a thread with a user's JWT
@pytest.mark.asyncio(scope="session")
async def test_delete_thread_as_user(app_client, test_db, user_headers):
    response = await app_client.delete(
        "/messages/threads/2", headers=user_headers["user"]
    )
    response_data = await response.get_json()
    get_thread = await app_client.get(
        "/messages?userID=1&type=thread&threadID=2",
        headers=user_headers["user"],
    )
    thread_data = await get_thread.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == 2
    assert len(thread_data["messages"]) == 0


# Attempt to delete a message with a moderator's JWT
@pytest.mark.asyncio(scope="session")
async def test_delete_message_as_mod(app_client, test_db, user_headers):
    response = await app_client.delete(
        "/messages/inbox/5", headers=user_headers["moderator"]
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == 5


# Attempt to delete another user's message (with a moderator's JWT)
@pytest.mark.asyncio(scope="session")
async def test_delete_message_from_another_user_as_mod(
    app_client, test_db, user_headers
):
    response = await app_client.delete(
        "/messages/outbox/9", headers=user_headers["moderator"]
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to delete a message with an admin's JWT
@pytest.mark.asyncio(scope="session")
async def test_delete_message_as_admin(app_client, test_db, user_headers):
    response = await app_client.delete(
        "/messages/outbox/10", headers=user_headers["admin"]
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == 10


# Attempt to delete another user's message (with an admin's JWT)
@pytest.mark.asyncio(scope="session")
async def test_delete_message_from_another_user_as_admin(
    app_client, test_db, user_headers
):
    response = await app_client.delete(
        "/messages/outbox/3", headers=user_headers["admin"]
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to delete a user's message with no mailbox (with admin's JWT)
@pytest.mark.asyncio(scope="session")
async def test_delete_no_id_user_message_as_admin(app_client, test_db, user_headers):
    response = await app_client.delete("/messages/", headers=user_headers["admin"])
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to delete a nonexistent user's message (with admin's JWT)
@pytest.mark.asyncio(scope="session")
async def test_delete_nonexistent_user_message_as_admin(
    app_client, test_db, user_headers
):
    response = await app_client.delete(
        "/messages/inbox/100", headers=user_headers["admin"]
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to delete a message without ID
@pytest.mark.asyncio(scope="session")
async def test_delete_message_without_id_admin(app_client, test_db, user_headers):
    response = await app_client.delete(
        "/messages/inbox/", headers=user_headers["admin"]
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 404


# Empty Mailbox Tests ('/messages/<mailbox>', DELETE)
# -------------------------------------------------------
# Attempt to empty mailbox without auth header
@pytest.mark.asyncio(scope="session")
async def test_empty_mailbox_no_auth(app_client, test_db, user_headers):
    response = await app_client.delete("/messages/inbox?userID=4")
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to empty mailbox with malformed auth header
@pytest.mark.asyncio(scope="session")
async def test_empty_mailbox_malformed_auth(app_client, test_db, user_headers):
    response = await app_client.delete(
        "/messages/inbox?userID=4", headers=user_headers["malformed"]
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to empty user's inbox (user JWT)
@pytest.mark.asyncio(scope="session")
async def test_empty_mailbox_as_user(
    app_client, test_db, user_headers, dummy_users_data
):
    response = await app_client.delete(
        f"/messages/inbox?userID={dummy_users_data['user']['internal']}",
        headers=user_headers["user"],
    )
    response_data = await response.get_json()

    get_response = await app_client.get(
        f"/messages?type=inbox&userID={dummy_users_data['user']['internal']}",
        headers=user_headers["user"],
    )
    get_response_data = await get_response.get_json()
    print(get_response_data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == 7
    assert response_data["userID"] == 1
    assert len(get_response_data["messages"]) == 0


# Attempt to empty another user's inbox (user JWT)
@pytest.mark.asyncio(scope="session")
async def test_empty_other_users_mailbox_as_user(app_client, test_db, user_headers):
    response = await app_client.delete(
        "/messages/inbox?userID=4", headers=user_headers["user"]
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to empty user's outbox (moderator's JWT)
@pytest.mark.asyncio(scope="session")
async def test_empty_mailbox_as_mod(
    app_client, test_db, user_headers, dummy_users_data
):
    response = await app_client.delete(
        f"/messages/outbox?userID={dummy_users_data['moderator']['internal']}",
        headers=user_headers["moderator"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == 2
    assert response_data["userID"] == 5


# Attempt to empty another user's outbox (moderator's JWT)
@pytest.mark.asyncio(scope="session")
async def test_empty_other_users_mailbox_as_mod(app_client, test_db, user_headers):
    response = await app_client.delete(
        "/messages/outbox?userID=1", headers=user_headers["moderator"]
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to empty user's threads mailbox (admin's JWT)
@pytest.mark.asyncio(scope="session")
async def test_empty_mailbox_as_admin(
    app_client, test_db, user_headers, dummy_users_data
):
    response = await app_client.delete(
        f"/messages/threads?userID={dummy_users_data['admin']['internal']}",
        headers=user_headers["admin"],
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == 2
    assert response_data["userID"] == 4


# Attempt to empty another user's threads mailbox (admin's JWT)
@pytest.mark.asyncio(scope="session")
async def test_empty_other_users_mailbox_as_admin(app_client, test_db, user_headers):
    response = await app_client.delete(
        "/messages/threads?userID=5", headers=user_headers["admin"]
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to empty user mailbox without user type
@pytest.mark.asyncio(scope="session")
async def test_empty_mailbox_type_as_admin(app_client, test_db, user_headers):
    response = await app_client.delete("/messages/", headers=user_headers["admin"])
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to empty user mailbox without user ID
@pytest.mark.asyncio(scope="session")
async def test_empty_mailbox_id_as_admin(app_client, test_db, user_headers):
    response = await app_client.delete(
        "/messages/threads?userID=", headers=user_headers["admin"]
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 400
