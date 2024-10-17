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


# Get Users by Type Tests ('/users/<type>', GET)
# -------------------------------------------------------
# Attempt to get list of users without auth header
@pytest.mark.asyncio(scope="session")
async def test_get_user_list_no_auth(app_client, test_db, user_headers, mocker):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.get("/users/blocked")
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get list of users with
@pytest.mark.parametrize(
    "user, error_code",
    [
        # malformed auth header
        ("malformed", 401),
        # user's auth header
        ("user", 403),
        # moderator's auth header
        ("moderator", 403),
    ],
)
@pytest.mark.asyncio(scope="session")
async def test_get_user_list_auth_error(
    app_client, test_db, user_headers, user, error_code, mocker
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.get("/users/blocked", headers=user_headers[user])
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == error_code


# Attempt to get list of users with admin's auth header
@pytest.mark.asyncio(scope="session")
async def test_get_user_list_as_admin(app_client, test_db, user_headers, mocker):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.get("/users/blocked", headers=user_headers["admin"])
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["total_pages"] == 1


# Attempt to get list of users with admin's auth header
@pytest.mark.asyncio(scope="session")
async def test_get_user_list_unsupported_type(
    app_client, test_db, user_headers, mocker
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.get("/users/meow", headers=user_headers["admin"])
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 500


# Get User Data Tests ('/users/all/<user_id>', GET)
# -------------------------------------------------------
# Attempt to get a user's data without auth header
@pytest.mark.asyncio(scope="session")
async def test_get_user_data_no_auth(app_client, test_db, user_headers, mocker):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.get("/users/all/1")
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get a user's data with malformed auth header
@pytest.mark.asyncio(scope="session")
async def test_get_user_data_malformed_auth(app_client, test_db, user_headers, mocker):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.get("/users/all/1", headers=user_headers["malformed"])
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get a user's data with a user's JWT
@pytest.mark.asyncio(scope="session")
async def test_get_user_data_as_user(
    app_client, test_db, user_headers, dummy_users_data, mocker
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.get(
        f"/users/all/{dummy_users_data['user']['firebase_id']}",
        headers=user_headers["user"],
    )
    response_data = await response.get_json()
    user_data = response_data["user"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert user_data["id"] == int(dummy_users_data["user"]["internal"])


# Attempt to get a user's data with a moderator's JWT
@pytest.mark.asyncio(scope="session")
async def test_get_user_data_as_mod(
    app_client, test_db, user_headers, dummy_users_data, mocker
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.get(
        f"/users/all/{dummy_users_data['moderator']['firebase_id']}",
        headers=user_headers["moderator"],
    )
    response_data = await response.get_json()
    user_data = response_data["user"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert user_data["id"] == int(dummy_users_data["moderator"]["internal"])


# Attempt to get a user's data with an admin's JWT
@pytest.mark.asyncio(scope="session")
async def test_get_user_data_as_admin(
    app_client, test_db, user_headers, dummy_users_data, mocker
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.get(
        f"/users/all/{dummy_users_data['admin']['firebase_id']}",
        headers=user_headers["admin"],
    )
    response_data = await response.get_json()
    user_data = response_data["user"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert user_data["id"] == int(dummy_users_data["admin"]["internal"])


# Attempt to get a nonexistent user's data (with admin's JWT)
@pytest.mark.asyncio(scope="session")
async def test_get_nonexistent_user_as_admin(app_client, test_db, user_headers, mocker):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.get("/users/all/100", headers=user_headers["admin"])
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to get a user's data with no ID (with admin's JWT)
@pytest.mark.asyncio(scope="session")
async def test_get_user_no_id_as_admin(app_client, test_db, user_headers, mocker):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.get("/users/all/", headers=user_headers["admin"])
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 404


# Create User Tests ('/users', POST)
# -------------------------------------------------------
# Attempt to create a user without auth header
@pytest.mark.asyncio(scope="session")
async def test_create_user_no_auth(
    app_client, test_db, user_headers, dummy_request_data, mocker
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.post(
        "/users", data=json.dumps(dummy_request_data["new_user"])
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to create a user with malformed auth header
@pytest.mark.asyncio(scope="session")
async def test_create_user_malformed_auth(
    app_client, test_db, user_headers, dummy_request_data, mocker
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.post(
        "/users",
        headers=user_headers["malformed"],
        data=json.dumps(dummy_request_data["new_user"]),
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to create a user with user's JWT
@pytest.mark.asyncio(scope="session")
async def test_create_user_as_user(
    app_client, test_db, user_headers, dummy_request_data, mocker
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.post(
        "/users",
        headers=user_headers["user"],
        data=json.dumps(dummy_request_data["new_user"]),
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 422


# Attempt to create a user with moderator's JWT
@pytest.mark.asyncio(scope="session")
async def test_create_user_as_moderator(
    app_client, test_db, user_headers, dummy_request_data, mocker
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.post(
        "/users",
        headers=user_headers["moderator"],
        data=json.dumps(dummy_request_data["new_user"]),
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 422


# Attempt to create a user with admin's JWT
@pytest.mark.asyncio(scope="session")
async def test_create_user_as_damin(
    app_client, test_db, user_headers, dummy_request_data, mocker
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.post(
        "/users",
        headers=user_headers["admin"],
        data=json.dumps(dummy_request_data["new_user"]),
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 422


# Attempt to create a user with new user's JWT
# This test is performed as fallback; since the new user -> user change
# is done automatically, it's no longer needed, but in case of an error
# adjusting a user's roles, it's important to make sure they still
# can't create other users
@pytest.mark.asyncio(scope="session")
async def test_create_different_user_as_new_user(
    app_client, test_db, user_headers, dummy_request_data, mocker
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    user_to_create = {**dummy_request_data["new_user"]}
    user_to_create["firebaseId"] = "twg"
    response = await app_client.post(
        "/users",
        headers=user_headers["blocked"],
        data=json.dumps(user_to_create),
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 409


# Edit User Data Tests ('/users/all/<user_id>', PATCH)
# -------------------------------------------------------
# Attempt to update a user's data without auth header
@pytest.mark.asyncio(scope="session")
async def test_update_user_no_auth(
    app_client, test_db, user_headers, dummy_request_data, mocker
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.patch(
        "/users/all/1", data=json.dumps(dummy_request_data["updated_user"])
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to update a user's data with malformed auth header
@pytest.mark.asyncio(scope="session")
async def test_update_user_malformed_auth(
    app_client, test_db, user_headers, dummy_request_data, mocker
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.patch(
        "/users/all/1",
        headers=user_headers["malformed"],
        data=json.dumps(dummy_request_data["updated_user"]),
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to update a user's data with a user's JWT
@pytest.mark.asyncio(scope="session")
async def test_update_user_as_user(
    app_client,
    test_db,
    user_headers,
    dummy_users_data,
    dummy_request_data,
    mocker,
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    user = dummy_request_data["updated_user"]
    user["id"] = dummy_users_data["user"]["internal"]
    user["displayName"] = "user123"
    response = await app_client.patch(
        f"/users/all/{dummy_users_data['user']['internal']}",
        headers=user_headers["user"],
        data=json.dumps(user),
    )
    response_data = await response.get_json()
    updated = response_data["updated"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert updated["displayName"] == user["displayName"]


# Attempt to update another user's display name with a user's JWT
@pytest.mark.asyncio(scope="session")
async def test_update_other_users_display_name_as_user(
    app_client,
    test_db,
    user_headers,
    dummy_users_data,
    dummy_request_data,
    mocker,
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    user = dummy_request_data["updated_display"]
    user["id"] = dummy_users_data["moderator"]["internal"]
    response = await app_client.patch(
        f"/users/all/{dummy_users_data['moderator']['internal']}",
        headers=user_headers["user"],
        data=json.dumps(user),
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to update a user's blocked state with a user's JWT
@pytest.mark.asyncio(scope="session")
async def test_update_block_user_as_user(
    app_client,
    test_db,
    user_headers,
    dummy_users_data,
    dummy_request_data,
    mocker,
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    user = dummy_request_data["updated_unblock_user"]
    user["id"] = dummy_users_data["user"]["internal"]
    user["blocked"] = True
    response = await app_client.patch(
        f"/users/all/{dummy_users_data['user']['internal']}",
        headers=user_headers["user"],
        data=json.dumps(user),
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to update a user's data with a moderator's JWT
@pytest.mark.asyncio(scope="session")
async def test_update_user_as_mod(
    app_client,
    test_db,
    user_headers,
    dummy_users_data,
    dummy_request_data,
    mocker,
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    user = dummy_request_data["updated_user"]
    user["id"] = dummy_users_data["moderator"]["internal"]
    user["displayName"] = "mod"
    response = await app_client.patch(
        f"/users/all/{dummy_users_data['moderator']['internal']}",
        headers=user_headers["moderator"],
        data=json.dumps(user),
    )
    response_data = await response.get_json()
    updated = response_data["updated"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert updated["displayName"] == user["displayName"]


# Attempt to update another user's display name with a moderator's JWT
@pytest.mark.asyncio(scope="session")
async def test_update_other_users_display_name_as_mod(
    app_client,
    test_db,
    user_headers,
    dummy_users_data,
    dummy_request_data,
    mocker,
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    user = dummy_request_data["updated_display"]
    user["id"] = dummy_users_data["admin"]["internal"]
    response = await app_client.patch(
        f"/users/all/{dummy_users_data['admin']['internal']}",
        headers=user_headers["moderator"],
        data=json.dumps(user),
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to update a user's blocked state with a moderator's JWT
@pytest.mark.asyncio(scope="session")
async def test_update_block_user_as_mod(
    app_client,
    test_db,
    user_headers,
    dummy_users_data,
    dummy_request_data,
    mocker,
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    user = dummy_request_data["updated_unblock_user"]
    user["id"] = dummy_users_data["moderator"]["internal"]
    user["blocked"] = True
    response = await app_client.patch(
        f"/users/all/{dummy_users_data['moderator']['internal']}",
        headers=user_headers["moderator"],
        data=json.dumps(user),
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to update a user's data with an admin's JWT
@pytest.mark.asyncio(scope="session")
async def test_update_user_as_admin(
    app_client,
    test_db,
    user_headers,
    dummy_users_data,
    dummy_request_data,
    mocker,
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    user = dummy_request_data["updated_user"]
    user["id"] = dummy_users_data["admin"]["internal"]
    user["displayName"] = "admin123"
    response = await app_client.patch(
        f"/users/all/{dummy_users_data['admin']['internal']}",
        headers=user_headers["admin"],
        data=json.dumps(user),
    )
    response_data = await response.get_json()
    updated = response_data["updated"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert updated["displayName"] == user["displayName"]


# Attempt to update another user's display name with an admin's JWT
@pytest.mark.asyncio(scope="session")
async def test_update_other_user_as_admin(
    app_client,
    test_db,
    user_headers,
    dummy_users_data,
    dummy_request_data,
    mocker,
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    user = dummy_request_data["updated_display"]
    user["id"] = dummy_users_data["user"]["internal"]
    user["displayName"] = "hello"
    response = await app_client.patch(
        f"/users/all/{dummy_users_data['user']['internal']}",
        headers=user_headers["admin"],
        data=json.dumps(user),
    )
    response_data = await response.get_json()
    updated = response_data["updated"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert updated["displayName"] == user["displayName"]


# Attempt to update a user's blocked state with an admin's JWT
@pytest.mark.asyncio(scope="session")
async def test_update_block_user_as_admin(
    app_client,
    test_db,
    user_headers,
    dummy_users_data,
    dummy_request_data,
    mocker,
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    user = dummy_request_data["updated_unblock_user"]
    user["id"] = dummy_users_data["user"]["internal"]
    response = await app_client.patch(
        f"/users/all/{dummy_users_data['user']['internal']}",
        headers=user_headers["admin"],
        data=json.dumps(user),
    )
    response_data = await response.get_json()
    updated = response_data["updated"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert updated["id"] == int(dummy_users_data["user"]["internal"])


# Attempt to update another user's settings (admin's JWT)
@pytest.mark.asyncio(scope="session")
async def test_update_user_settings_as_admin(
    app_client,
    test_db,
    user_headers,
    dummy_users_data,
    dummy_request_data,
    mocker,
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    user = dummy_request_data["updated_unblock_user"]
    user["id"] = dummy_users_data["user"]["internal"]
    user["autoRefresh"] = True
    user["pushEnabled"] = True
    response = await app_client.patch(
        f"/users/all/{dummy_users_data['user']['internal']}",
        headers=user_headers["admin"],
        data=json.dumps(user),
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to update a user's data with no ID (with admin's JWT)
@pytest.mark.asyncio(scope="session")
async def test_update_no_id_user_as_admin(
    app_client, test_db, user_headers, dummy_request_data, mocker
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.patch(
        "/users/all/",
        headers=user_headers["admin"],
        data=json.dumps(dummy_request_data["updated_user"]),
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to update another user's settings (admin's JWT)
@pytest.mark.asyncio(scope="session")
async def test_update_admin_settings_as_admin(
    app_client,
    test_db,
    user_headers,
    dummy_users_data,
    dummy_request_data,
    mocker,
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    user = {**dummy_request_data["updated_unblock_user"]}
    user["id"] = dummy_users_data["admin"]["internal"]
    user["autoRefresh"] = True
    user["pushEnabled"] = True
    user["refreshRate"] = 60
    response = await app_client.patch(
        f"/users/all/{dummy_users_data['admin']['internal']}",
        headers=user_headers["admin"],
        data=json.dumps(user),
    )
    response_data = await response.get_json()
    updated = response_data["updated"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert updated["autoRefresh"] is True
    assert updated["pushEnabled"] is True
    assert updated["refreshRate"] == 60


# Attempt to update another user's settings (admin's JWT) - 0 refresh rate
@pytest.mark.asyncio(scope="session")
async def test_update_admin_settings_as_admin_invalid_settings(
    app_client,
    test_db,
    user_headers,
    dummy_users_data,
    dummy_request_data,
    mocker,
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    user = {**dummy_request_data["updated_unblock_user"]}
    user["id"] = dummy_users_data["admin"]["internal"]
    user["autoRefresh"] = True
    user["pushEnabled"] = True
    user["refreshRate"] = 0
    response = await app_client.patch(
        f"/users/all/{dummy_users_data['admin']['internal']}",
        headers=user_headers["admin"],
        data=json.dumps(user),
    )
    response_data = await response.get_json()

    get_response = await app_client.get(
        f"/users/all/{dummy_users_data['admin']['internal']}",
        headers=user_headers["admin"],
    )
    get_response_data = await get_response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 422
    assert get_response_data["user"]["refreshRate"] == 20


# Get User's Posts Tests ('/users/all/<user_id>/posts', GET)
# -------------------------------------------------------
# Attempt to get a user's posts without auth header
@pytest.mark.asyncio(scope="session")
async def test_get_user_posts_no_auth(app_client, test_db, user_headers, mocker):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.get("/users/all/1/posts")
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get a user's posts with malformed auth header
@pytest.mark.asyncio(scope="session")
async def test_get_user_posts_malformed_auth(app_client, test_db, user_headers, mocker):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.get(
        "/users/all/1/posts", headers=user_headers["malformed"]
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get a user's posts with
@pytest.mark.parametrize(
    "user_id, user, total_pages, posts_num",
    [
        # a user's JWT
        (1, "user", 2, 5),
        # a moderator's JWT
        (4, "moderator", 3, 5),
        # an admin's JWT
        (5, "admin", 1, 2),
    ],
)
@pytest.mark.asyncio(scope="session")
async def test_get_user_posts(
    app_client,
    test_db,
    user_headers,
    user_id,
    user,
    total_pages,
    posts_num,
    mocker,
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.get(
        f"/users/all/{user_id}/posts", headers=user_headers[user]
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["page"] == 1
    assert response_data["total_pages"] == total_pages
    assert len(response_data["posts"]) == posts_num


# Delete User's Posts Route Tests ('/users/all/<user_id>/posts', DELETE)
# -------------------------------------------------------
# Attempt to delete user's posts with no authorisation header
@pytest.mark.asyncio(scope="session")
async def test_delete_posts_no_auth(app_client, test_db, user_headers, mocker):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.delete("/users/all/1/posts")
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to delete user's with a malformed auth header
@pytest.mark.asyncio(scope="session")
async def test_delete_posts_malformed_auth(app_client, test_db, user_headers, mocker):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.delete(
        "/users/all/1/posts", headers=user_headers["malformed"]
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to delete the user's posts
@pytest.mark.parametrize(
    "user_id, user, deleted_post",
    [
        # (with same user's JWT)
        (1, "user", 8),
        # (with same moderator's JWT)
        (5, "moderator", 2),
        # (with same admin's JWT)
        (4, "admin", 14),
    ],
)
@pytest.mark.asyncio(scope="session")
async def test_delete_own_posts(
    app_client, test_db, user_headers, user_id, user, deleted_post, mocker
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.delete(
        f"/users/all/{user_id}/posts", headers=user_headers[user]
    )
    response_data = await response.get_json()

    get_response = await app_client.get(
        f"/users/all/{user_id}/posts", headers=user_headers[user]
    )
    get_response_data = await get_response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == deleted_post
    assert len(get_response_data["posts"]) == 0


# Attempt to delete another user's posts without permission
@pytest.mark.parametrize(
    "user_id, user",
    [
        # (with user's JWT)
        (4, "user"),
        # (with moderator's JWT)
        (1, "moderator"),
    ],
)
@pytest.mark.asyncio(scope="session")
async def test_delete_other_users_posts_no_permission(
    app_client, test_db, user_headers, user_id, user, mocker
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.delete(
        f"/users/all/{user_id}/posts", headers=user_headers[user]
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to delete another user's posts (with admin's JWT)
@pytest.mark.asyncio(scope="session")
async def test_delete_other_users_posts_as_admin(
    app_client, test_db, user_headers, mocker
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.delete(
        "/users/all/5/posts", headers=user_headers["admin"]
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == 2


# Attempt to delete the posts of a user that doesn't exist (admin's JWT)
@pytest.mark.asyncio(scope="session")
async def test_delete_nonexistent_users_posts_as_admin(
    app_client, test_db, user_headers, mocker
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.delete(
        "/users/all/100/posts", headers=user_headers["admin"]
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to delete the posts of a user that has no posts (admin's JWT)
@pytest.mark.asyncio(scope="session")
async def test_delete_nonexistent_posts_as_admin(
    app_client, test_db, user_headers, mocker
):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.delete(
        "/users/all/9/posts", headers=user_headers["admin"]
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 404


# Send a Hug for user Tests ('/users/all/<user_id>/hugs', POST)
# -------------------------------------------------------
# Attempt to send hugs for a post that doesn't exist
@pytest.mark.asyncio(scope="session")
async def test_user_hugs_post_no_existing(app_client, test_db, user_headers, mocker):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.post(
        "/users/all/1000/hugs", headers=user_headers["admin"]
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to send hugs
@pytest.mark.asyncio(scope="session")
async def test_user_hugs(app_client, test_db, user_headers, mocker):
    mocker.patch(
        "controllers.users.sah_config.db.session", new_callable=test_db.session
    )

    response = await app_client.post(
        "/users/all/1/hugs", headers=user_headers["moderator"]
    )
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["updated"] == "Successfully sent hug to shirb"
