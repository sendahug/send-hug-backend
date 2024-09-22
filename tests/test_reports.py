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


# Get Open Reports Tests ('/reports', GET)
# -------------------------------------------------------
# Attempt to get open reports without auth header
@pytest.mark.asyncio(loop_scope="session")
async def test_get_open_reports_no_auth(app_client, test_db, user_headers):
    response = await app_client.get("/reports")
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get open reports with malformed auth header
@pytest.mark.asyncio(loop_scope="session")
async def test_get_open_reports_malformed_auth(app_client, test_db, user_headers):
    response = await app_client.get("/reports", headers=user_headers["malformed"])
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get open reports with a user's JWT
@pytest.mark.asyncio(loop_scope="session")
async def test_get_open_reports_as_user(app_client, test_db, user_headers):
    response = await app_client.get("/reports", headers=user_headers["user"])
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 403


#  Attempt to get open reports with a moderator's JWT
@pytest.mark.asyncio(loop_scope="session")
async def test_get_open_reports_as_mod(app_client, test_db, user_headers):
    response = await app_client.get("/reports", headers=user_headers["moderator"])
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to get open reports with an admin's JWT
@pytest.mark.asyncio(loop_scope="session")
async def test_get_open_reports_as_admin(app_client, test_db, user_headers):
    response = await app_client.get("/reports", headers=user_headers["admin"])
    response_data = await response.get_json()

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["totalUserPages"] == 0
    assert response_data["totalPostPages"] == 0
    assert len(response_data["userReports"]) == 0
    assert len(response_data["postReports"]) == 0


# Create Report Route Tests ('/reports', POST)
# -------------------------------------------------------
# Attempt to create a report with no authorisation header
@pytest.mark.asyncio(loop_scope="session")
async def test_send_report_no_auth(
    app_client, test_db, user_headers, dummy_request_data
):
    response = await app_client.post(
        "/reports", data=json.dumps(dummy_request_data["new_report"])
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to create a report with a malformed auth header
@pytest.mark.asyncio(loop_scope="session")
async def test_send_report_malformed_auth(
    app_client, test_db, user_headers, dummy_request_data
):
    response = await app_client.post(
        "/reports",
        headers=user_headers["malformed"],
        data=json.dumps(dummy_request_data["new_report"]),
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to create a report with a user's JWT
@pytest.mark.asyncio(loop_scope="session")
async def test_send_report_as_user(
    app_client,
    test_db,
    user_headers,
    dummy_request_data,
    dummy_users_data,
):
    report = dummy_request_data["new_report"]
    report["userID"] = 4
    report["postID"] = 25
    report["reporter"] = dummy_users_data["user"]["internal"]
    response = await app_client.post(
        "/reports", headers=user_headers["user"], data=json.dumps(report)
    )
    response_data = await response.get_json()
    response_report = response_data["report"]

    assert response_data["success"] is True
    assert response_report["closed"] is False
    assert response.status_code == 200
    assert response_report["postID"] == report["postID"]


# Attempt to create a report with a moderator's JWT
@pytest.mark.asyncio(loop_scope="session")
async def test_send_report_as_mod(
    app_client,
    test_db,
    user_headers,
    dummy_request_data,
    dummy_users_data,
):
    report = dummy_request_data["new_report"]
    report["userID"] = 4
    report["postID"] = 25
    report["reporter"] = dummy_users_data["moderator"]["internal"]
    response = await app_client.post(
        "/reports", headers=user_headers["moderator"], data=json.dumps(report)
    )
    response_data = await response.get_json()
    response_report = response_data["report"]

    assert response_data["success"] is True
    assert response_report["closed"] is False
    assert response.status_code == 200
    assert response_report["postID"] == report["postID"]


# Attempt to create a report with an admin's JWT
@pytest.mark.asyncio(loop_scope="session")
async def test_send_report_as_admin(
    app_client,
    test_db,
    user_headers,
    dummy_request_data,
    dummy_users_data,
):
    report = dummy_request_data["new_report"]
    report["userID"] = 4
    report["postID"] = 25
    report["reporter"] = dummy_users_data["admin"]["internal"]
    response = await app_client.post(
        "/reports", headers=user_headers["admin"], data=json.dumps(report)
    )
    response_data = await response.get_json()
    response_report = response_data["report"]

    assert response_data["success"] is True
    assert response_report["closed"] is False
    assert response.status_code == 200
    assert response_report["postID"] == report["postID"]


# Attempt to create a post report without post ID with an admin's JWT
@pytest.mark.asyncio(loop_scope="session")
async def test_send_malformed_report_as_admin(
    app_client,
    test_db,
    user_headers,
    dummy_request_data,
    dummy_users_data,
):
    report = dummy_request_data["new_report"]
    report["userID"] = 4
    report["postID"] = None
    report["reporter"] = dummy_users_data["admin"]["internal"]
    response = await app_client.post(
        "/reports", headers=user_headers["admin"], data=json.dumps(report)
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 422


# Attempt to create a message from another user - validate
# that it sets the user ID based on the JWT
@pytest.mark.asyncio(loop_scope="session")
async def test_send_report_as_another_user(
    app_client,
    test_db,
    user_headers,
    dummy_request_data,
    dummy_users_data,
):
    report = dummy_request_data["new_report"]
    report["userID"] = 4
    report["postID"] = 25
    report["reporter"] = dummy_users_data["user"]["internal"]
    response = await app_client.post(
        "/reports", headers=user_headers["admin"], data=json.dumps(report)
    )
    response_data = await response.get_json()
    response_report = response_data["report"]

    assert response_report["reporter"] != int(report["reporter"])
    assert response_report["reporter"] == int(dummy_users_data["admin"]["internal"])


# Attempt to create a post report for post that doesn't exist
@pytest.mark.asyncio(loop_scope="session")
async def test_send_report_nonexistent_post_as_admin(
    app_client,
    test_db,
    user_headers,
    dummy_request_data,
    dummy_users_data,
):
    report = dummy_request_data["new_report"]
    report["userID"] = 4
    report["postID"] = 1000
    report["reporter"] = dummy_users_data["admin"]["internal"]
    response = await app_client.post(
        "/reports", headers=user_headers["admin"], data=json.dumps(report)
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to create a report with an admin's JWT
@pytest.mark.asyncio(loop_scope="session")
async def test_send_user_report_as_admin(
    app_client,
    test_db,
    user_headers,
    dummy_request_data,
    dummy_users_data,
):
    report = dummy_request_data["new_user_report"]
    report["userID"] = 1
    report["reporter"] = dummy_users_data["admin"]["internal"]
    response = await app_client.post(
        "/reports", headers=user_headers["admin"], data=json.dumps(report)
    )
    response_data = await response.get_json()
    response_report = response_data["report"]

    assert response_data["success"] is True
    assert response_report["closed"] is False
    assert response.status_code == 200
    assert response_report["userID"] == report["userID"]


# Attempt to create a report for user that doesn't exist
@pytest.mark.asyncio(loop_scope="session")
async def test_send_user_report_nonexistent_user_as_admin(
    app_client,
    test_db,
    user_headers,
    dummy_request_data,
    dummy_users_data,
):
    report = dummy_request_data["new_user_report"]
    report["userID"] = 100
    report["reporter"] = dummy_users_data["admin"]["internal"]
    response = await app_client.post(
        "/reports", headers=user_headers["admin"], data=json.dumps(report)
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 404


# Update Report Route Tests ('/reports/<report_id>', PATCH)
# -------------------------------------------------------
# Attempt to update a report with no authorisation header
@pytest.mark.asyncio(loop_scope="session")
async def test_update_report_no_auth(
    app_client, test_db, user_headers, dummy_request_data
):
    response = await app_client.patch(
        "/reports/36", data=json.dumps(dummy_request_data["new_report"])
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to update a report with a malformed auth header
@pytest.mark.asyncio(loop_scope="session")
async def test_update_report_malformed_auth(
    app_client, test_db, user_headers, dummy_request_data
):
    response = await app_client.patch(
        "/reports/36",
        headers=user_headers["malformed"],
        data=json.dumps(dummy_request_data["new_report"]),
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to update a report (with user's JWT)
@pytest.mark.asyncio(loop_scope="session")
async def test_update_report_as_user(
    app_client,
    test_db,
    user_headers,
    dummy_request_data,
    dummy_users_data,
):
    report = dummy_request_data["new_report"]
    report["userID"] = 4
    report["postID"] = 25
    report["reporter"] = dummy_users_data["user"]["internal"]
    response = await app_client.patch(
        "/reports/36", headers=user_headers["user"], data=json.dumps(report)
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to update a report (with moderator's JWT)
@pytest.mark.asyncio(loop_scope="session")
async def test_update_report_as_mod(
    app_client,
    test_db,
    user_headers,
    dummy_request_data,
    dummy_users_data,
):
    report = dummy_request_data["new_report"]
    report["userID"] = 4
    report["postID"] = 25
    report["reporter"] = dummy_users_data["moderator"]["internal"]
    response = await app_client.patch(
        "/reports/36", headers=user_headers["moderator"], data=json.dumps(report)
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to update a report (with admin's JWT)
@pytest.mark.asyncio(loop_scope="session")
async def test_update_report_as_admin(
    app_client,
    test_db,
    user_headers,
    dummy_request_data,
    dummy_users_data,
):
    report = dummy_request_data["new_report"]
    report["id"] = 36
    report["userID"] = 4
    report["postID"] = 25
    report["reporter"] = dummy_users_data["admin"]["internal"]
    report["dismissed"] = False
    report["closed"] = False
    response = await app_client.patch(
        "/reports/36", headers=user_headers["admin"], data=json.dumps(report)
    )
    response_data = await response.get_json()
    report_text = response_data["updated"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert report_text["id"] == report["id"]


# Attempt to update a report (with admin's JWT)
@pytest.mark.asyncio(loop_scope="session")
async def test_update_user_report_as_admin(
    app_client,
    test_db,
    user_headers,
    dummy_request_data,
    dummy_users_data,
):
    report = dummy_request_data["new_user_report"]
    report["id"] = 35
    report["userID"] = 5
    report["reporter"] = dummy_users_data["admin"]["internal"]
    report["dismissed"] = False
    report["closed"] = False
    response = await app_client.patch(
        "/reports/35", headers=user_headers["admin"], data=json.dumps(report)
    )
    response_data = await response.get_json()
    report_text = response_data["updated"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert report_text["id"] == report["id"]
    assert report_text["userID"] == report["userID"]


# Attempt to update a report with no ID (with admin's JWT)
@pytest.mark.asyncio(loop_scope="session")
async def test_update_no_id_report_as_admin(
    app_client,
    test_db,
    user_headers,
    dummy_request_data,
    dummy_users_data,
):
    report = dummy_request_data["new_report"]
    report["id"] = 36
    report["userID"] = 4
    report["postID"] = 25
    report["reporter"] = dummy_users_data["admin"]["internal"]
    report["dismissed"] = False
    report["closed"] = False
    response = await app_client.patch(
        "/reports/", headers=user_headers["admin"], data=json.dumps(report)
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to update a report that doesn't exist (with admin's JWT)
@pytest.mark.asyncio(loop_scope="session")
async def test_update_nonexistent_report_as_admin(
    app_client,
    test_db,
    user_headers,
    dummy_request_data,
    dummy_users_data,
):
    report = dummy_request_data["new_report"]
    report["id"] = 36
    report["userID"] = 4
    report["postID"] = 25
    report["reporter"] = dummy_users_data["admin"]["internal"]
    report["dismissed"] = False
    report["closed"] = False
    response = await app_client.patch(
        "/reports/100", headers=user_headers["admin"], data=json.dumps(report)
    )
    response_data = await response.get_json()

    assert response_data["success"] is False
    assert response.status_code == 404
