# Send A Hug

## Version

Version 1 (currently in development).

For full API documentation, check the [`API Docs`](./api_docs.md).

For full project information, check the [`main README file`](https://github.com/sendahug/sendahug/blob/master/README.md).

## Requirements

- Python 3

## Installation and Usage (Local Development)

### Developers

1. Download or clone the repo.
2. cd into the project directory.
3. cd into backend.
4. Run ```pip install -r requirements.txt``` to install dependencies.
5. Update the database URI to match your system.
  - The database URI comes from an environment variable named **DATABASE_URL**.
6. Set Auth0 configuration variables:
  - AUTH0_DOMAIN - environment variable containing your Auth0 domain.
  - API_AUDIENCE - environment variable containing your Auth0 API audience.
7. Set up your frontend URI.
  - The frontend URI comes from an environment variable named **FRONTEND**.
7. Update your database using ```flask migrate upgrade```
8. Run flask with:
  - ```export FLASK_APP=app.py```
  - ```export FLASK_ENV=development``` (Recommended)
  - ```flask run```

### Users

**Not yet ready for users!**

## Contents

The app contains several files and folders:

1. **app.py** - The main application file. This file contains all endpoints and error handlers.
2. **filter.py** - The system responsible for filtering words. (Work in progress)
3. **manage.py** - The file managing running database migrations when deploying.
4. **models.py** - The file containing SQLAlchemy models, as well as all database-related methods.
5. **auth.py** - The file dealing with authentication - getting the Authorization header, verifying the JWT and confirming the user has the required permission.
6. **test_app.py** - The file containing the backend's test suite.

## Dependencies

The site uses several tools to maximise compatibility:

1. **Flask** - Flask is a microframework used to build and run the local server on which the app is running. For full Flask documentation, try the [Flask website](https://flask.palletsprojects.com/en/1.1.x/). Flask is a Python framework, so it requires installing Python (or Python3).

2. **Flask-SQLAlchemy** - This application uses the SQLAlchemy ORM in order to interact with the database, using the Flask-SQLAlchemy extension. You can read more about SQLAlchemy (including API documentation) on the [SQLAlchemy website](https://docs.sqlalchemy.org/en/13/), and about Flask-SQLAlchemy on the [Flask-SQLAlchemy website](https://flask-sqlalchemy.palletsprojects.com/en/2.x/).

3. **Flask-Migrate** - This application uses Flask-Migrate in order to manage model versions. You can read more on the [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/) website.

4. **Flask-CORS** - This application uses Flask-CORS in order to enable communication from the frontend. You can read more on the [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/) website.

5. **Python-Jose** - This application uses Python-Jose in order to decode and verify the authenticity of a given JWT (see Contents -> auth.py). You can read more on the [Python-Jose](https://python-jose.readthedocs.io/en/latest/) website.

6. **Wordfilter** - This application uses the Wordfilter module in order to handle word filtering. You can read about it more on the module's [PyPI page](https://pypi.org/project/wordfilter/).

7. **PyWebPush** - This application uses pywebpush in order to handle push notifications. For more information, check their [GitHub repo](https://github.com/web-push-libs/pywebpush).

8. **sh** - This application uses sh during testing (in order to handle the database). For more information, check the [sh PyPi page](https://pypi.org/project/sh/).

## Authentication

The project uses Auth0 as a third-party authentication provider. Authentication is done by Auth0, which in turn returns a JSON Web Token containing the user's data and permissions.

Decoding and verifying the token is done by [`auth.py`](./auth.py), in three stages:

1. The server gets the Authorization header from the request and ensures that it exists and is in the right form. (Done by the `get_auth_header()` function.)

2. The server uses Jose to decode and verify the token. (Done by the `verify_jwt()` function.)

3. Once the JWT is decoded and verified, the user's permissions (taken from the token payload) are checked. Each endpoint that requires authorisation contains a string, which is then compared to the user's permissions. (Done by the `check_permissions()` function.)

Endpoints that require authorisation are marked with the `@requires_auth` decorator. The function creating the decorator is written in full in [`auth.py`](./auth.py).

In case the user's authorisation header is malformed, their JWT is invalid in any way, or they don't have the required permission, the server raises an AuthError. The error handler is defined in full with the rest of the error handlers, in [`app.py`](./app.py).

## Testing

This project utilises unittest for testing. In order to run project tests, you need to set up the following environment variables:

1. USER_JWT - JWT of a user with the role of a user.
2. MOD_JWT - JWT of a user with the role of a moderator.
3. ADMIN_JWT - JWT of a user with the role of an admin.
4. BLOCKED_JWT - JWT of a user who's currently blocked.

Then, run the following commands:

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

## Hosting

The project is hosted live on Heroku. You can view the live version [here](https://send-hug-server.herokuapp.com/). If you want to clone and host your own version, you can do so by using the following guide (the following commands are for Heroku, but they can be adjusted depending on your host):

  1. Create a Heroku account (skip this step if you already have an account).
  2. Install the Heroku command line interface.
  3. In your Terminal, enter `heroku login`. This triggers logging in via the CLI.
  4. Enter `heroku create <APP_NAME>` (with your own app name). If successful, Heroku returns the live version's URL (will be referred to as <LIVE_URL>) and the Git repo link (will be referred to as <GIT_URL>).
  5. Enter `heroku addons:create heroku-postgresql:hobby-dev --app <APP_NAME>`. This creates a Postgres database for your app. Change 'hobby-dev' to another tier if you want to use the app with a paid tier (depending on your needs; for more information check the [Heroku guide](https://devcenter.heroku.com/articles/heroku-postgres-plans)).
  6. Make sure you're in the top directory (FSND-capstone). In your terminal, enter `git remote add heroku-server <GIT_URL>`.
  7. Enter `git subtree push --prefix backend heroku-server master`. This triggers the app build. If successful, you'll get a 'Verifying deploy... done.' message.
  8. Add the following environment variables (via CLI or via the Heroku website):
    - API_AUDIENCE - set with your own API audience from Auth0
    - AUTH0_DOMAIN - set with your own Auth0 domain
    - CLIENT_ID - set with your own client ID from Auth0
    - FRONTEND - set with your own frontend URL (necessary for setting up CORS!)
    - PRIVATE_KEY - The private VAPID key (required for sending push notifications).
  9. Enter `heroku run python manage.py db upgrade --app <APP_NAME>` to trigger database migrations and bring your live database up to date.
  10. All done! Now you can visit your <GIT_URL> to see the live app.

## Known Issues

There are no current issues at the time.
