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


# Get Filters Tests ('/filters', GET)
# -------------------------------------------------------
# Attempt to get filters without auth header
@pytest.mark.asyncio(scope="session")
async def test_get_filters_no_auth(app_client, test_db, mock_verify_id_token):
    response = await app_client.get("/filters")
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get filters without permission
@pytest.mark.parametrize(
    "user, status_code",
    [
        # malformed auth header
        ("malformed", 401),
        # a user's JWT
        ("user", 403),
        # a moderator's JWT
        ("moderator", 403),
    ],
)
@pytest.mark.asyncio(scope="session")
async def test_get_filters_auth_error(
    app_client, test_db, user_headers, user, status_code, mock_verify_id_token
):
    response = await app_client.get("/filters", headers=user_headers[user])
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == status_code


# Attempt to get filters with an admin's JWT
@pytest.mark.asyncio(scope="session")
async def test_get_filters_as_admin(
    app_client, test_db, user_headers, mock_verify_id_token
):
    response = await app_client.get("/filters", headers=user_headers["admin"])
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["total_pages"] == 1
    assert len(response_data["words"]) == 2


# Create Filters Tests ('/filters', POST)
# -------------------------------------------------------
# Attempt to create a filter without auth header
@pytest.mark.asyncio(scope="session")
async def test_create_filters_no_auth(
    app_client, test_db, user_headers, mock_verify_id_token
):
    response = await app_client.post("/filters", data=json.dumps({"word": "sample"}))
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get filters without permission
@pytest.mark.parametrize(
    "user, status_code",
    [
        # malformed auth header
        ("malformed", 401),
        # a user's JWT
        ("user", 403),
        # a moderator's JWT
        ("moderator", 403),
    ],
)
@pytest.mark.asyncio(scope="session")
async def test_create_filters_auth_error(
    app_client, test_db, user_headers, user, status_code, mock_verify_id_token
):
    response = await app_client.post(
        "/filters",
        headers=user_headers[user],
        data=json.dumps({"word": "sample"}),
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == status_code


# Attempt to create a filter with an admin's JWT
@pytest.mark.asyncio(scope="session")
async def test_create_filters_as_admin(
    app_client, test_db, user_headers, mock_verify_id_token
):
    response = await app_client.post(
        "/filters", headers=user_headers["admin"], data=json.dumps({"word": "sample"})
    )
    response_data = await response.get_json()
    added_word = response_data["added"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert added_word["filter"] == "sample"


# Attempt to create a filter with an admin's JWT
@pytest.mark.asyncio(scope="session")
async def test_create_duplicate_filters_as_admin(
    app_client, test_db, user_headers, mock_verify_id_token
):
    filter = {"word": "sample"}
    await app_client.post(
        "/filters", headers=user_headers["admin"], data=json.dumps(filter)
    )
    response = await app_client.post(
        "/filters", headers=user_headers["admin"], data=json.dumps(filter)
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 409


# Delete Filters Tests ('/filters/<id>', DELETE)
# -------------------------------------------------------
# Attempt to delete a filter without auth header
@pytest.mark.asyncio(scope="session")
async def test_delete_filters_no_auth(
    app_client, test_db, user_headers, mock_verify_id_token
):
    response = await app_client.delete("/filters/1")
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get filters without permission
@pytest.mark.parametrize(
    "user, status_code",
    [
        # malformed auth header
        ("malformed", 401),
        # a user's JWT
        ("user", 403),
        # a moderator's JWT
        ("moderator", 403),
    ],
)
@pytest.mark.asyncio(scope="session")
async def test_delete_filters_auth_error(
    app_client, test_db, user_headers, user, status_code, mock_verify_id_token
):
    response = await app_client.delete("/filters/1", headers=user_headers[user])
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == status_code


# Attempt to delete a filter with an admin's JWT
@pytest.mark.asyncio(scope="session")
async def test_delete_filters_as_admin(
    app_client, test_db, user_headers, mock_verify_id_token
):
    # Delete the filter
    response = await app_client.delete("/filters/2", headers=user_headers["admin"])
    response_data = await response.get_json()
    deleted = response_data["deleted"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert deleted["filter"] == "filtered_word_2"


# Attempt to delete a filter that doesn't exist with an admin's JWT
@pytest.mark.asyncio(scope="session")
async def test_delete_nonexistent_filters_as_admin(
    app_client, test_db, user_headers, mock_verify_id_token
):
    response = await app_client.delete("/filters/100", headers=user_headers["admin"])
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 404
