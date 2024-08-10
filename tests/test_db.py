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

from datetime import datetime

import pytest
from pytest_mock import MockerFixture
from sqlalchemy import Update, and_, delete, select, update
from sqlalchemy.exc import DataError, IntegrityError, OperationalError
from werkzeug.exceptions import HTTPException

from models import SendADatabase
from models.schemas.posts import Post


@pytest.fixture
def posts_to_add():
    current_date = datetime.now()
    return [
        Post(
            user_id=1,
            text="hello",
            date=current_date,
            given_hugs=0,
            sent_hugs=[],
        ),
        Post(
            user_id=1,
            text="hello",
            date=current_date,
            given_hugs=0,
            sent_hugs="",
        ),
    ]


@pytest.fixture
def invalid_post_to_add():
    current_date = datetime.now()
    return Post(
        user_id=100,
        text="hello",
        date=current_date,
        given_hugs=0,
        sent_hugs=[],
    )


@pytest.fixture
def update_post_stmts():
    return [
        update(Post).where(Post.user_id == 1).values(given_hugs=100),
        update(Post).where(Post.user_id == 4).values(given_hugs=10),
    ]


@pytest.mark.asyncio(scope="session")
async def test_paginate_no_error(test_db: SendADatabase):
    query = select(Post).where(Post.given_hugs > 0)

    results = await test_db.paginate(query, 1, 10)

    assert results.total_pages == 3
    assert results.total_items == 21
    assert len(results.resource) == 10


@pytest.mark.asyncio(scope="session")
async def test_paginate_with_error(mocker: MockerFixture, test_db: SendADatabase):
    mocker.patch(
        "models.models.Post.format", side_effect=Exception("There was an error!")
    )
    query = select(Post).where(Post.given_hugs > 0)

    with pytest.raises(HTTPException) as exc:
        await test_db.paginate(query, 1, 10)

    assert "There was an error" in str(exc.value)
    assert "500" in str(exc.value)


@pytest.mark.asyncio(scope="session")
async def test_one_or_404_success(test_db: SendADatabase):
    result = await test_db.one_or_404(1, Post)

    assert result.id == 1
    assert result.text == "test"


@pytest.mark.asyncio(scope="session")
async def test_one_or_404_not_existing(test_db: SendADatabase):
    with pytest.raises(HTTPException) as exc:
        await test_db.one_or_404(100, Post)

    assert "404" in str(exc.value)


@pytest.mark.asyncio(scope="session")
async def test_one_or_404_error(test_db: SendADatabase):
    with pytest.raises(HTTPException) as exc:
        await test_db.one_or_404("hi", Post)  # type: ignore

    assert "422" in str(exc.value)
    assert "invalid input for query argument" in str(exc.value)
    assert "'str' object cannot be interpreted as an integer" in str(exc.value)


@pytest.mark.asyncio(scope="session")
async def test_add_no_errors(test_db: SendADatabase, posts_to_add: list[Post]):
    post_to_add = posts_to_add[0]
    expected_return = {
        "id": 46,
        "userId": 1,
        "user": "shirb",
        "text": "hello",
        "date": post_to_add.date,
        "givenHugs": 0,
        "sentHugs": [],
    }

    actual_return = await test_db.add_object(obj=post_to_add)

    assert expected_return == actual_return


@pytest.mark.asyncio(scope="session")
async def test_add_integrity_error(test_db: SendADatabase, invalid_post_to_add: Post):
    with pytest.raises(HTTPException) as exc:
        await test_db.add_object(obj=invalid_post_to_add)

    assert "Unprocessable Entity" in str(exc.value)
    assert "422" in str(exc.value)
    assert "violates foreign key constraint" in str(exc.value)


@pytest.mark.asyncio(scope="session")
async def test_add_other_error(
    test_db: SendADatabase, mocker: MockerFixture, posts_to_add: list[Post]
):
    post_to_add = posts_to_add[0]
    mocker.patch.object(
        test_db.session,
        "commit",
        side_effect=OperationalError(
            statement="test error", params=None, orig=BaseException()
        ),
    )

    with pytest.raises(HTTPException) as exc:
        await test_db.add_object(obj=post_to_add)

    assert "500 Internal Server Error" in str(exc.value)
    assert "test error" in str(exc.value)


@pytest.mark.asyncio(scope="session")
async def test_add_multiple_no_errors(test_db: SendADatabase, posts_to_add: list[Post]):
    expected_return = [
        {
            "id": 46,
            "userId": 1,
            "user": "shirb",
            "text": "hello",
            "date": posts_to_add[0].date,
            "givenHugs": 0,
            "sentHugs": [],
        },
        {
            "id": 47,
            "userId": 1,
            "user": "shirb",
            "text": "hello",
            "date": posts_to_add[1].date,
            "givenHugs": 0,
            "sentHugs": [],
        },
    ]

    actual_return = await test_db.add_multiple_objects(objects=[*posts_to_add])

    assert expected_return == actual_return


@pytest.mark.asyncio(scope="session")
async def test_add_multiple_integrity_error(
    test_db: SendADatabase, invalid_post_to_add: Post, posts_to_add: list[Post]
):
    with pytest.raises(HTTPException) as exc:
        await test_db.add_multiple_objects(objects=[invalid_post_to_add, *posts_to_add])

    assert "Unprocessable Entity" in str(exc.value)
    assert "422" in str(exc.value)
    assert "violates foreign key constraint" in str(exc.value)


@pytest.mark.asyncio(scope="session")
async def test_add_multiple_other_error(
    test_db: SendADatabase, mocker: MockerFixture, posts_to_add: list[Post]
):
    mocker.patch.object(
        test_db.session,
        "commit",
        side_effect=OperationalError(
            statement="test error", params=None, orig=BaseException()
        ),
    )

    with pytest.raises(HTTPException) as exc:
        await test_db.add_multiple_objects(objects=[*posts_to_add])

    assert "500 Internal Server Error" in str(exc.value)
    assert "test error" in str(exc.value)


@pytest.mark.asyncio(scope="session")
async def test_update_no_errors(test_db: SendADatabase, db_helpers_dummy_data):
    expected_return = db_helpers_dummy_data["updated_post"]

    post = await test_db.session.get(Post, 1)

    if not post:
        pytest.fail("The post doesn't exist! Check the test database")

    original_text = post.text
    post.text = "new test"
    actual_return = await test_db.update_object(obj=post)

    assert expected_return == actual_return
    assert original_text != actual_return["text"]


@pytest.mark.asyncio(scope="session")
async def test_update_integrity_error(test_db: SendADatabase):
    post = await test_db.session.get(Post, 1)

    if not post:
        pytest.fail("The post doesn't exist! Check the test database")

    post.text = None  # type: ignore

    with pytest.raises(HTTPException) as exc:
        await test_db.update_object(obj=post)

    assert "Unprocessable Entity" in str(exc.value)
    assert "violates not-null constraint" in str(exc.value)


@pytest.mark.asyncio(scope="session")
async def test_update_other_error(
    test_db: SendADatabase, mocker: MockerFixture, posts_to_add: list[Post]
):
    mocker.patch.object(
        test_db.session,
        "commit",
        side_effect=OperationalError(
            statement="test error", params=None, orig=BaseException()
        ),
    )

    with pytest.raises(HTTPException) as exc:
        await test_db.update_object(obj=posts_to_add[0])

    assert "500 Internal Server Error" in str(exc.value)
    assert "test error" in str(exc.value)


@pytest.mark.asyncio(scope="session")
async def test_update_multiple_no_errors(test_db: SendADatabase, db_helpers_dummy_data):
    expected_return = [
        db_helpers_dummy_data["updated_post"],
        {
            "id": 2,
            "userId": 1,
            "user": "shirb",
            "text": "test",
            "date": datetime.strptime(
                "2020-06-01 15:10:59.898", db_helpers_dummy_data["DATETIME_PATTERN"]
            ),
            "givenHugs": 3,
            "sentHugs": [4],
        },
    ]

    posts_instances = await test_db.session.scalars(
        select(Post).filter(Post.id < 3).order_by(Post.id)
    )
    posts = posts_instances.all()
    original_post_1_text = posts[0].text
    posts[0].text = "new test"
    original_post_2_hugs = posts[1].given_hugs
    posts[1].given_hugs = 3
    actual_return = await test_db.update_multiple_objects(objects=posts)
    updated_posts = sorted(actual_return, key=lambda p: p["id"])

    assert expected_return == updated_posts
    assert updated_posts[0]["text"] != original_post_1_text
    assert updated_posts[1]["givenHugs"] != original_post_2_hugs


@pytest.mark.asyncio(scope="session")
async def test_update_multiple_error(test_db: SendADatabase):
    posts_instances = await test_db.session.scalars(
        select(Post).filter(Post.id < 3).order_by(Post.id)
    )
    posts = posts_instances.all()
    posts[0].text = "hello"
    posts[1].user_id = 1000

    with pytest.raises(HTTPException) as exc:
        await test_db.update_multiple_objects(objects=posts)

    assert "Unprocessable Entity" in str(exc.value)
    assert "violates foreign key constraint" in str(exc.value)

    # Make sure the post that's right wasn't updated either
    post = await test_db.session.get(Post, 1)

    if not post:
        pytest.fail("The post doesn't exist! Check the test database")

    assert post.text != "hello"


@pytest.mark.asyncio(scope="session")
async def test_update_multiple_other_error(
    test_db: SendADatabase, mocker: MockerFixture, posts_to_add: list[Post]
):
    mocker.patch.object(
        test_db.session,
        "commit",
        side_effect=OperationalError(
            statement="test error", params=None, orig=BaseException()
        ),
    )

    with pytest.raises(HTTPException) as exc:
        await test_db.update_multiple_objects(objects=[*posts_to_add])

    assert "500 Internal Server Error" in str(exc.value)
    assert "test error" in str(exc.value)


@pytest.mark.asyncio(scope="session")
async def test_update_multiple_dml_one_stmt(
    test_db: SendADatabase, update_post_stmts: list[Update]
):
    await test_db.update_multiple_objects_with_dml(update_stmts=update_post_stmts[0])

    closed_report_posts_scalars = await test_db.session.scalars(
        select(Post).where(and_(Post.user_id == 1, Post.given_hugs != 100))
    )
    closed_report_posts = closed_report_posts_scalars.all()
    given_hugs_posts_scalars = await test_db.session.scalars(
        select(Post).where(and_(Post.user_id == 4, Post.given_hugs != 10))
    )
    given_hugs_posts = given_hugs_posts_scalars.all()

    assert len(closed_report_posts) == 0
    assert len(given_hugs_posts) != 0


@pytest.mark.asyncio(scope="session")
async def test_update_multiple_dml_multiple_stmts(
    test_db: SendADatabase, update_post_stmts: list[Update]
):
    await test_db.update_multiple_objects_with_dml(update_stmts=update_post_stmts)

    closed_report_posts_scalars = await test_db.session.scalars(
        select(Post).where(and_(Post.user_id == 1, Post.given_hugs != 100))
    )
    closed_report_posts = closed_report_posts_scalars.all()
    given_hugs_posts_scalars = await test_db.session.scalars(
        select(Post).where(and_(Post.user_id == 4, Post.given_hugs != 10))
    )
    given_hugs_posts = given_hugs_posts_scalars.all()

    assert len(closed_report_posts) == 0
    assert len(given_hugs_posts) == 0


@pytest.mark.asyncio(scope="session")
async def test_update_multiple_dml_integrity_error(
    test_db: SendADatabase, mocker: MockerFixture, update_post_stmts: list[Update]
):
    mocker.patch.object(
        test_db.session,
        "commit",
        side_effect=DataError(
            statement="test error", params=None, orig=BaseException()
        ),
    )

    with pytest.raises(HTTPException) as exc:
        await test_db.update_multiple_objects_with_dml(update_stmts=update_post_stmts)

    assert "Unprocessable Entity" in str(exc.value)
    assert "422" in str(exc.value)


@pytest.mark.asyncio(scope="session")
async def test_update_multiple_dml_other_error(
    test_db: SendADatabase, mocker: MockerFixture, update_post_stmts: list[Update]
):
    mocker.patch.object(
        test_db.session,
        "commit",
        side_effect=OperationalError(
            statement="test error", params=None, orig=BaseException()
        ),
    )

    with pytest.raises(HTTPException) as exc:
        await test_db.update_multiple_objects_with_dml(update_stmts=update_post_stmts)

    assert "500 Internal Server Error" in str(exc.value)
    assert "test error" in str(exc.value)


@pytest.mark.parametrize(
    "error, exception_code, exception_error",
    [
        (IntegrityError, "422 Unprocessable Entity", "invalid selection!"),
        (DataError, "422 Unprocessable Entity", "DBAPI error!"),
        (OperationalError, "500 Internal Server Error", "test error"),
    ],
)
@pytest.mark.asyncio(scope="session")
async def test_delete_error(
    test_db: SendADatabase,
    mocker: MockerFixture,
    posts_to_add: list[Post],
    error,
    exception_code,
    exception_error,
):
    mocker.patch.object(
        test_db.session,
        "delete",
        side_effect=error(
            statement=exception_error, params=None, orig=BaseException(exception_error)
        ),
    )

    with pytest.raises(HTTPException) as exc:
        await test_db.delete_object(object=posts_to_add[0])

    assert exception_code in str(exc.value)
    assert exception_error in str(exc.value)


@pytest.mark.parametrize(
    "error, exception_code, exception_error",
    [
        (IntegrityError, "422 Unprocessable Entity", "invalid selection!"),
        (DataError, "422 Unprocessable Entity", "DBAPI error!"),
        (OperationalError, "500 Internal Server Error", "test error"),
    ],
)
@pytest.mark.asyncio(scope="session")
async def test_delete_dml_error(
    test_db: SendADatabase,
    mocker: MockerFixture,
    error,
    exception_code,
    exception_error,
):
    mocker.patch.object(
        test_db.session,
        "execute",
        side_effect=error(
            statement=exception_error, params=None, orig=BaseException(exception_error)
        ),
    )

    delete_stmt = delete(Post).where(Post.user_id == 1)

    with pytest.raises(HTTPException) as exc:
        await test_db.delete_multiple_objects(delete_stmt=delete_stmt)

    assert exception_code in str(exc.value)
    assert exception_error in str(exc.value)
