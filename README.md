# APP

## Version

Version 1 (currently in development).

For full API documentation, check the [`API Docs`](./api_docs.md)

## Requirements

- Python 3

## Installation and Usage

### Developers

1. Download or clone the repo.
2. cd into the project directory.
3. cd into backend.
4. Run ```pip install -r requirements.txt``` to install dependencies.
5. Update the database URI to match your system.
  - The username is stored in an environment variable.
6. Run flask with:
  - ```export FLASK_APP=app.py```
  - ```export FLASK_ENV=development``` (Recommended)
  - ```flask run```
7. Update your database using ```flask migrate upgrade```

### Users

**Not yet ready for users!**

## Contents

The app contains several files and folders:

1. **app.py** - The main application file. This file contains all endpoints and error handlers.
2. **models.py** - The file containing SQLAlchemy models, as well as all database-related methods.
3. **auth.py** - The file dealing with authentication - getting the Authorization header, verifying the JWT and confirming the user has the required permission.
4. **test_app.py** - The file containing the backend's test suite.

## Dependencies

The site uses several tools to maximise compatibility:

1. **Flask** - Flask is a microframework used to build and run the local server on which the app is running. For full Flask documentation, try the [Flask website](https://flask.palletsprojects.com/en/1.1.x/). Flask is a Python framework, so it requires installing Python (or Python3).

2. **Flask-SQLAlchemy** - This application uses the SQLAlchemy ORM in order to interact with the database, using the Flask-SQLAlchemy extension. You can read more about SQLAlchemy (including API documentation) on the [SQLAlchemy website](https://docs.sqlalchemy.org/en/13/), and about Flask-SQLAlchemy on the [Flask-SQLAlchemy website](https://flask-sqlalchemy.palletsprojects.com/en/2.x/).

3. **Flask-Migrate** - This application uses Flask-Migrate in order to manage model versions. You can read more on the [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/) website.

4. **Flask-CORS** - This application uses Flask-CORS in order to enable communication from the frontend. You can read more on the [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/) website.

5. **Python-Jose** - This application uses Python-Jose in order to decode and verify the authenticity of a given JWT (see Contents -> auth.py). You can read more on the [Python-Jose](https://python-jose.readthedocs.io/en/latest/) website.

## Authentication

The project uses Auth0 as a third-party authentication provider. Authentication is done by Auth0, which in turn returns a JSON Web Token containing the user's data and permissions.

Decoding and verifying the token is done by [`auth.py`](./auth.py), in three stages:

1. The server gets the Authorization header from the request and ensures that it exists and is in the right form. (Done by the `get_auth_header()` function.)

2. The server uses Jose to decode and verify the token. (Done by the `verify_jwt()` function.)

3. Once the JWT is decoded and verified, the user's permissions (taken from the token payload) are checked. Each endpoint that requires authorisation contains a string, which is then compared to the user's permissions. (Done by the `check_permissions()` function.)

Endpoints that require authorisation are marked with the `@requires_auth` decorator. The function creating the decorator is written in full in [`auth.py`](./auth.py).

In case the user's authorisation header is malformed, their JWT is invalid in any way, or they don't have the required permission, the server raises an AuthError. The error handler is defined in full with the rest of the error handlers, in [`app.py`](./app.py).

## Testing

This project utilises unittest for testing. In order to run project tests, run the following commands:

```
dropdb test-capstone && createdb test-capstone
psql test-capstone < capstone_db.sql
python test_app.py
```

Or, if using MacOS:
```
dropdb test-capstone && createdb test-capstone
psql test-capstone < capstone_db.sql
python3 test_app.py
```

## Known Issues

There are no current issues at the time.
