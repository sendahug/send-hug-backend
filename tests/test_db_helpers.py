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

import unittest
from datetime import datetime

from sh import pg_restore  # type: ignore
from werkzeug.exceptions import HTTPException

from models.db_helpers import (
    add,
    update,
    update_multiple,
    add_or_update_multiple,
)
from create_app import create_app
from models import db, Post
from .dummy_data import updated_post_1, DATETIME_PATTERN


# App testing
class TestHugApp(unittest.TestCase):
    # Setting up each test
    def setUp(self):
        test_db_path = "postgresql://postgres:password@localhost:5432/test_sah"
        self.app = create_app(db_path=test_db_path)
        self.client = self.app.test_client
        self.db = db

        pg_restore(
            "-d",
            "test_sah",
            "tests/capstone_db",
            "--clean",
            "--if-exists",
            "-Fc",
            "--no-owner",
            "-h",
            "localhost",
            "-p",
            "5432",
            "-U",
            "postgres",
        )

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            self.db.create_all()

    # Executed after each test
    def tearDown(self):
        # binds the app to the current context
        with self.app.app_context():
            self.db.drop_all()
            self.db.session.close()

    def test_add_no_errors(self):
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

        with self.app.app_context():
            post_to_add = Post(
                user_id=1,
                text="hello",
                date=current_date,
                given_hugs=0,
                open_report=False,
                sent_hugs="",
            )
            actual_return = add(obj=post_to_add)

            self.assertEqual(expected_return, actual_return["resource"])

    def test_add_integrity_error(self):
        with self.app.app_context():
            current_date = datetime.now()
            post_to_add = Post(
                user_id=100,
                text="hello",
                date=current_date,
                given_hugs=0,
                open_report=False,
                sent_hugs="",
            )

            with self.assertRaises(HTTPException) as exc:
                add(obj=post_to_add)

            self.assertIn("Unprocessable Entity", str(exc.exception))
            self.assertIn("violates foreign key constraint", str(exc.exception))

    def test_update_no_errors(self):
        expected_return = updated_post_1

        with self.app.app_context():
            post = self.db.session.get(Post, 1)
            original_text = post.text
            post.text = "new test"
            actual_return = update(obj=post)

            self.assertEqual(expected_return, actual_return["resource"])
            self.assertNotEqual(original_text, actual_return["resource"]["text"])

    def test_update_integrity_error(self):
        with self.app.app_context():
            post = self.db.session.get(Post, 1)
            post.text = None

            with self.assertRaises(HTTPException) as exc:
                update(obj=post)

            self.assertIn("Unprocessable Entity", str(exc.exception))
            self.assertIn("violates not-null constraint", str(exc.exception))

    def test_update_multiple_no_errors(self):
        expected_return = [
            updated_post_1,
            {
                "id": 2,
                "userId": 1,
                "user": "",
                "text": "test",
                "date": datetime.strptime("2020-06-01 15:10:59.898", DATETIME_PATTERN),
                "givenHugs": 3,
                "sentHugs": ["4"],
            },
        ]

        with self.app.app_context():
            posts = (
                self.db.session.query(Post).filter(Post.id < 3).order_by(Post.id).all()
            )
            original_post_1_text = posts[0].text
            posts[0].text = "new test"
            original_post_2_hugs = posts[1].given_hugs
            posts[1].given_hugs = 3
            actual_return = update_multiple(objs=posts)
            updated_posts = sorted(actual_return["resource"], key=lambda p: p["id"])

            self.assertEqual(expected_return, updated_posts)
            self.assertNotEqual(updated_posts[0]["text"], original_post_1_text)
            self.assertNotEqual(updated_posts[1]["givenHugs"], original_post_2_hugs)

    def test_update_multiple_error(self):
        with self.app.app_context():
            posts = (
                self.db.session.query(Post).filter(Post.id < 3).order_by(Post.id).all()
            )
            posts[0].text = "hello"
            posts[1].user_id = 1000

            with self.assertRaises(HTTPException) as exc:
                update_multiple(objs=posts)

            self.assertIn("Unprocessable Entity", str(exc.exception))
            self.assertIn("violates foreign key constraint", str(exc.exception))

            # Make sure the post that's right wasn't updated either
            post = self.db.session.get(Post, 1)
            self.assertNotEqual(post.text, "hello")

    def test_add_or_update_no_errors(self):
        current_date = datetime.now()
        expected_return = [
            updated_post_1,
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

        with self.app.app_context():
            post_to_add = Post(
                user_id=1,
                text="hello",
                date=current_date,
                given_hugs=0,
                open_report=False,
                sent_hugs="",
            )
            post_to_update = self.db.session.get(Post, 1)
            original_post_text = post_to_update.text
            post_to_update.text = "new test"
            actual_return = add_or_update_multiple(
                add_objs=[post_to_add], update_objs=[post_to_update]
            )

            self.assertEqual(expected_return, actual_return["resource"])
            self.assertNotEqual(
                original_post_text, actual_return["resource"][0]["text"]
            )

    def test_add_or_update_error(self):
        current_date = datetime.now()

        with self.app.app_context():
            post_to_add = Post(
                user_id=100,
                text="hello",
                date=current_date,
                given_hugs=0,
                open_report=False,
                sent_hugs="",
            )
            post_to_update = self.db.session.get(Post, 1)
            post_to_update.text = "new test"

            with self.assertRaises(HTTPException) as exc:
                add_or_update_multiple(
                    add_objs=[post_to_add], update_objs=[post_to_update]
                )

            self.assertIn("Unprocessable Entity", str(exc.exception))
            self.assertIn("violates foreign key constraint", str(exc.exception))

            # Make sure the post that's right wasn't updated either
            post = self.db.session.get(Post, 1)
            self.assertNotEqual(post.text, "new test")
