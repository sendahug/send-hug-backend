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

import json
from tests.dummy_data import (
    sample_admin_id,
    sample_moderator_id,
    sample_user_id,
    new_post,
    updated_post,
    blocked_user_id,
    report_post,
)


# Create Post Route Tests ('/posts', POST)
# -------------------------------------------------------
# Attempt to create a post without auth header
def test_send_post_no_auth(app_client, test_db, user_headers):
    response = app_client.post("/posts", data=json.dumps(new_post))
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to create a post with a malformed auth header
def test_send_post_malformed_auth(app_client, test_db, user_headers):
    response = app_client.post(
        "/posts", headers=user_headers["malformed"], data=json.dumps(new_post)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to create a post with a user's JWT
def test_send_post_as_user(app_client, test_db, user_headers):
    post = new_post
    post["userId"] = sample_user_id
    response = app_client.post(
        "/posts", headers=user_headers["user"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)
    response_post = response_data["posts"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_post["text"] == post["text"]


# Attempt to create a post with a moderator's JWT
def test_send_post_as_mod(app_client, test_db, user_headers):
    post = new_post
    post["userId"] = sample_moderator_id
    response = app_client.post(
        "/posts", headers=user_headers["moderator"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)
    response_post = response_data["posts"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_post["text"] == post["text"]


# Attempt to create a post with an admin's JWT
def test_send_post_as_admin(app_client, test_db, user_headers):
    post = new_post
    post["userId"] = sample_admin_id
    response = app_client.post(
        "/posts", headers=user_headers["admin"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)
    response_post = response_data["posts"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_post["text"] == post["text"]


# Attempt to create a post with a blocked user's JWT
def test_send_post_as_blocked(app_client, test_db, user_headers):
    post = new_post
    post["userId"] = blocked_user_id
    response = app_client.post(
        "/posts", headers=user_headers["blocked"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Update Post Route Tests ('/posts/<post_id>', PATCH)
# -------------------------------------------------------
# Attempt to update a post with no authorisation header
def test_update_post_no_auth(app_client, test_db, user_headers):
    response = app_client.patch("/posts/4", data=json.dumps(updated_post))
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to update a post with a malformed auth header
def test_update_post_malformed_auth(app_client, test_db, user_headers):
    response = app_client.patch(
        "/posts/4", headers=user_headers["malformed"], data=json.dumps(updated_post)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to update the user's post (with same user's JWT)
def test_update_own_post_as_user(app_client, test_db, user_headers):
    post = updated_post
    post["userId"] = sample_user_id
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
def test_update_other_users_post_as_user(app_client, test_db, user_headers):
    post = updated_post
    post["userId"] = sample_moderator_id
    post["givenHugs"] = 1
    response = app_client.patch(
        "/posts/13", headers=user_headers["user"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to update the moderator's post (with same moderator's JWT)
def test_update_own_post_as_mod(app_client, test_db, user_headers):
    post = updated_post
    post["userId"] = sample_moderator_id
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
def test_update_other_users_post_as_mod(app_client, test_db, user_headers):
    post = updated_post
    post["userId"] = sample_user_id
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
def test_update_other_users_post_report_as_mod(app_client, test_db, user_headers):
    post = report_post
    post["userId"] = sample_user_id
    post["givenHugs"] = 2
    response = app_client.patch(
        "/posts/4", headers=user_headers["moderator"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to update the admin's post (with same admin's JWT)
def test_update_own_post_as_admin(app_client, test_db, user_headers):
    post = updated_post
    post["userId"] = sample_admin_id
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
def test_update_other_users_post_as_admin(app_client, test_db, user_headers):
    post = updated_post
    post["userId"] = sample_user_id
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
def test_update_other_users_post_report_as_admin(app_client, test_db, user_headers):
    post = report_post
    post["userId"] = sample_user_id
    post["givenHugs"] = 2
    response = app_client.patch(
        "/posts/4", headers=user_headers["admin"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)
    post_text = response_data["updated"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert post_text["text"] == post["text"]


# Attempt to update a post with no ID (with admin's JWT)
def test_update_no_id_post_as_admin(app_client, test_db, user_headers):
    post = updated_post
    post["userId"] = sample_user_id
    response = app_client.patch(
        "/posts/", headers=user_headers["admin"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to update a post that doesn't exist (with admin's JWT)
def test_update_nonexistent_post_as_admin(app_client, test_db, user_headers):
    post = updated_post
    post["userId"] = sample_user_id
    response = app_client.patch(
        "/posts/100", headers=user_headers["admin"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to update a post without post ID
def test_update_post_no_id_as_admin(app_client, test_db, user_headers):
    post = updated_post
    post["userId"] = sample_user_id
    response = app_client.patch(
        "/posts/", headers=user_headers["admin"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to send hugs for post you already sent hugs for
def test_update_post_hugs_given_duplicate_hugs(app_client, test_db, user_headers):
    post = {"id": 1, "text": "test", "givenHugs": 3}
    response = app_client.patch(
        "/posts/1", headers=user_headers["admin"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 409


# Attempt to send hugs
def test_update_post_hugs(app_client, test_db, user_headers):
    post = {"id": 1, "text": "test", "givenHugs": 3}
    response = app_client.patch(
        "/posts/1", headers=user_headers["moderator"], data=json.dumps(post)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["updated"]["givenHugs"] == 3


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


# Attempt to delete the user's post (with same user's JWT)
def test_delete_own_post_as_user(app_client, test_db, user_headers):
    response = app_client.delete("/posts/2", headers=user_headers["user"])
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == "2"


# Attempt to delete another user's post (with user's JWT)
def test_delete_other_users_post_as_user(app_client, test_db, user_headers):
    response = app_client.delete("/posts/12", headers=user_headers["user"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to delete the moderator's post (with same moderator's JWT)
def test_delete_own_post_as_mod(app_client, test_db, user_headers):
    response = app_client.delete("/posts/12", headers=user_headers["moderator"])
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == "12"


# Attempt to delete another user's post (with moderator's JWT)
def test_delete_other_users_post_as_mod(app_client, test_db, user_headers):
    response = app_client.delete("/posts/25", headers=user_headers["moderator"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to delete the admin's post (with same admin's JWT)
def test_delete_own_post_as_admin(app_client, test_db, user_headers):
    response = app_client.delete("/posts/23", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == "23"


# Attempt to delete another user's post (with admin's JWT)
def test_delete_other_users_post_as_admin(app_client, test_db, user_headers):
    response = app_client.delete("/posts/1", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == "1"


# Attempt to delete a post with no ID (with admin's JWT)
def test_delete_no_id_post_as_admin(app_client, test_db, user_headers):
    response = app_client.delete("/posts/", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to delete a post that doesn't exist (with admin's JWT)
def test_delete_nonexistent_post_as_admin(app_client, test_db, user_headers):
    response = app_client.delete("/posts/100", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to delete a post without post ID
def test_delete_post_no_id_as_admin(app_client, test_db, user_headers):
    response = app_client.delete("/posts/", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Get Posts by Type Tests ('posts/<type>', GET)
# -------------------------------------------------------
# Attempt to get page 1 of full new posts
def test_get_full_new_posts(app_client, test_db, user_headers):
    response = app_client.get("/posts/new")
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert len(response_data["posts"]) == 5
    assert response_data["total_pages"] == 5


# Attempt to get page 2 of full new posts
def test_get_full_new_posts_page_2(app_client, test_db, user_headers):
    response = app_client.get("/posts/new?page=2")
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert len(response_data["posts"]) == 5
    assert response_data["total_pages"] == 5


# Attempt to get page 1 of full suggested posts
def test_get_full_suggested_posts(app_client, test_db, user_headers):
    response = app_client.get("/posts/suggested")
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert len(response_data["posts"]) == 5
    assert response_data["total_pages"] == 5


# Attempt to get page 2 of full suggested posts
def test_get_full_suggested_posts_page_2(app_client, test_db, user_headers):
    response = app_client.get("/posts/suggested?page=2")
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert len(response_data["posts"]) == 5
    assert response_data["total_pages"] == 5
