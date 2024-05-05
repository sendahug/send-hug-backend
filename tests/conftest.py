from datetime import datetime
from asyncio import current_task

import pytest
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import async_sessionmaker, async_scoped_session
from firebase_admin import initialize_app  # type: ignore

from create_app import create_app
from config import SAHConfig
from models.models import BaseModel
from models import SendADatabase
from tests.data_models import create_data, DATETIME_PATTERN, update_sequences


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
def test_config(session_mocker: MockerFixture):
    """Set up the config"""
    test_db_path = "postgresql+asyncpg://postgres:password@localhost:5432/test_sah"
    # TODO: We should at least make sure that this works with
    # an actual key.
    session_mocker.patch("config.initialize_app", return_value=initialize_app())
    session_mocker.patch("config.Certificate")
    yield SAHConfig(database_url=test_db_path)


@pytest.fixture(scope="function")
def app_client(test_config: SAHConfig):
    """Get the test client for the test app"""
    app = create_app(config=test_config)
    yield app.test_client()


@pytest.fixture(scope="session")
async def db(test_config: SAHConfig):
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
async def test_db(db: SendADatabase, mocker: MockerFixture):
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

        await update_sequences(db)

        await db.session.begin_nested()
        mocker.patch("pywebpush.webpush")
        mocker.patch("create_app.webpush")

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
            "auth0": "auth0|5ed34765f0b8e60c8e87ca62",
            "firebase_id": "abcd",
        },
        "moderator": {
            "internal": "5",
            "auth0": "auth0|5ede3e7a0793080013259050",
            "firebase_id": "efgh",
        },
        "admin": {
            "internal": "4",
            "auth0": "auth0|5ed8e3d0def75d0befbc7e50",
            "firebase_id": "ijkl",
        },
        "blocked": {"internal": "20", "auth0": "", "firebase_id": "twg"},
    }

    return user_data


@pytest.fixture
def dummy_request_data():
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
            "id": "auth0|5edf778e56d062001335196e",
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
def db_helpers_dummy_data():
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
