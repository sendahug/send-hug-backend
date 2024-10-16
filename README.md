# Send A Hug

[![CircleCI](https://circleci.com/gh/sendahug/send-hug-backend.svg?style=shield)](https://circleci.com/gh/sendahug/send-hug-backend)
[![codecov](https://codecov.io/gh/sendahug/send-hug-backend/graph/badge.svg)](https://codecov.io/gh/sendahug/send-hug-backend)
[![Known Vulnerabilities](https://snyk.io/test/github/sendahug/send-hug-backend/badge.svg)](https://snyk.io/test/github/sendahug/send-hug-backend)
![Libraries.io dependency status for GitHub repo](https://img.shields.io/librariesio/github/sendahug/send-hug-backend)

## Version

Version 1 (currently in development).

For full API documentation, check the [`API Docs`](./api_docs.md).

For full project information, check the [`main README file`](https://github.com/sendahug/sendahug/blob/master/README.md).

## Code Usage and Contribution

If you want to contribute to the project, you should start by reading the [contribution guidelines](https://github.com/sendahug/send-hug-backend/blob/dev/CONTRIBUTING.md) and the [code of conduct](https://github.com/sendahug/send-hug-backend/blob/dev/CODE_OF_CONDUCT.md).

The project is open source, so feel free to use parts of the code. However, the full project itself is **not** meant to be reused. The design, the concept and the project itself are personal and belong to the Send A Hug group.

## Installation and Usage (Local Development)

### Requirements

- Python 3.11+
- Postgres 13

### Developers

1. Download or clone the repo.
2. cd into the project directory.
3. cd into backend.
4. Run ```pip install -r requirements.txt -r dev_requirements.txt``` to install dependencies.
5. Run ```pre-commit install``` to install and initialise pre-commit.
6. Create a database for the app.
7. Set the required environment variables:
    - The database URI is built in the config using the following environment variables:
      - **DB_CREDENTIALS_PATH** - The path to the credentials file.
      - **DATABASE_USERNAME** - The username to log into the database if no credentials file is set.
      - **DATABASE_PASSWORD** - The password to log into the database if no credentials file is set.
    - **PRIVATE_VAPID_KEY** - environment variable containing your private VAPID key (required for push notifications).
    - The frontend URI comes from an environment variable named **FRONTEND**.
    - The firebase credentials file's location is in an environment variable called **FIREBASE_CREDENTIALS_FILE**.
8. Update your database using ```alembic upgrade head```
9. Run Quart with:
    - ```export QUART_APP=app.py```
    - ```quart --debug run```

### Users

**Not yet ready for users!**

## Contents

The app contains several files and folders:

1. **app.py** - The main application file. Simply generates and runs the app.
2. **create_app.py** - Contains the app's content. This file contains all endpoints and error handlers.
3. **filter.py** - The system responsible for filtering words. (Work in progress)
4. **manage.py** - The file managing running database migrations when deploying.
5. **models** - The folder containing SQLAlchemy models, as well as all database-related methods.
6. **auth.py** - The file dealing with authentication - getting the Authorization header, verifying the JWT and confirming the user has the required permission.
7. **tests** - The folder containing the backend's test suite.

## Dependencies

The site uses several tools to maximise compatibility:

1. **Quart** - Quart is a Python microframework used to build and run the local server on which the app is running. As Quart is an async reimplementation of Flask, its API is mostly the same as Flask's. For full Quart documentation, try the [Quart website](https://quart.palletsprojects.com/en/latest/).

2. **SQLAlchemy** - This application uses the SQLAlchemy ORM in order to interact with the database. You can read more about SQLAlchemy (including API documentation) on the [SQLAlchemy website](https://docs.sqlalchemy.org/en/20/contents.html).

3. **Alembic** - This application uses Alembic, a database migration tool made by the SQLAlchemy team, in order to manage model versions. You can read more on the [Alembic docs](https://alembic.sqlalchemy.org).

4. **Quart-CORS** - This application uses Quart-CORS in order to enable communication from the frontend. You can read more about it in the [Quart-CORS repository](https://github.com/pgjones/quart-cors).

5. **Firebase-Admin** - This application uses firebase-admin in order to decode and verify the authenticity of a given JWT (see Contents -> auth.py). You can read more on the [Firebase SDK API docs](https://firebase.google.com/docs/reference/admin).

6. **PyWebPush** - This application uses pywebpush in order to handle push notifications. For more information, check their [GitHub repo](https://github.com/web-push-libs/pywebpush).

7. **Coverage** - This application uses coverage in order to provide code coverage for testing. For more information, check the [Coverage documentation](https://coverage.readthedocs.io/en/coverage-5.2.1/).

## Authentication

The project uses Firebase as a third-party authentication provider. Authentication is done by Firebase, which in turn returns a JSON Web Token containing the user's data and permissions.

Decoding and verifying the token is done by [`auth.py`](./auth.py), in three stages:

1. The server gets the Authorization header from the request and ensures that it exists and is in the right form. (Done by the `get_auth_header` function.)

2. The server uses the Firebase SDK to decode and verify the token. (Done by the `validate_token` function.)

3. Once the JWT is decoded and verified, the user's data (including permissions) is fetched from the back-end (done by the `get_current_user` function). Each endpoint that requires authorisation contains a string, which is then compared to the user's permissions. (Done by the `check_user_permissions` function.)
  - There's one exception to this, which is the `POST /users` endpoint. Since at that point the user doesn't exist in the internal database yet, fetching the permissions would fail. This endpoint is the only endpoint that requires authentication but no authorisation. This allows them to create a user, which is then used for all subsequent visits.

Endpoints that require authorisation are marked with the `@requires_auth` decorator. The function creating the decorator is written in full in [`auth.py`](./auth.py).

In case the user's authorisation header is malformed, their JWT is invalid in any way, or they don't have the required permission, the server raises an AuthError. The error handler is defined in full with the rest of the error handlers, in [`app.py`](./app.py).

## Testing

This project utilises Pytest for testing.

### Running Tests

Once you've completed the setup for whichever approach you've chosen, run the following commands:

```
"CREATE DATABASE test_sah;" | sudo -u postgres psql
pytest
```

Or, if using macOS:
```
dropdb test_sah && createdb test_sah
pytest
```

## Known Issues

There are no current issues at the time.
