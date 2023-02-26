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

from datetime import datetime

from werkzeug.exceptions import HTTPException
import pytest

from models.db_helpers import (
    add,
    update,
    update_multiple,
    add_or_update_multiple,
)
from models import Post


def test_add_no_errors(test_db):
    current_date = datetime.now()
    expected_return = {
        "id": 46,
        "userId": 1,
        "user": "",
        "text": "hello",
        "date": current_date,
        "givenHugs": 0,
        "sentHugs": [],
    }

    post_to_add = Post(
        user_id=1,
        text="hello",
        date=current_date,
        given_hugs=0,
        open_report=False,
        sent_hugs="",
    )
    actual_return = add(obj=post_to_add)

    assert expected_return == actual_return["resource"]


def test_add_integrity_error(test_db):
    current_date = datetime.now()
    post_to_add = Post(
        user_id=100,
        text="hello",
        date=current_date,
        given_hugs=0,
        open_report=False,
        sent_hugs="",
    )

    with pytest.raises(HTTPException) as exc:
        add(obj=post_to_add)

    assert "Unprocessable Entity" in str(exc.value)
    assert "violates foreign key constraint" in str(exc.value)


def test_update_no_errors(test_db, db_helpers_dummy_data):
    expected_return = db_helpers_dummy_data["updated_post"]

    post = test_db.session.get(Post, 1)

    if not post:
        pytest.fail("The post doesn't exist! Check the test database")

    original_text = post.text
    post.text = "new test"
    actual_return = update(obj=post)

    assert expected_return == actual_return["resource"]
    assert original_text != actual_return["resource"]["text"]


def test_update_integrity_error(test_db):
    post = test_db.session.get(Post, 1)

    if not post:
        pytest.fail("The post doesn't exist! Check the test database")

    post.text = None

    with pytest.raises(HTTPException) as exc:
        update(obj=post)

    assert "Unprocessable Entity" in str(exc.value)
    assert "violates not-null constraint" in str(exc.value)


def test_update_multiple_no_errors(test_db, db_helpers_dummy_data):
    expected_return = [
        db_helpers_dummy_data["updated_post"],
        {
            "id": 2,
            "userId": 1,
            "user": "",
            "text": "test",
            "date": datetime.strptime(
                "2020-06-01 15:10:59.898", db_helpers_dummy_data["DATETIME_PATTERN"]
            ),
            "givenHugs": 3,
            "sentHugs": ["4"],
        },
    ]

    posts = test_db.session.query(Post).filter(Post.id < 3).order_by(Post.id).all()
    original_post_1_text = posts[0].text
    posts[0].text = "new test"
    original_post_2_hugs = posts[1].given_hugs
    posts[1].given_hugs = 3
    actual_return = update_multiple(objs=posts)
    updated_posts = sorted(actual_return["resource"], key=lambda p: p["id"])

    assert expected_return == updated_posts
    assert updated_posts[0]["text"] != original_post_1_text
    assert updated_posts[1]["givenHugs"] != original_post_2_hugs


def test_update_multiple_error(test_db):
    posts = test_db.session.query(Post).filter(Post.id < 3).order_by(Post.id).all()
    posts[0].text = "hello"
    posts[1].user_id = 1000

    with pytest.raises(HTTPException) as exc:
        update_multiple(objs=posts)

    assert "Unprocessable Entity" in str(exc.value)
    assert "violates foreign key constraint" in str(exc.value)

    # Make sure the post that's right wasn't updated either
    post = test_db.session.get(Post, 1)

    if not post:
        pytest.fail("The post doesn't exist! Check the test database")

    assert post.text != "hello"


def test_add_or_update_no_errors(test_db, db_helpers_dummy_data):
    current_date = datetime.now()
    expected_return = [
        db_helpers_dummy_data["updated_post"],
        {
            "id": 46,
            "userId": 1,
            "user": "",
            "text": "hello",
            "date": current_date,
            "givenHugs": 0,
            "sentHugs": [],
        },
    ]

    post_to_add = Post(
        user_id=1,
        text="hello",
        date=current_date,
        given_hugs=0,
        open_report=False,
        sent_hugs="",
    )
    post_to_update = test_db.session.get(Post, 1)

    if not post_to_update:
        pytest.fail("The post doesn't exist! Check the test database")

    original_post_text = post_to_update.text
    post_to_update.text = "new test"
    actual_return = add_or_update_multiple(
        add_objs=[post_to_add], update_objs=[post_to_update]
    )

    assert expected_return == actual_return["resource"]
    assert original_post_text != actual_return["resource"][0]["text"]


def test_add_or_update_error(test_db):
    current_date = datetime.now()

    post_to_add = Post(
        user_id=100,
        text="hello",
        date=current_date,
        given_hugs=0,
        open_report=False,
        sent_hugs="",
    )
    post_to_update = test_db.session.get(Post, 1)

    if not post_to_update:
        pytest.fail("The post doesn't exist! Check the test database")

    post_to_update.text = "new test"

    with pytest.raises(HTTPException) as exc:
        add_or_update_multiple(add_objs=[post_to_add], update_objs=[post_to_update])

    assert "Unprocessable Entity" in str(exc.value)
    assert "violates foreign key constraint" in str(exc.value)

    # Make sure the post that's right wasn't updated either
    post = test_db.session.get(Post, 1)

    if not post:
        pytest.fail("The post doesn't exist! Check the test database")

    assert post.text != "new test"
