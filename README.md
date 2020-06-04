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


## Known Issues

There are no current issues at the time.
