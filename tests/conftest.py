import os
import urllib.request
import json
from datetime import datetime

import pytest
from sh import pg_restore  # type: ignore

from create_app import create_app
from models import db

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN", "")
API_AUDIENCE = os.environ.get("API_AUDIENCE", "")
TEST_CLIENT_ID = os.environ.get("TEST_CLIENT_ID", "")
TEST_CLIENT_SECRET = os.environ.get("TEST_CLIENT_SECRET", "")
DATETIME_PATTERN = "%Y-%m-%d %H:%M:%S.%f"


@pytest.fixture(scope="session")
def user_headers():
    """
    Get Auth0 access tokens for each of the users to be able to run
    the tests.
    """
    headers = {"content-type": "application/x-www-form-urlencoded"}

    roles = ["user", "moderator", "admin", "blocked"]
    user_headers: dict[str, dict[str, str]] = {}

    for role in roles:
        url = f"https://{AUTH0_DOMAIN}/oauth/token"

        # Get the user's username and password
        role_username = os.environ.get(f"{role.upper()}_USERNAME", "")
        role_password = os.environ.get(f"{role.upper()}_PASSWORD", "")

        data = (
            f"grant_type=password&username={role_username}"
            f"&password={role_password}&audience={API_AUDIENCE}"
            f"&client_id={TEST_CLIENT_ID}&client_secret={TEST_CLIENT_SECRET}"
        )

        # make the request and get the token
        req = urllib.request.Request(url, data.encode("utf-8"), headers, method="POST")
        f = urllib.request.urlopen(req)
        response_data = f.read()
        token_data = response_data.decode("utf8").replace("'", '"')
        token = json.loads(token_data)["access_token"]
        # Set the authorisation headers with the newly fetched JWTs
        user_headers[role] = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        f.close()

    user_headers["malformed"] = {
        "Content-Type": "application/json",
        "Authorization": "Bearer",
    }

    return user_headers


@pytest.fixture()
def test_app():
    """Set up the test app"""
    test_db_path = "postgresql://postgres:password@localhost:5432/test_sah"
    app = create_app(db_path=test_db_path)
    yield app


@pytest.fixture()
def app_client(test_app):
    """Get the test client for the test app"""
    yield test_app.test_client()


@pytest.fixture(scope="function")
def test_db(test_app):
    """Restore the test database from the db snapshot"""
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
    with test_app.app_context():
        # create all tables
        db.create_all()

        try:
            yield db
        finally:
            db.session.close()


@pytest.fixture
def dummy_users_data():
    """Get the users' dummy data for the test"""
    # Sample users data
    user_data = {
        "user": {
            "internal": "1",
            "auth0": "auth0|5ed34765f0b8e60c8e87ca62",
        },
        "moderator": {
            "internal": "5",
            "auth0": "auth0|5ede3e7a0793080013259050",
        },
        "admin": {
            "internal": "4",
            "auth0": "auth0|5ed8e3d0def75d0befbc7e50",
        },
        "blocked": {
            "internal": "20",
            "auth0": "",
        },
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
            "date": "Sun Jun 07 2020 15:57:45",
            "givenHugs": 0,
        },
        "updated_post": {
            "userId": 0,
            "text": "test post",
            "date": "Sun Jun 07 2020 15:57:45",
            "givenHugs": 0,
        },
        "report_post": {
            "user_id": 0,
            "text": "test post",
            "date": "Sun Jun 07 2020 15:57:45",
            "givenHugs": 0,
            "closeReport": 1,
        },
        "new_user": {
            "id": "auth0|5edf778e56d062001335196e",
            "displayName": "user",
            "receivedH": 0,
            "givenH": 0,
            "loginCount": 0,
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
            "date": "Sun Jun 07 2020 15:57:45",
        },
        "new_report": {
            "type": "Post",
            "userID": 0,
            "postID": 0,
            "reporter": 0,
            "reportReason": "It is inappropriate",
            "date": "Sun Jun 07 2020 15:57:45",
        },
        "new_user_report": {
            "type": "User",
            "userID": 0,
            "reporter": 0,
            "reportReason": "The user is posting Spam",
            "date": "Sun Jun 07 2022 15:57:45",
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
            "sentHugs": ["4"],
        },
    }

    return dummy_data
