from asyncio import current_task
from datetime import datetime
import os
from os import listdir, path
from typing import AsyncGenerator, Generator

import pytest
from pytest_mock import MockerFixture
from quart.typing import TestClientProtocol
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_scoped_session, async_sessionmaker

from tests.data_models import DATETIME_PATTERN, create_data, update_sequences

from models import SendADatabase
from models.common import BaseModel

# TODO: depcrate the below once we update docs with how to use
# db_development_creds/latest.json for development
DATABASE_USERNAME = os.environ.get("DATABASE_USERNAME", "")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD", "")


@pytest.fixture(scope="session")
def user_headers(session_mocker: MockerFixture) -> dict[str, dict[str, str]]:
    """
    Sets the headers for each of the users and mocks
    the verify_id_token function from Firebase.
    """
    roles = ["user", "moderator", "admin", "blocked", "newUserRole", "actualNewUser"]
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
        if "newUserRole" in token:
            return {"uid": "123456", "email_verified": True, "email": "email"}
        elif "user" in token:
            return {"uid": "abcd", "email_verified": True, "email": "email"}
        elif "moderator" in token:
            return {"uid": "efgh", "email_verified": False, "email": "email"}
        elif "blocked" in token:
            return {"uid": "twg", "email_verified": False, "email": "email"}
        elif "actualNewUser" in token:
            return {"uid": "actualNewUser", "email_verified": False, "email": "email"}
        else:
            return {"uid": "ijkl", "email_verified": False, "email": "email"}

    session_mocker.patch("auth.verify_id_token", new=verify_token)

    return user_headers


@pytest.fixture(scope="session")
def certificate_mocker(
    session_mocker: MockerFixture,
) -> None:
    """Mocks the get_certificate helper"""
    session_mocker.patch("config.sah_config.get_certificate", return_value=None)


@pytest.fixture(scope="function")
def app_client(
    certificate_mocker, mocker: MockerFixture
) -> Generator[TestClientProtocol, None, None]:
    """Get the test client for the test app"""
    # we import here as we need to mock the firebase certficate because CircleCI
    # does not have access to the firebase credentials file
    from create_app import create_app

    app = create_app()

    yield app.test_client()


@pytest.fixture(scope="session")
async def db() -> AsyncGenerator[SendADatabase, None]:
    """Creates the database and inserts the test data."""
    db = SendADatabase(
        database_url=URL.create(
            drivername="postgresql+asyncpg",
            username=DATABASE_USERNAME,
            password=DATABASE_PASSWORD,
            host="localhost",
            port=5432,
            database="test_sah",
        )
    )

    try:
        async with db.engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.drop_all)
            await conn.run_sync(BaseModel.metadata.create_all)

        await create_data(db)

        await db.engine.dispose()

        yield db

    finally:
        async with db.engine.begin() as conn:
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

        # Mock the session for all controllers
        # TODO: Surely there's a better way to do this
        controllers = listdir(path.join(path.dirname(__file__), "../controllers"))
        non_controllers = ["__init__.py", "common.py", "__pycache__"]
        for controller in controllers:
            if controller in non_controllers:
                continue

            mocker.patch(
                f"controllers.{controller[:-3]}.sah_config.db.session",
                new_callable=get_scoped_session,
            )

        await update_sequences(db)

        await db.session.begin_nested()
        mocker.patch("pywebpush.webpush")
        mocker.patch("controllers.common.webpush")

        yield db

    finally:
        # Delete the session
        await db.session.remove()

        # Rollback the transaction and return the connection to the pool
        await transaction.rollback()
        await connection.close()
        await db.engine.dispose()


@pytest.fixture
def dummy_users_data() -> dict[str, dict[str, str]]:
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
        "blocked": {"internal": "17", "firebase_id": "twg"},
        "new": {"internal": "19", "firebase_id": "123456"},
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
        "updated_notifications": {
            "notification_ids": [],
            "read": True,
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
            "archived": False,
        },
    }

    return dummy_data
