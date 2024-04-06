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
    assert 1 == 2


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
