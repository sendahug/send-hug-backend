from asyncio import current_task
from datetime import datetime
from os import listdir, path
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
from pytest_mock import MockerFixture
from quart.typing import TestClientProtocol
from sqlalchemy.ext.asyncio import async_scoped_session, async_sessionmaker

from config import SAHConfig
from create_app import create_app
from tests.data_models import DATETIME_PATTERN, create_data, update_sequences

from models import SendADatabase
from models.common import BaseModel


@pytest.fixture(scope="session")
def user_headers(session_mocker: MockerFixture):
    """
    Sets the headers for each of the users and mocks
    the verify_id_token function from Firebase.
    """

    roles = ["user", "moderator", "admin", "blocked"]
    user_headers: dict[str, dict[str, str]] = {}

    for role in roles:
        # Set the authorisation headers
        user_headers[role] = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {role}.{role}.{role}",
        }

    user_headers["malformed"] = {
        "Content-Type": "application/json",
        "Authorization": "Bearer",
    }

    def verify_token(token, app):
        if "user" in token:
            return {"uid": "abcd"}
        elif "moderator" in token:
            return {"uid": "efgh"}
        elif "blocked" in token:
            return {"uid": "twg"}
        else:
            return {"uid": "ijkl"}

    session_mocker.patch("auth.verify_id_token", new=verify_token)

    return user_headers


@pytest.fixture(scope="session")
def test_config(session_mocker: MockerFixture) -> Generator[SAHConfig, None, None]:
    """Set up the config"""

    # TODO: We should at least make sure that this works with
    # an actual key.
    # session_mocker.patch("config.initialize_app", return_value=initialize_app())
    # session_mocker.patch("config.Certificate")
    yield SAHConfig(
        credentials_path=Path("test.json"),
        override_db_name="test_sah",
    )


@pytest.fixture(scope="function")
def app_client(
    test_config: SAHConfig, mocker: MockerFixture
) -> Generator[TestClientProtocol, None, None]:
    """Get the test client for the test app"""

    # mocker.patch("create_app.sah_config", AsyncMock())
    # mocker.patch("controllers.root.sah_config", AsyncMock())

    app = create_app()

    yield app.test_client()


@pytest.fixture(scope="session")
async def db(test_config: SAHConfig) -> AsyncGenerator[SendADatabase, None]:
    """Creates the database and inserts the test data."""
    try:
        async with test_config.db.engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.drop_all)
            await conn.run_sync(BaseModel.metadata.create_all)

        await create_data(test_config.db)

        await test_config.db.engine.dispose()

        yield test_config.db

    finally:
        async with test_config.db.engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.drop_all)


@pytest.fixture(scope="function")
async def test_db(
    db: SendADatabase, mocker: MockerFixture
) -> AsyncGenerator[SendADatabase, None]:
    """
    Generates the session to use in tests. Once tests are done, rolls
    back the transaction and closes the session. Also updates the values
    of all sequences.
    Credit to gmassman; the code is mostly copied from
    https://github.com/gmassman/fsa-rollback-per-test-example.
    """
    try:
        connection = await db.engine.connect()
        transaction = await connection.begin_nested()

        db.session_factory = async_sessionmaker(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        db.session = async_scoped_session(
            session_factory=db.session_factory, scopefunc=current_task
        )

        def get_scoped_session():
            return async_scoped_session(
                session_factory=db.session_factory, scopefunc=current_task
            )

        # Surely there's a better way to do this
        controllers = listdir(path.join(path.dirname(__file__), "../controllers"))
        non_controllers = ["__init__.py", "common.py", "__pycache__"]
        for controller in controllers:
            if controller in non_controllers:
                continue

            mocker.patch(
                f"controllers.{controller[:-3]}.sah_config.db.session",
                new_callable=get_scoped_session,
            )

        # async_mock = AsyncMock()

        await update_sequences(db)

        await db.session.begin_nested()
        mocker.patch("pywebpush.webpush")
        mocker.patch("controllers.common.webpush")

        # mocker.patch.object(connection, "begin", new=connection.begin_nested)
        # mocker.patch.object(session, "commit", new=session.flush)
        # mocker.patch("config.sah_config.db.session", side_effect=async_mock)
        # mocker.patch("config.get_db_credentials_path", return_value=Path("test.json"))

        # async_mock.return_value = db.session

        yield db

    finally:
        # Delete the session
        await db.session.remove()

        # Rollback the transaction and return the connection to the pool
        await transaction.rollback()
        await connection.close()
        await db.engine.dispose()


@pytest.fixture
def dummy_users_data():
    """Get the users' dummy data for the test"""
    # Sample users data
    user_data = {
        "user": {
            "internal": "1",
            "firebase_id": "abcd",
        },
        "moderator": {
            "internal": "5",
            "firebase_id": "efgh",
        },
        "admin": {
            "internal": "4",
            "firebase_id": "ijkl",
        },
        "blocked": {"internal": "20", "firebase_id": "twg"},
    }

    return user_data


@pytest.fixture
def dummy_request_data() -> dict:
    """Dummy POST/PATCH request data for the various endpoints."""
    # Item Samples
    request_data = {
        "new_post": {
            "userId": 0,
            "text": "test post",
            "date": "2020-06-07T15:57:45.901Z",
            "givenHugs": 0,
        },
        "updated_post": {
            "userId": 0,
            "text": "test post",
            "date": "2020-06-07T15:57:45.901Z",
            "givenHugs": 0,
        },
        "report_post": {
            "user_id": 0,
            "text": "test post",
            "date": "2020-06-07T15:57:45.901Z",
            "givenHugs": 0,
            "closeReport": 1,
        },
        "new_user": {
            "displayName": "user",
            "receivedH": 0,
            "givenH": 0,
            "loginCount": 0,
            "firebaseId": "uohljl",
        },
        "updated_user": {
            "id": 0,
            "displayName": "",
            "receivedH": 0,
            "givenH": 0,
            "loginCount": 0,
        },
        "updated_unblock_user": {
            "id": 0,
            "displayName": "hello",
            "receivedH": 0,
            "givenH": 0,
            "loginCount": 0,
            "blocked": False,
            "releaseDate": None,
        },
        "updated_display": {
            "id": 0,
            "displayName": "meow",
            "receivedH": 0,
            "givenH": 0,
            "loginCount": 0,
        },
        "new_message": {
            "fromId": 0,
            "forId": 0,
            "messageText": "meow",
            "date": "2020-06-07T15:57:45.901Z",
        },
        "new_report": {
            "type": "Post",
            "userID": 0,
            "postID": 0,
            "reporter": 0,
            "reportReason": "It is inappropriate",
            "date": "2020-06-07T15:57:45.901Z",
        },
        "new_user_report": {
            "type": "User",
            "userID": 0,
            "reporter": 0,
            "reportReason": "The user is posting Spam",
            "date": "2022-06-07T15:57:45.901Z",
        },
        "new_subscription": {
            "endpoint": "https://fcm.googleapis.com/fcm/send/epyhl2GD",
            "expirationTime": None,
            "keys": {"p256dh": "fdsfd", "auth": "dfs"},
        },
    }

    return request_data


@pytest.fixture
def db_helpers_dummy_data() -> dict:
    """Dummy data for test_db_helpers"""
    dummy_data = {
        "DATETIME_PATTERN": DATETIME_PATTERN,
        "updated_post": {
            "id": 1,
            "userId": 1,
            "user": "shirb",
            "text": "new test",
            "date": datetime.strptime("2020-06-01 15:05:01.966", DATETIME_PATTERN),
            "givenHugs": 2,
            "sentHugs": [4],
        },
    }

    return dummy_data
