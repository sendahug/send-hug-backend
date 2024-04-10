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


# Create Post Route Tests ('/posts', POST)
# -------------------------------------------------------
# Attempt to create a post without auth header
def test_send_post_no_auth(app_client, test_db, user_headers, dummy_request_data):
    response = app_client.post(
        "/posts", data=json.dumps(dummy_request_data["new_post"])
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to create a post with a malformed auth header
def test_send_post_malformed_auth(
    app_client, test_db, user_headers, dummy_request_data
):
    response = app_client.post(
        "/posts",
        headers=user_headers["malformed"],
        data=json.dumps(dummy_request_data["new_post"]),
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to create a post with a user's JWT
def test_send_post_as_user(
    app_client, test_db, user_headers, dummy_request_data, dummy_users_data
):
    post = dummy_request_data["new_post"]
    post["userId"] = dummy_users_data["user"]["internal"]
    response = app_client.post(
        "/posts", headers=user_headers["user"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)
    response_post = response_data["posts"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_post["text"] == post["text"]


# Attempt to create a post with a moderator's JWT
def test_send_post_as_mod(
    app_client, test_db, user_headers, dummy_request_data, dummy_users_data
):
    post = dummy_request_data["new_post"]
    post["userId"] = dummy_users_data["moderator"]["internal"]
    response = app_client.post(
        "/posts", headers=user_headers["moderator"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)
    response_post = response_data["posts"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_post["text"] == post["text"]


# Attempt to create a post with an admin's JWT
def test_send_post_as_admin(
    app_client, test_db, user_headers, dummy_request_data, dummy_users_data
):
    post = dummy_request_data["new_post"]
    post["userId"] = dummy_users_data["admin"]["internal"]
    response = app_client.post(
        "/posts", headers=user_headers["admin"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)
    response_post = response_data["posts"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_post["text"] == post["text"]


# Attempt to create a post with a blocked user's JWT
def test_send_post_as_blocked(
    app_client, test_db, user_headers, dummy_request_data, dummy_users_data
):
    post = dummy_request_data["new_post"]
    post["userId"] = dummy_users_data["blocked"]["internal"]
    response = app_client.post(
        "/posts", headers=user_headers["blocked"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Update Post Route Tests ('/posts/<post_id>', PATCH)
# -------------------------------------------------------
# Attempt to update a post with no authorisation header
def test_update_post_no_auth(app_client, test_db, user_headers, dummy_request_data):
    response = app_client.patch(
        "/posts/4", data=json.dumps(dummy_request_data["updated_post"])
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to update a post with a malformed auth header
def test_update_post_malformed_auth(
    app_client, test_db, user_headers, dummy_request_data
):
    response = app_client.patch(
        "/posts/4",
        headers=user_headers["malformed"],
        data=json.dumps(dummy_request_data["updated_post"]),
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to update the user's post (with same user's JWT)
def test_update_own_post_as_user(
    app_client, test_db, user_headers, dummy_request_data, dummy_users_data
):
    post = dummy_request_data["updated_post"]
    post["userId"] = dummy_users_data["user"]["internal"]
    post["givenHugs"] = 2
    response = app_client.patch(
        "/posts/4", headers=user_headers["user"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)
    post_text = response_data["updated"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert post_text["text"] == post["text"]


# Attempt to update another user's post (with user's JWT)
def test_update_other_users_post_as_user(
    app_client, test_db, user_headers, dummy_request_data, dummy_users_data
):
    post = dummy_request_data["updated_post"]
    post["userId"] = dummy_users_data["moderator"]["internal"]
    post["givenHugs"] = 1
    response = app_client.patch(
        "/posts/13", headers=user_headers["user"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to update the moderator's post (with same moderator's JWT)
def test_update_own_post_as_mod(
    app_client, test_db, user_headers, dummy_request_data, dummy_users_data
):
    post = dummy_request_data["updated_post"]
    post["userId"] = dummy_users_data["moderator"]["internal"]
    post["givenHugs"] = 1
    response = app_client.patch(
        "/posts/13", headers=user_headers["moderator"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)
    post_text = response_data["updated"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert post_text["text"] == post["text"]


# Attempt to update another user's post (with moderator's JWT)
def test_update_other_users_post_as_mod(
    app_client, test_db, user_headers, dummy_request_data, dummy_users_data
):
    post = dummy_request_data["updated_post"]
    post["userId"] = dummy_users_data["user"]["internal"]
    post["givenHugs"] = 2
    response = app_client.patch(
        "/posts/4", headers=user_headers["moderator"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)
    post_text = response_data["updated"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert post_text["text"] == post["text"]


# Attempt to close the report on another user's post (with mod's JWT)
def test_update_other_users_post_report_as_mod(
    app_client, test_db, user_headers, dummy_request_data, dummy_users_data
):
    post = dummy_request_data["report_post"]
    post["userId"] = dummy_users_data["user"]["internal"]
    post["givenHugs"] = 2
    response = app_client.patch(
        "/posts/4", headers=user_headers["moderator"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to update the admin's post (with same admin's JWT)
def test_update_own_post_as_admin(
    app_client, test_db, user_headers, dummy_request_data, dummy_users_data
):
    post = dummy_request_data["updated_post"]
    post["userId"] = dummy_users_data["admin"]["internal"]
    post["givenHugs"] = 2
    response = app_client.patch(
        "/posts/23", headers=user_headers["admin"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)
    post_text = response_data["updated"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert post_text["text"] == post["text"]


# Attempt to update another user's post (with admin's JWT)
def test_update_other_users_post_as_admin(
    app_client, test_db, user_headers, dummy_request_data, dummy_users_data
):
    post = dummy_request_data["updated_post"]
    post["userId"] = dummy_users_data["user"]["internal"]
    post["givenHugs"] = 2
    response = app_client.patch(
        "/posts/4", headers=user_headers["admin"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)
    post_text = response_data["updated"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert post_text["text"] == post["text"]


# Attempt to close the report on another user's post (with admin's JWT)
def test_update_other_users_post_report_as_admin(
    app_client, test_db, user_headers, dummy_request_data, dummy_users_data
):
    post = dummy_request_data["report_post"]
    post["userId"] = dummy_users_data["user"]["internal"]
    post["givenHugs"] = 2
    response = app_client.patch(
        "/posts/4", headers=user_headers["admin"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)
    post_text = response_data["updated"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert post_text["text"] == post["text"]


# Attempt to update a post that doesn't exist (with admin's JWT)
def test_update_nonexistent_post_as_admin(
    app_client, test_db, user_headers, dummy_request_data, dummy_users_data
):
    post = dummy_request_data["updated_post"]
    post["userId"] = dummy_users_data["user"]["internal"]
    response = app_client.patch(
        "/posts/100", headers=user_headers["admin"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to update a post without post ID (with admin's JWT)
def test_update_post_no_id_as_admin(
    app_client, test_db, user_headers, dummy_request_data, dummy_users_data
):
    post = dummy_request_data["updated_post"]
    post["userId"] = dummy_users_data["user"]["internal"]
    response = app_client.patch(
        "/posts/", headers=user_headers["admin"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Send a Hug for post Tests ('/posts/<post_id>/hugs', POST)
# -------------------------------------------------------
# Attempt to send hugs for post you already sent hugs for
def test_post_hugs_given_duplicate_hugs(app_client, test_db, user_headers):
    response = app_client.post("/posts/1/hugs", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 409


# Attempt to send hugs for a post that doesn't exist
def test_post_hugs_post_no_existing(app_client, test_db, user_headers):
    response = app_client.post("/posts/1000/hugs", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to send hugs
def test_post_hugs(app_client, test_db, user_headers):
    response = app_client.post("/posts/1/hugs", headers=user_headers["moderator"])
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["updated"] == "Successfully sent hug for post 1"


# Delete Post Route Tests ('/posts/<post_id>', DELETE)
# -------------------------------------------------------
# Attempt to delete a post with no authorisation header
def test_delete_post_no_auth(app_client, test_db, user_headers):
    response = app_client.delete("/posts/3")
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to delete a post with a malformed auth header
def test_delete_post_malformed_auth(app_client, test_db, user_headers):
    response = app_client.delete("/posts/3", headers=user_headers["malformed"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to delete the user's post
@pytest.mark.parametrize(
    "post_id, user",
    [
        # (with same user's JWT)
        (2, "user"),
        # (with same moderator's JWT)
        (12, "moderator"),
        # (with same admin's JWT)
        (23, "admin"),
    ],
)
def test_delete_own_post(app_client, test_db, user_headers, post_id, user):
    response = app_client.delete(f"/posts/{post_id}", headers=user_headers[user])
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == post_id


# Attempt to delete another user's post (with user's JWT)
def test_delete_other_users_post_as_user(app_client, test_db, user_headers):
    response = app_client.delete("/posts/12", headers=user_headers["user"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to delete another user's post (with moderator's JWT)
def test_delete_other_users_post_as_mod(app_client, test_db, user_headers):
    response = app_client.delete("/posts/25", headers=user_headers["moderator"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to delete another user's post (with admin's JWT)
def test_delete_other_users_post_as_admin(app_client, test_db, user_headers):
    response = app_client.delete("/posts/1", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == 1


# Attempt to delete a post that doesn't exist (with admin's JWT)
def test_delete_nonexistent_post_as_admin(app_client, test_db, user_headers):
    response = app_client.delete("/posts/100", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to delete a post without post ID (with admin's JWT)
def test_delete_post_no_id_as_admin(app_client, test_db, user_headers):
    response = app_client.delete("/posts/", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Get Posts by Type Tests ('posts/<type>', GET)
# -------------------------------------------------------
# Attempt to get page 1 of each full page
@pytest.mark.parametrize(
    "post_type",
    [
        ("new"),
        ("suggested"),
    ],
)
def test_get_full_posts_page_1(app_client, test_db, post_type):
    response = app_client.get(f"/posts/{post_type}")
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert len(response_data["posts"]) == 5
    assert response_data["total_pages"] == 5


# Attempt to get page 2 of each full page
@pytest.mark.parametrize(
    "post_type",
    [
        ("new"),
        ("suggested"),
    ],
)
def test_get_full_posts_page_2(app_client, test_db, post_type):
    response = app_client.get(f"/posts/{post_type}?page=2")
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert len(response_data["posts"]) == 5
    assert response_data["total_pages"] == 5
