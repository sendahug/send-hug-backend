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

import pytest

from models import User, Report
from tests.dummy_data import (
    sample_admin_auth0_id,
    sample_admin_id,
    sample_moderator_auth0_id,
    sample_moderator_id,
    sample_user_auth0_id,
    sample_user_id,
    new_message,
    new_post,
    new_report,
    new_subscription,
    new_user,
    updated_display,
    updated_post,
    updated_unblock_user,
    updated_user,
    blocked_user_id,
    report_post,
    new_user_report,
)


# App testing
# Index Route Tests ('/', GET)
# -------------------------------------------------------
def test_get_home_page(app_client, test_db, user_headers):
    response = app_client.get("/")
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert len(response_data["recent"]) == 10
    assert len(response_data["suggested"]) == 10


# Search Route Tests ('/', POST)
# -------------------------------------------------------
# Run a search
def test_search(app_client, test_db, user_headers):
    response = app_client.post("/", data=json.dumps({"search": "user"}))
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["post_results"] == 1
    assert response_data["user_results"] == 4


# Run a search which returns multiple pages of results
def test_search_multiple_pages(app_client, test_db, user_headers):
    response = app_client.post("/", data=json.dumps({"search": "test"}))
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["post_results"] == 13
    assert len(response_data["posts"]) == 5
    assert response_data["total_pages"] == 3
    assert response_data["current_page"] == 1
    assert response_data["user_results"] == 0


# Run a search which returns multiple pages of results - get page 2
def test_search_multiple_pages_page_2(app_client, test_db, user_headers):
    response = app_client.post("/?page=2", data=json.dumps({"search": "test"}))
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["post_results"] == 13
    assert len(response_data["posts"]) == 5
    assert response_data["total_pages"] == 3
    assert response_data["current_page"] == 2
    assert response_data["user_results"] == 0


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


# Get Users by Type Tests ('/users/<type>', GET)
# -------------------------------------------------------
# Attempt to get list of users without auth header
def test_get_user_list_no_auth(app_client, test_db, user_headers):
    response = app_client.get("/users/blocked")
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get list of users with malformed auth header
def test_get_user_list_malformed_auth(app_client, test_db, user_headers):
    response = app_client.get("/users/blocked", headers=user_headers["malformed"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get list of users with user's auth header
def test_get_user_list_as_user(app_client, test_db, user_headers):
    response = app_client.get("/users/blocked", headers=user_headers["user"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to get list of users with moderator's auth header
def test_get_user_list_as_mod(app_client, test_db, user_headers):
    response = app_client.get("/users/blocked", headers=user_headers["moderator"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to get list of users with admin's auth header
def test_get_user_list_as_admin(app_client, test_db, user_headers):
    response = app_client.get("/users/blocked", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["total_pages"] == 1


# Attempt to get list of users with admin's auth header
def test_get_user_list_unsupported_type(app_client, test_db, user_headers):
    response = app_client.get("/users/meow", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 500


# Get User Data Tests ('/users/all/<user_id>', GET)
# -------------------------------------------------------
# Attempt to get a user's data without auth header
def test_get_user_data_no_auth(app_client, test_db, user_headers):
    response = app_client.get("/users/all/1")
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get a user's data with malformed auth header
def test_get_user_data_malformed_auth(app_client, test_db, user_headers):
    response = app_client.get("/users/all/1", headers=user_headers["malformed"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get a user's data with a user's JWT
def test_get_user_data_as_user(app_client, test_db, user_headers):
    response = app_client.get(
        f"/users/all/{sample_user_auth0_id}", headers=user_headers["user"]
    )
    response_data = json.loads(response.data)
    user_data = response_data["user"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert user_data["id"] == int(sample_user_id)


# Attempt to get a user's data with a moderator's JWT
def test_get_user_data_as_mod(app_client, test_db, user_headers):
    response = app_client.get(
        f"/users/all/{sample_moderator_auth0_id}", headers=user_headers["moderator"]
    )
    response_data = json.loads(response.data)
    user_data = response_data["user"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert user_data["id"] == int(sample_moderator_id)


# Attempt to get a user's data with an admin's JWT
def test_get_user_data_as_admin(app_client, test_db, user_headers):
    response = app_client.get(
        f"/users/all/{sample_admin_auth0_id}", headers=user_headers["admin"]
    )
    response_data = json.loads(response.data)
    user_data = response_data["user"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert user_data["id"] == int(sample_admin_id)


# Attempt to get a user's data with no ID (with admin's JWT)
def test_get_no_id_user_as_admin(app_client, test_db, user_headers):
    response = app_client.get("/users/all/", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to get a nonexistent user's data (with admin's JWT)
def test_get_nonexistent_user_as_admin(app_client, test_db, user_headers):
    response = app_client.get("/users/all/100", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to get a user without post ID
def test_get_user_no_id_as_admin(app_client, test_db, user_headers):
    response = app_client.get("/users/all/", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Create User Tests ('/users', POST)
# -------------------------------------------------------
# Attempt to create a user without auth header
def test_create_user_no_auth(app_client, test_db, user_headers):
    response = app_client.post("/users", data=new_user)
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to create a user with malformed auth header
def test_create_user_malformed_auth(app_client, test_db, user_headers):
    response = app_client.post(
        "/users", headers=user_headers["malformed"], data=new_user
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to create a user with user's JWT
def test_create_user_as_user(app_client, test_db, user_headers):
    response = app_client.post("/users", headers=user_headers["user"], data=new_user)
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to create a user with moderator's JWT
def test_create_user_as_moderator(app_client, test_db, user_headers):
    response = app_client.post(
        "/users", headers=user_headers["moderator"], data=new_user
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to create a user with admin's JWT
def test_create_user_as_damin(app_client, test_db, user_headers):
    response = app_client.post("/users", headers=user_headers["admin"], data=new_user)
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to create a user with new user's JWT
# This test is performed as fallback; since the new user -> user change
# is done automatically, it's no longer needed, but in case of an error
# adjusting a user's roles, it's important to make sure they still
# can't create other users
def test_create_different_user_as_new_user(app_client, test_db, user_headers):
    response = app_client.post("/users", headers=user_headers["blocked"], data=new_user)
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 422


# Edit User Data Tests ('/users/all/<user_id>', PATCH)
# -------------------------------------------------------
# Attempt to update a user's data without auth header
def test_update_user_no_auth(app_client, test_db, user_headers):
    response = app_client.patch("/users/all/1", data=json.dumps(updated_user))
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to update a user's data with malformed auth header
def test_update_user_malformed_auth(app_client, test_db, user_headers):
    response = app_client.patch(
        "/users/all/1", headers=user_headers["malformed"], data=json.dumps(updated_user)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to update a user's data with a user's JWT
def test_update_user_as_user(app_client, test_db, user_headers):
    user = updated_user
    user["id"] = sample_user_id
    user["displayName"] = "user"
    response = app_client.patch(
        f"/users/all/{sample_user_id}",
        headers=user_headers["user"],
        data=json.dumps(user),
    )
    response_data = json.loads(response.data)
    updated = response_data["updated"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert updated["receivedH"] == user["receivedH"]
    assert updated["givenH"] == user["givenH"]


# Attempt to update another user's display name with a user's JWT
def test_update_other_users_display_name_as_user(app_client, test_db, user_headers):
    user = updated_display
    user["id"] = sample_moderator_id
    response = app_client.patch(
        f"/users/all/{sample_moderator_id}",
        headers=user_headers["user"],
        data=json.dumps(user),
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to update a user's blocked state with a user's JWT
def test_update_block_user_as_user(app_client, test_db, user_headers):
    user = updated_unblock_user
    user["id"] = sample_user_id
    response = app_client.patch(
        f"/users/all/{sample_user_id}",
        headers=user_headers["user"],
        data=json.dumps(user),
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to update a user's data with a moderator's JWT
def test_update_user_as_mod(app_client, test_db, user_headers):
    user = updated_user
    user["id"] = sample_moderator_id
    user["displayName"] = "mod"
    response = app_client.patch(
        f"/users/all/{sample_moderator_id}",
        headers=user_headers["moderator"],
        data=json.dumps(user),
    )
    response_data = json.loads(response.data)
    updated = response_data["updated"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert updated["receivedH"] == user["receivedH"]
    assert updated["givenH"] == user["givenH"]


# Attempt to update another user's display name with a moderator's JWT
def test_update_other_users_display_name_as_mod(app_client, test_db, user_headers):
    user = updated_display
    user["id"] = sample_admin_id
    response = app_client.patch(
        f"/users/all/{sample_admin_id}",
        headers=user_headers["moderator"],
        data=json.dumps(user),
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to update a user's blocked state with a moderator's JWT
def test_update_block_user_as_mod(app_client, test_db, user_headers):
    user = updated_unblock_user
    user["id"] = sample_moderator_id
    response = app_client.patch(
        f"/users/all/{sample_moderator_id}",
        headers=user_headers["moderator"],
        data=json.dumps(user),
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to update a user's data with an admin's JWT
def test_update_user_as_admin(app_client, test_db, user_headers):
    user = updated_user
    user["id"] = sample_admin_id
    user["displayName"] = "admin"
    response = app_client.patch(
        f"/users/all/{sample_admin_id}",
        headers=user_headers["admin"],
        data=json.dumps(user),
    )
    response_data = json.loads(response.data)
    updated = response_data["updated"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert updated["receivedH"] == user["receivedH"]
    assert updated["givenH"] == user["givenH"]


# Attempt to update another user's display name with an admin's JWT
def test_update_other_user_as_admin(app_client, test_db, user_headers):
    user = updated_display
    user["id"] = sample_user_id
    response = app_client.patch(
        f"/users/all/{sample_user_id}",
        headers=user_headers["admin"],
        data=json.dumps(user),
    )
    response_data = json.loads(response.data)
    updated = response_data["updated"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert updated["receivedH"] == user["receivedH"]


# Attempt to update a user's blocked state with an admin's JWT
def test_update_block_user_as_admin(app_client, test_db, user_headers):
    user = updated_unblock_user
    user["id"] = sample_user_id
    response = app_client.patch(
        f"/users/all/{sample_user_id}",
        headers=user_headers["admin"],
        data=json.dumps(user),
    )
    response_data = json.loads(response.data)
    updated = response_data["updated"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert updated["id"] == int(sample_user_id)


# Attempt to update another user's settings (admin's JWT)
def test_update_user_settings_as_admin(app_client, test_db, user_headers):
    user = updated_unblock_user
    user["id"] = sample_user_id
    user["autoRefresh"] = True
    user["pushEnabled"] = True
    response = app_client.patch(
        f"/users/all/{sample_user_id}",
        headers=user_headers["admin"],
        data=json.dumps(user),
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to update a user's data with no ID (with admin's JWT)
def test_update_no_id_user_as_admin(app_client, test_db, user_headers):
    response = app_client.patch(
        "/users/all/", headers=user_headers["admin"], data=json.dumps(updated_user)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to update another user's settings (admin's JWT)
def test_update_admin_settings_as_admin(app_client, test_db, user_headers):
    user = {**updated_unblock_user}
    user["id"] = sample_admin_id
    user["autoRefresh"] = True
    user["pushEnabled"] = True
    user["refreshRate"] = 60
    response = app_client.patch(
        f"/users/all/{sample_admin_id}",
        headers=user_headers["admin"],
        data=json.dumps(user),
    )
    response_data = json.loads(response.data)
    updated = response_data["updated"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert updated["autoRefresh"] is True
    assert updated["pushEnabled"] is True
    assert updated["refreshRate"] == 60


def test_close_report_update_user_as_admin(app_client, test_db, user_headers):
    user = {**updated_unblock_user}
    user["id"] = sample_moderator_id
    user["closeReport"] = 6
    response = app_client.patch(
        f"/users/all/{sample_admin_id}",
        headers=user_headers["admin"],
        data=json.dumps(user),
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200

    moderator = test_db.session.get(User, sample_moderator_id)
    report = test_db.session.get(Report, 6)

    if not moderator or not report:
        pytest.fail()

    assert moderator.open_report is False
    assert (report.closed) is True
    assert report.dismissed is False


# Get User's Posts Tests ('/users/all/<user_id>/posts', GET)
# -------------------------------------------------------
# Attempt to get a user's posts without auth header
def test_get_user_posts_no_auth(app_client, test_db, user_headers):
    response = app_client.get("/users/all/1/posts")
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get a user's posts with malformed auth header
def test_get_user_posts_malformed_auth(app_client, test_db, user_headers):
    response = app_client.get("/users/all/1/posts", headers=user_headers["malformed"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get a user's posts with a user's JWT
def test_get_user_posts_as_user(app_client, test_db, user_headers):
    response = app_client.get("/users/all/1/posts", headers=user_headers["user"])
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["page"] == 1
    assert response_data["total_pages"] == 2
    assert len(response_data["posts"]) == 5


# Attempt to get a user's posts with a moderator's JWT
def test_get_user_posts_as_mod(app_client, test_db, user_headers):
    response = app_client.get("/users/all/4/posts", headers=user_headers["moderator"])
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["page"] == 1
    assert response_data["total_pages"] == 3
    assert len(response_data["posts"]) == 5


# Attempt to get a user's posts with an admin's JWT
def test_get_user_posts_as_admin(app_client, test_db, user_headers):
    response = app_client.get("/users/all/5/posts", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["page"] == 1
    assert response_data["total_pages"] == 1
    assert len(response_data["posts"]) == 2


# Delete User's Posts Route Tests ('/users/all/<user_id>/posts', DELETE)
# -------------------------------------------------------
# Attempt to delete user's posts with no authorisation header
def test_delete_posts_no_auth(app_client, test_db, user_headers):
    response = app_client.delete("/users/all/1/posts")
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to delete user's with a malformed auth header
def test_delete_posts_malformed_auth(app_client, test_db, user_headers):
    response = app_client.delete(
        "/users/all/1/posts", headers=user_headers["malformed"]
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to delete the user's posts (with same user's JWT)
def test_delete_own_posts_as_user(app_client, test_db, user_headers):
    response = app_client.delete("/users/all/1/posts", headers=user_headers["user"])
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == 8


# Attempt to delete another user's posts (with user's JWT)
def test_delete_other_users_posts_as_user(app_client, test_db, user_headers):
    response = app_client.delete("/users/all/4/posts", headers=user_headers["user"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to delete the moderator's posts (with same moderator's JWT)
def test_delete_own_posts_as_mod(app_client, test_db, user_headers):
    response = app_client.delete(
        "/users/all/5/posts", headers=user_headers["moderator"]
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == 2


# Attempt to delete another user's posts (with moderator's JWT)
def test_delete_other_users_posts_as_mod(app_client, test_db, user_headers):
    response = app_client.delete(
        "/users/all/1/posts", headers=user_headers["moderator"]
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to delete the admin's posts (with same admin's JWT)
def test_delete_own_posts_as_admin(app_client, test_db, user_headers):
    response = app_client.delete("/users/all/4/posts", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == 14


# Attempt to delete another user's posts (with admin's JWT)
def test_delete_other_users_posts_as_admin(app_client, test_db, user_headers):
    response = app_client.delete("/users/all/5/posts", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == 2


# Attempt to delete the posts of a user that doesn't exist (admin's JWT)
def test_delete_nonexistent_users_posts_as_admin(app_client, test_db, user_headers):
    response = app_client.delete("/users/all/100/posts", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to delete the posts of a user that has no posts (admin's JWT)
def test_delete_nonexistent_posts_as_admin(app_client, test_db, user_headers):
    response = app_client.delete("/users/all/9/posts", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Get User's Messages Tests ('/messages', GET)
# -------------------------------------------------------
# Attempt to get a user's messages without auth header
def test_get_user_messages_no_auth(app_client, test_db, user_headers):
    response = app_client.get("/messages?userID=1")
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get a user's messages with malformed auth header
def test_get_user_messages_malformed_auth(app_client, test_db, user_headers):
    response = app_client.get("/messages?userID=1", headers=user_headers["malformed"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get a user's inbox with a user's JWT
def test_get_user_inbox_as_user(app_client, test_db, user_headers):
    response = app_client.get(
        f"/messages?userID={sample_user_id}", headers=user_headers["user"]
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["current_page"] == 1
    assert response_data["total_pages"] == 2
    assert len(response_data["messages"]) == 5


# Attempt to get a user's outbox with a user's JWT
def test_get_user_outbox_as_user(app_client, test_db, user_headers):
    response = app_client.get(
        f"/messages?type=outbox&userID={sample_user_id}", headers=user_headers["user"]
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["current_page"] == 1
    assert response_data["total_pages"] == 1
    assert len(response_data["messages"]) == 2


# Attempt to get a user's threads mailbox with a user's JWT
def test_get_user_threads_as_user(app_client, test_db, user_headers):
    response = app_client.get(
        f"/messages?type=threads&userID={sample_user_id}", headers=user_headers["user"]
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["current_page"] == 1
    assert response_data["total_pages"] == 1
    assert len(response_data["messages"]) == 4


# Attempt to get another user's messages with a user's JWT
def test_get_another_users_messages_as_user(app_client, test_db, user_headers):
    response = app_client.get(
        f"/messages?userID={sample_moderator_id}", headers=user_headers["user"]
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to get a user's inbox with a moderator's JWT
def test_get_user_inbox_as_mod(app_client, test_db, user_headers):
    response = app_client.get(
        f"/messages?userID={sample_moderator_id}", headers=user_headers["moderator"]
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["current_page"] == 1
    assert response_data["total_pages"] == 1
    assert len(response_data["messages"]) == 5


# Attempt to get a user's outbox with a moderator's JWT
def test_get_user_outbox_as_mod(app_client, test_db, user_headers):
    response = app_client.get(
        f"/messages?type=outbox&userID={sample_moderator_id}",
        headers=user_headers["moderator"],
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["current_page"] == 1
    assert response_data["total_pages"] == 1
    assert len(response_data["messages"]) == 2


# Attempt to get a user's threads mailbox with a moderator's JWT
def test_get_user_threads_as_mod(app_client, test_db, user_headers):
    response = app_client.get(
        f"/messages?type=threads&userID={sample_moderator_id}",
        headers=user_headers["moderator"],
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["current_page"] == 1
    assert response_data["total_pages"] == 1
    assert len(response_data["messages"]) == 3


#  Attempt to get another user's messages with a moderator's JWT
def test_get_another_users_messages_as_mod(app_client, test_db, user_headers):
    response = app_client.get(
        f"/messages?userID={sample_admin_id}", headers=user_headers["moderator"]
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to get a user's inbox with an admin's JWT
def test_get_user_inbox_as_admin(app_client, test_db, user_headers):
    response = app_client.get(
        f"/messages?userID={sample_admin_id}", headers=user_headers["admin"]
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["current_page"] == 1
    assert response_data["total_pages"] == 1
    assert len(response_data["messages"]) == 1


# Attempt to get a user's outbox with an admin's JWT
def test_get_user_outbox_as_admin(app_client, test_db, user_headers):
    response = app_client.get(
        f"/messages?type=outbox&userID={sample_admin_id}", headers=user_headers["admin"]
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["current_page"] == 1
    assert response_data["total_pages"] == 1
    assert len(response_data["messages"]) == 3


# Attempt to get a user's threads mailbox with an admin's JWT
def test_get_user_threads_as_admin(app_client, test_db, user_headers):
    response = app_client.get(
        f"/messages?type=threads&userID={sample_admin_id}",
        headers=user_headers["admin"],
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["current_page"] == 1
    assert response_data["total_pages"] == 1
    assert len(response_data["messages"]) == 2


# Attempt to get another user's messages with an admin's JWT
def test_get_another_users_messages_as_admin(app_client, test_db, user_headers):
    response = app_client.get(
        f"/messages?userID={sample_user_id}", headers=user_headers["admin"]
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to get a user's messages with no ID (with admin's JWT)
def test_get_no_id_user_messages_as_admin(app_client, test_db, user_headers):
    response = app_client.get("/messages", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 400


# Attempt to get other users' messaging thread (with admin's JWT)
def get_other_users_thread_as_admin(app_client, test_db, user_headers):
    response = app_client.get(
        "/messages?userID=4&type=thread&threadID=2",
        headers=user_headers["admin"],
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to get other users' messaging thread (with admin's JWT)
def get_nonexistent_thread_as_admin(app_client, test_db, user_headers):
    response = app_client.get(
        f"/messages?userID={sample_admin_id}&type=thread&threadID=200",
        headers=user_headers["admin"],
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Create Message Route Tests ('/message', POST)
# -------------------------------------------------------
# Attempt to create a message with no authorisation header
def test_send_message_no_auth(app_client, test_db, user_headers):
    response = app_client.post("/messages", data=json.dumps(new_message))
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to create a message with a malformed auth header
def test_send_message_malformed_auth(app_client, test_db, user_headers):
    response = app_client.post(
        "/messages", headers=user_headers["malformed"], data=json.dumps(new_message)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to create a message with a user's JWT
def test_send_message_as_user(app_client, test_db, user_headers):
    message = new_message
    message["fromId"] = int(sample_user_id)
    message["forId"] = sample_moderator_id
    response = app_client.post(
        "/messages", headers=user_headers["user"], data=json.dumps(message)
    )
    response_data = json.loads(response.data)
    response_message = response_data["message"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_message["messageText"] == message["messageText"]


# Attempt to create a message from another user (with a user's JWT)
def test_send_message_from_another_user_as_user(app_client, test_db, user_headers):
    message = new_message
    message["fromId"] = int(sample_admin_id)
    message["forId"] = sample_moderator_id
    response = app_client.post(
        "/messages", headers=user_headers["user"], data=json.dumps(message)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to create a message with a moderator's JWT
def test_send_message_as_mod(app_client, test_db, user_headers):
    message = new_message
    message["fromId"] = int(sample_moderator_id)
    message["forId"] = sample_admin_id
    response = app_client.post(
        "/messages", headers=user_headers["moderator"], data=json.dumps(message)
    )
    response_data = json.loads(response.data)
    response_message = response_data["message"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_message["messageText"] == message["messageText"]


# Attempt to create a message from another user (with a moderator's JWT)
def test_send_message_from_another_user_as_mod(app_client, test_db, user_headers):
    message = new_message
    message["fromId"] = int(sample_admin_id)
    message["forId"] = sample_user_id
    response = app_client.post(
        "/messages", headers=user_headers["moderator"], data=json.dumps(message)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to create a message with an admin's JWT
def test_send_message_as_admin(app_client, test_db, user_headers):
    message = new_message
    message["fromId"] = int(sample_admin_id)
    message["forId"] = sample_moderator_id
    response = app_client.post(
        "/messages", headers=user_headers["admin"], data=json.dumps(message)
    )
    response_data = json.loads(response.data)
    response_message = response_data["message"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_message["messageText"] == message["messageText"]


# Attempt to create a message from another user (with an admin's JWT)
def test_send_message_from_another_user_as_admin(app_client, test_db, user_headers):
    message = new_message
    message["fromId"] = int(sample_user_id)
    message["forId"] = sample_moderator_id
    response = app_client.post(
        "/messages", headers=user_headers["admin"], data=json.dumps(message)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to send a message from a user (when there's no thread)
def test_send_message_existing_thread_as_user(app_client, test_db, user_headers):
    message = new_message
    message["fromId"] = int(blocked_user_id)
    message["forId"] = sample_admin_id
    response = app_client.post(
        "/messages", headers=user_headers["blocked"], data=json.dumps(message)
    )
    response_data = json.loads(response.data)
    response_message = response_data["message"]
    new_thread = app_client.get(
        "/messages?userID=20&type=thread&threadID=7", headers=user_headers["blocked"]
    )
    new_thread_data = json.loads(new_thread.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_message["messageText"] == message["messageText"]
    assert response_message["threadID"] == 7
    assert len(new_thread_data["messages"]) == 2


def test_send_message_create_thread(app_client, test_db, user_headers):
    message = {**new_message}
    message["fromId"] = int(sample_admin_id)
    message["forId"] = 9
    response = app_client.post(
        "/messages", headers=user_headers["admin"], data=json.dumps(message)
    )
    response_data = json.loads(response.data)
    response_message = response_data["message"]
    new_thread = app_client.get(
        f"/messages?userID={sample_admin_id}&type=thread&threadID=9",
        headers=user_headers["admin"],
    )
    new_thread_data = json.loads(new_thread.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_message["messageText"] == message["messageText"]
    assert response_message["threadID"] == 9
    assert len(new_thread_data["messages"]) == 1


# Delete Message Route Tests ('/message/<message_id>', DELETE)
# -------------------------------------------------------
# Attempt to delete a message with no authorisation header
def test_delete_message_no_auth(app_client, test_db, user_headers):
    response = app_client.delete("/messages/inbox/1")
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to delete a message with a malformed auth header
def test_delete_message_malformed_auth(app_client, test_db, user_headers):
    response = app_client.delete("/messages/inbox/1", headers=user_headers["malformed"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to delete a message with a user's JWT
def test_delete_message_as_user(app_client, test_db, user_headers):
    response = app_client.delete("/messages/inbox/3", headers=user_headers["user"])
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == "3"


# Attempt to delete another user's message (with a user's JWT)
def test_delete_message_from_another_user_as_user(app_client, test_db, user_headers):
    response = app_client.delete("/messages/inbox/7", headers=user_headers["user"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to delete a thread with a user's JWT
def test_delete_thread_as_user(app_client, test_db, user_headers):
    response = app_client.delete("/messages/threads/2", headers=user_headers["user"])
    response_data = json.loads(response.data)
    get_thread = app_client.get(
        "/messages?userID=1&type=thread&threadID=2",
        headers=user_headers["user"],
    )
    thread_data = json.loads(get_thread.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == "2"
    assert len(thread_data["messages"]) == 0


# Attempt to delete a message with a moderator's JWT
def test_delete_message_as_mod(app_client, test_db, user_headers):
    response = app_client.delete("/messages/inbox/5", headers=user_headers["moderator"])
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == "5"


# Attempt to delete another user's message (with a moderator's JWT)
def test_delete_message_from_another_user_as_mod(app_client, test_db, user_headers):
    response = app_client.delete(
        "/messages/outbox/9", headers=user_headers["moderator"]
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to delete a message with an admin's JWT
def test_delete_message_as_admin(app_client, test_db, user_headers):
    response = app_client.delete("/messages/outbox/10", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == "10"


# Attempt to delete another user's message (with an admin's JWT)
def test_delete_message_from_another_user_as_admin(app_client, test_db, user_headers):
    response = app_client.delete("/messages/outbox/3", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to delete a user's message with no mailbox (with admin's JWT)
def test_delete_no_id_user_message_as_admin(app_client, test_db, user_headers):
    response = app_client.delete("/messages/", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to delete a nonexistent user's message (with admin's JWT)
def test_delete_nonexistent_user_message_as_admin(app_client, test_db, user_headers):
    response = app_client.delete("/messages/inbox/100", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to delete a message without ID
def test_delete_message_without_id_admin(app_client, test_db, user_headers):
    response = app_client.delete("/messages/inbox/", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Empty Mailbox Tests ('/messages/<mailbox>', DELETE)
# -------------------------------------------------------
# Attempt to empty mailbox without auth header
def test_empty_mailbox_no_auth(app_client, test_db, user_headers):
    response = app_client.delete("/messages/inbox?userID=4")
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to empty mailbox with malformed auth header
def test_empty_mailbox_malformed_auth(app_client, test_db, user_headers):
    response = app_client.delete(
        "/messages/inbox?userID=4", headers=user_headers["malformed"]
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to empty user's inbox (user JWT)
def test_empty_mailbox_as_user(app_client, test_db, user_headers):
    response = app_client.delete(
        f"/messages/inbox?userID={sample_user_id}", headers=user_headers["user"]
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == 7
    assert response_data["userID"] == 1


# Attempt to empty another user's inbox (user JWT)
def test_empty_other_users_mailbox_as_user(app_client, test_db, user_headers):
    response = app_client.delete(
        "/messages/inbox?userID=4", headers=user_headers["user"]
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to empty user's outbox (moderator's JWT)
def test_empty_mailbox_as_mod(app_client, test_db, user_headers):
    response = app_client.delete(
        f"/messages/outbox?userID={sample_moderator_id}",
        headers=user_headers["moderator"],
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == 2
    assert response_data["userID"] == 5


# Attempt to empty another user's outbox (moderator's JWT)
def test_empty_other_users_mailbox_as_mod(app_client, test_db, user_headers):
    response = app_client.delete(
        "/messages/outbox?userID=1", headers=user_headers["moderator"]
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to empty user's threads mailbox (admin's JWT)
def test_empty_mailbox_as_admin(app_client, test_db, user_headers):
    response = app_client.delete(
        f"/messages/threads?userID={sample_admin_id}", headers=user_headers["admin"]
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["deleted"] == 2
    assert response_data["userID"] == 4


# Attempt to empty another user's threads mailbox (admin's JWT)
def test_empty_other_users_mailbox_as_admin(app_client, test_db, user_headers):
    response = app_client.delete(
        "/messages/threads?userID=5", headers=user_headers["admin"]
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to empty user mailbox without user type
def test_empty_mailbox_type_as_admin(app_client, test_db, user_headers):
    response = app_client.delete("/messages/", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to empty user mailbox without user ID
def test_empty_mailbox_id_as_admin(app_client, test_db, user_headers):
    response = app_client.delete(
        "/messages/threads?userID=", headers=user_headers["admin"]
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 400


# Get Open Reports Tests ('/reports', GET)
# -------------------------------------------------------
# Attempt to get open reports without auth header
def test_get_open_reports_no_auth(app_client, test_db, user_headers):
    response = app_client.get("/reports")
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get open reports with malformed auth header
def test_get_open_reports_malformed_auth(app_client, test_db, user_headers):
    response = app_client.get("/reports", headers=user_headers["malformed"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get open reports with a user's JWT
def test_get_open_reports_as_user(app_client, test_db, user_headers):
    response = app_client.get("/reports", headers=user_headers["user"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


#  Attempt to get open reports with a moderator's JWT
def test_get_open_reports_as_mod(app_client, test_db, user_headers):
    response = app_client.get("/reports", headers=user_headers["moderator"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to get open reports with an admin's JWT
def test_get_open_reports_as_admin(app_client, test_db, user_headers):
    response = app_client.get("/reports", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["totalUserPages"] == 0
    assert response_data["totalPostPages"] == 0
    assert len(response_data["userReports"]) == 0
    assert len(response_data["postReports"]) == 0


# Create Report Route Tests ('/reports', POST)
# -------------------------------------------------------
# Attempt to create a report with no authorisation header
def test_send_report_no_auth(app_client, test_db, user_headers):
    response = app_client.post("/reports", data=json.dumps(new_report))
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to create a report with a malformed auth header
def test_send_report_malformed_auth(app_client, test_db, user_headers):
    response = app_client.post(
        "/reports", headers=user_headers["malformed"], data=json.dumps(new_report)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to create a report with a user's JWT
def test_send_report_as_user(app_client, test_db, user_headers):
    report = new_report
    report["userID"] = 4
    report["postID"] = 25
    report["reporter"] = sample_user_id
    response = app_client.post(
        "/reports", headers=user_headers["user"], data=json.dumps(report)
    )
    response_data = json.loads(response.data)
    response_report = response_data["report"]

    assert response_data["success"] is True
    assert response_report["closed"] is False
    assert response.status_code == 200
    assert response_report["postID"] == report["postID"]


# Attempt to create a report with a moderator's JWT
def test_send_report_as_mod(app_client, test_db, user_headers):
    report = new_report
    report["userID"] = 4
    report["postID"] = 25
    report["reporter"] = sample_moderator_id
    response = app_client.post(
        "/reports", headers=user_headers["moderator"], data=json.dumps(report)
    )
    response_data = json.loads(response.data)
    response_report = response_data["report"]

    assert response_data["success"] is True
    assert response_report["closed"] is False
    assert response.status_code == 200
    assert response_report["postID"] == report["postID"]


# Attempt to create a report with an admin's JWT
def test_send_report_as_admin(app_client, test_db, user_headers):
    report = new_report
    report["userID"] = 4
    report["postID"] = 25
    report["reporter"] = sample_admin_id
    response = app_client.post(
        "/reports", headers=user_headers["admin"], data=json.dumps(report)
    )
    response_data = json.loads(response.data)
    response_report = response_data["report"]

    assert response_data["success"] is True
    assert response_report["closed"] is False
    assert response.status_code == 200
    assert response_report["postID"] == report["postID"]


# Attempt to create a post report without post ID with an admin's JWT
def test_send_malformed_report_as_admin(app_client, test_db, user_headers):
    report = new_report
    report["userID"] = 4
    report["postID"] = None
    report["reporter"] = sample_admin_id
    response = app_client.post(
        "/reports", headers=user_headers["admin"], data=json.dumps(report)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 422


# Attempt to create a post report for post that doesn't exist
def test_send_report_nonexistent_post_as_admin(app_client, test_db, user_headers):
    report = new_report
    report["userID"] = 4
    report["postID"] = 1000
    report["reporter"] = sample_admin_id
    response = app_client.post(
        "/reports", headers=user_headers["admin"], data=json.dumps(report)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to create a report with an admin's JWT
def test_send_user_report_as_admin(app_client, test_db, user_headers):
    report = new_user_report
    report["userID"] = 1
    report["reporter"] = sample_admin_id
    response = app_client.post(
        "/reports", headers=user_headers["admin"], data=json.dumps(report)
    )
    response_data = json.loads(response.data)
    response_report = response_data["report"]

    assert response_data["success"] is True
    assert response_report["closed"] is False
    assert response.status_code == 200
    assert response_report["userID"] == report["userID"]


# Attempt to create a report for user that doesn't exist
def test_send_user_report_nonexistent_user_as_admin(app_client, test_db, user_headers):
    report = new_user_report
    report["userID"] = 100
    report["reporter"] = sample_admin_id
    response = app_client.post(
        "/reports", headers=user_headers["admin"], data=json.dumps(report)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Update Report Route Tests ('/reports/<report_id>', PATCH)
# -------------------------------------------------------
# Attempt to update a report with no authorisation header
def test_update_report_no_auth(app_client, test_db, user_headers):
    response = app_client.patch("/reports/36", data=json.dumps(new_report))
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to update a report with a malformed auth header
def test_update_report_malformed_auth(app_client, test_db, user_headers):
    response = app_client.patch(
        "/reports/36", headers=user_headers["malformed"], data=json.dumps(new_report)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to update a report (with user's JWT)
def test_update_report_as_user(app_client, test_db, user_headers):
    report = new_report
    report["userID"] = 4
    report["postID"] = 25
    report["reporter"] = sample_user_id
    response = app_client.patch(
        "/reports/36", headers=user_headers["user"], data=json.dumps(report)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to update a report (with moderator's JWT)
def test_update_report_as_mod(app_client, test_db, user_headers):
    report = new_report
    report["userID"] = 4
    report["postID"] = 25
    report["reporter"] = sample_moderator_id
    response = app_client.patch(
        "/reports/36", headers=user_headers["moderator"], data=json.dumps(report)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to update a report (with admin's JWT)
def test_update_report_as_admin(app_client, test_db, user_headers):
    report = new_report
    report["id"] = 36
    report["userID"] = 4
    report["postID"] = 25
    report["reporter"] = sample_admin_id
    report["dismissed"] = False
    report["closed"] = False
    response = app_client.patch(
        "/reports/36", headers=user_headers["admin"], data=json.dumps(report)
    )
    response_data = json.loads(response.data)
    report_text = response_data["updated"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert report_text["id"] == report["id"]


# Attempt to update a report (with admin's JWT)
def test_update_user_report_as_admin(app_client, test_db, user_headers):
    report = new_user_report
    report["id"] = 35
    report["userID"] = 5
    report["reporter"] = sample_admin_id
    report["dismissed"] = False
    report["closed"] = False
    response = app_client.patch(
        "/reports/35", headers=user_headers["admin"], data=json.dumps(report)
    )
    response_data = json.loads(response.data)
    report_text = response_data["updated"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert report_text["id"] == report["id"]
    assert report_text["userID"] == report["userID"]


# Attempt to update a report with no ID (with admin's JWT)
def test_update_no_id_report_as_admin(app_client, test_db, user_headers):
    report = new_report
    report["id"] = 36
    report["userID"] = 4
    report["postID"] = 25
    report["reporter"] = sample_admin_id
    report["dismissed"] = False
    report["closed"] = False
    response = app_client.patch(
        "/reports/", headers=user_headers["admin"], data=json.dumps(report)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Attempt to update a report that doesn't exist (with admin's JWT)
def test_update_nonexistent_report_as_admin(app_client, test_db, user_headers):
    report = new_report
    report["id"] = 36
    report["userID"] = 4
    report["postID"] = 25
    report["reporter"] = sample_admin_id
    report["dismissed"] = False
    report["closed"] = False
    response = app_client.patch(
        "/reports/100", headers=user_headers["admin"], data=json.dumps(report)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


# Get Filters Tests ('/filters', GET)
# -------------------------------------------------------
# Attempt to get filters without auth header
def test_get_filters_no_auth(app_client, test_db, user_headers):
    response = app_client.get("/filters")
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get filters with malformed auth header
def test_get_filters_malformed_auth(app_client, test_db, user_headers):
    response = app_client.get("/filters", headers=user_headers["malformed"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to get filters with a user's JWT
def test_get_filters_as_user(app_client, test_db, user_headers):
    response = app_client.get("/filters", headers=user_headers["user"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


#  Attempt to get filters with a moderator's JWT
def test_get_filters_as_mod(app_client, test_db, user_headers):
    response = app_client.get("/filters", headers=user_headers["moderator"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to get filters with an admin's JWT
def test_get_filters_as_admin(app_client, test_db, user_headers):
    response = app_client.get("/filters", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["total_pages"] == 0
    assert len(response_data["words"]) == 0


# Create Filters Tests ('/filters', POST)
# -------------------------------------------------------
# Attempt to create a filter without auth header
def test_create_filters_no_auth(app_client, test_db, user_headers):
    response = app_client.post("/filters", data=json.dumps({"word": "sample"}))
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to create a filter with malformed auth header
def test_create_filters_malformed_auth(app_client, test_db, user_headers):
    response = app_client.post(
        "/filters",
        headers=user_headers["malformed"],
        data=json.dumps({"word": "sample"}),
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to create a filter with a user's JWT
def test_create_filters_as_user(app_client, test_db, user_headers):
    response = app_client.post(
        "/filters", headers=user_headers["user"], data=json.dumps({"word": "sample"})
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


#  Attempt to create a filter with a moderator's JWT
def test_create_filters_as_mod(app_client, test_db, user_headers):
    response = app_client.post(
        "/filters",
        headers=user_headers["moderator"],
        data=json.dumps({"word": "sample"}),
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to create a filter with an admin's JWT
def test_create_filters_as_admin(app_client, test_db, user_headers):
    response = app_client.post(
        "/filters", headers=user_headers["admin"], data=json.dumps({"word": "sample"})
    )
    response_data = json.loads(response.data)
    added_word = response_data["added"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert added_word["filter"] == "sample"


# Attempt to create a filter with an admin's JWT
def test_create_duplicate_filters_as_admin(app_client, test_db, user_headers):
    filter = {"word": "sample"}
    app_client.post("/filters", headers=user_headers["admin"], data=json.dumps(filter))
    response = app_client.post(
        "/filters", headers=user_headers["admin"], data=json.dumps(filter)
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 409


# Delete Filters Tests ('/filters/<id>', DELETE)
# -------------------------------------------------------
# Attempt to delete a filter without auth header
def test_delete_filters_no_auth(app_client, test_db, user_headers):
    response = app_client.delete("/filters/1")
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to delete a filter with malformed auth header
def test_delete_filters_malformed_auth(app_client, test_db, user_headers):
    response = app_client.delete("/filters/1", headers=user_headers["malformed"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to delete a filter with a user's JWT
def test_delete_filters_as_user(app_client, test_db, user_headers):
    response = app_client.delete("/filters/1", headers=user_headers["user"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


#  Attempt to delete a filter with a moderator's JWT
def test_delete_filters_as_mod(app_client, test_db, user_headers):
    response = app_client.delete("/filters/1", headers=user_headers["moderator"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 403


# Attempt to delete a filter with an admin's JWT
def test_delete_filters_as_admin(app_client, test_db, user_headers):
    # Set up the test by adding a word
    app_client.post(
        "/filters", headers=user_headers["admin"], data=json.dumps({"word": "sample"})
    )
    # Delete the filter
    response = app_client.delete("/filters/2", headers=user_headers["admin"])
    response_data = json.loads(response.data)
    deleted = response_data["deleted"]

    assert response_data["success"] is True
    assert response.status_code == 200
    assert deleted["filter"] == "sample"


# Attempt to delete a filter that doesn't exist with an admin's JWT
def test_delete_nonexistent_filters_as_admin(app_client, test_db, user_headers):
    response = app_client.delete("/filters/100", headers=user_headers["admin"])
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 404


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
def test_get_silent_notifications_as_user(app_client, test_db, user_headers):
    pre_user_query = app_client.get(
        f"/users/all/{sample_user_auth0_id}", headers=user_headers["user"]
    )
    pre_user_data = json.loads(pre_user_query.data)["user"]
    response = app_client.get(
        "/notifications?silentRefresh=true", headers=user_headers["user"]
    )
    response_data = json.loads(response.data)
    post_user_query = app_client.get(
        f"/users/all/{sample_user_auth0_id}", headers=user_headers["user"]
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
def test_get_non_silent_notifications_as_user(app_client, test_db, user_headers):
    pre_user_query = app_client.get(
        f"/users/all/{sample_user_auth0_id}", headers=user_headers["user"]
    )
    pre_user_data = json.loads(pre_user_query.data)["user"]
    response = app_client.get(
        "/notifications?silentRefresh=false", headers=user_headers["user"]
    )
    response_data = json.loads(response.data)
    post_user_query = app_client.get(
        f"/users/all/{sample_user_auth0_id}", headers=user_headers["user"]
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
def test_get_silent_notifications_as_mod(app_client, test_db, user_headers):
    pre_user_query = app_client.get(
        f"/users/all/{sample_moderator_auth0_id}", headers=user_headers["moderator"]
    )
    pre_user_data = json.loads(pre_user_query.data)["user"]
    response = app_client.get(
        "/notifications?silentRefresh=true", headers=user_headers["moderator"]
    )
    response_data = json.loads(response.data)
    post_user_query = app_client.get(
        f"/users/all/{sample_moderator_auth0_id}", headers=user_headers["moderator"]
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
def test_get_non_silent_notifications_as_mod(app_client, test_db, user_headers):
    pre_user_query = app_client.get(
        f"/users/all/{sample_moderator_auth0_id}", headers=user_headers["moderator"]
    )
    pre_user_data = json.loads(pre_user_query.data)["user"]
    response = app_client.get(
        "/notifications?silentRefresh=false", headers=user_headers["moderator"]
    )
    response_data = json.loads(response.data)
    post_user_query = app_client.get(
        f"/users/all/{sample_moderator_auth0_id}", headers=user_headers["moderator"]
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
def test_get_silent_notifications_as_admin(app_client, test_db, user_headers):
    pre_user_query = app_client.get(
        f"/users/all/{sample_admin_auth0_id}", headers=user_headers["admin"]
    )
    pre_user_data = json.loads(pre_user_query.data)["user"]
    response = app_client.get(
        "/notifications?silentRefresh=true", headers=user_headers["admin"]
    )
    response_data = json.loads(response.data)
    post_user_query = app_client.get(
        f"/users/all/{sample_admin_auth0_id}", headers=user_headers["admin"]
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
def test_get_non_silent_notifications_as_admin(app_client, test_db, user_headers):
    pre_user_query = app_client.get(
        f"/users/all/{sample_admin_auth0_id}", headers=user_headers["admin"]
    )
    pre_user_data = json.loads(pre_user_query.data)["user"]
    response = app_client.get(
        "/notifications?silentRefresh=false", headers=user_headers["admin"]
    )
    response_data = json.loads(response.data)
    post_user_query = app_client.get(
        f"/users/all/{sample_admin_auth0_id}", headers=user_headers["admin"]
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
def test_post_subscription_no_auth(app_client, test_db, user_headers):
    response = app_client.post("/notifications", data=json.dumps(new_subscription))
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to create push subscription with malformed auth header
def test_post_subscription_malformed_auth(app_client, test_db, user_headers):
    response = app_client.post(
        "/notifications",
        data=json.dumps(new_subscription),
        headers=user_headers["malformed"],
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to create push subscription with a user's JWT
def test_post_subscription_as_user(app_client, test_db, user_headers):
    response = app_client.post(
        "/notifications",
        data=json.dumps(new_subscription),
        headers=user_headers["user"],
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["subscribed"] == "shirb"
    assert response_data["subId"] == 11


# Attempt to create push subscription with a moderator's JWT
def test_post_subscription_as_mod(app_client, test_db, user_headers):
    response = app_client.post(
        "/notifications",
        data=json.dumps(new_subscription),
        headers=user_headers["moderator"],
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["subscribed"] == "user52"
    assert response_data["subId"] == 11


# Attempt to create push subscription with an admin's JWT
def test_post_subscription_as_admin(app_client, test_db, user_headers):
    response = app_client.post(
        "/notifications",
        data=json.dumps(new_subscription),
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
def test_update_subscription_no_auth(app_client, test_db, user_headers):
    # Create the subscription
    app_client.post(
        "/notifications",
        data=json.dumps(new_subscription),
        headers=user_headers["user"],
    )
    # Then update it
    updated_subscription: dict[str, Any] = {**new_subscription}
    updated_subscription["id"] = 11
    response = app_client.patch("/notifications/11", data=json.dumps(new_subscription))
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to update push subscription with malformed auth header
def test_update_subscription_malformed_auth(app_client, test_db, user_headers):
    # Create the subscription
    app_client.post(
        "/notifications",
        data=json.dumps(new_subscription),
        headers=user_headers["user"],
    )
    # Then update it
    updated_subscription: dict[str, Any] = {**new_subscription}
    updated_subscription["id"] = 11
    response = app_client.patch(
        "/notifications/11",
        data=json.dumps(new_subscription),
        headers=user_headers["malformed"],
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is False
    assert response.status_code == 401


# Attempt to update push subscription with a user's JWT
def test_update_subscription_as_user(app_client, test_db, user_headers):
    # Create the subscription
    app_client.post(
        "/notifications",
        data=json.dumps(new_subscription),
        headers=user_headers["user"],
    )
    # Then update it
    updated_subscription: dict[str, Any] = {**new_subscription}
    updated_subscription["id"] = 11
    response = app_client.patch(
        "/notifications/11",
        data=json.dumps(new_subscription),
        headers=user_headers["user"],
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["subscribed"] == "shirb"
    assert response_data["subId"] == 11


# Attempt to create push subscription with a moderator's JWT
def test_update_subscription_as_mod(app_client, test_db, user_headers):
    # Create the subscription
    app_client.post(
        "/notifications",
        data=json.dumps(new_subscription),
        headers=user_headers["moderator"],
    )
    # Then update it
    updated_subscription: dict[str, Any] = {**new_subscription}
    updated_subscription["id"] = 11
    response = app_client.patch(
        "/notifications/11",
        data=json.dumps(new_subscription),
        headers=user_headers["moderator"],
    )
    response_data = json.loads(response.data)

    assert response_data["success"] is True
    assert response.status_code == 200
    assert response_data["subscribed"] == "user52"
    assert response_data["subId"] == 11


# Attempt to create push subscription with an admin's JWT
def test_update_subscription_as_admin(app_client, test_db, user_headers):
    # Create the subscription
    app_client.post(
        "/notifications",
        data=json.dumps(new_subscription),
        headers=user_headers["admin"],
    )
    # Then update it
    updated_subscription: dict[str, Any] = {**new_subscription}
    updated_subscription["id"] = 11
    response = app_client.patch(
        "/notifications/11",
        data=json.dumps(new_subscription),
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
