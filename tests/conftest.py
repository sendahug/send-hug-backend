import os
import urllib.request
import json

import pytest
from sh import pg_restore  # type: ignore

from create_app import create_app
from models import db

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN", "")
API_AUDIENCE = os.environ.get("API_AUDIENCE", "")
TEST_CLIENT_ID = os.environ.get("TEST_CLIENT_ID", "")
TEST_CLIENT_SECRET = os.environ.get("TEST_CLIENT_SECRET", "")


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
    """ """
    test_db_path = "postgresql://postgres:password@localhost:5432/test_sah"
    app = create_app(db_path=test_db_path)
    yield app


@pytest.fixture()
def app_client(test_app):
    """ """
    yield test_app.test_client()


@pytest.fixture(scope="function")
def test_db(test_app):
    """ """
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
