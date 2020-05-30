import os
from flask import abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Database configuration
databate_username = os.environ.get('DBUSERNAME')
database_name = 'capstone'
database_path = 'postgres://{}@localhost:5432/{}'.format(databate_username,
                                                         database_name)

db = SQLAlchemy()


# Database setup
def create_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate = Migrate(app, db)


# Models
# -----------------------------------------------------------------
# Post Model
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.String(480), nullable=False)
    date = db.Column(db.DateTime)
    given_hugs = db.Column(db.Integer, default=0)

    # Format method
    # Responsible for returning a JSON object
    def format(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'text': self.text,
            'date': self.date,
            'givenHugs': self.given_hugs
        }


# User Model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(), nullable=False)
    auth0_id = db.Column(db.String(), nullable=False)
    received_hugs = db.Column(db.Integer, default=0)
    given_hugs = db.Column(db.Integer, default=0)
    login_count = db.Column(db.Integer, default=1)
    posts = db.relationship('Post', backref='user')

    # Format method
    # Responsible for returning a JSON object
    def format(self):
        return {
            'id': self.id,
            'auth0Id':  self.auth0_id,
            'displayName': self.display_name,
            'receivedH': self.received_hugs,
            'givenH': self.given_hugs,
            'postsNum': self.posts,
            'loginCount': self.login_count
        }


# Message Model
class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    from_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    for_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.String(480), nullable=False)
    date = db.Column(db.DateTime)

    # Format method
    # Responsible for returning a JSON object
    def format(self):
        return {
            'id': self.id,
            'fromId': self.from_id,
            'forId': self.for_id,
            'messageText': self.text,
            'date': self.date
        }


# Database management methods
# -----------------------------------------------------------------
# Method: Add
# Description: Inserts a new record into the database.
# Parameters: Object to insert (User, Post or Message).
def add(obj):
    return_object = {}

    # Try to add the object to the database
    try:
        db.session.add(obj)
        db.session.commit()
        return_object = obj
    # If there's an error, rollback
    except Exception as e:
        db.session.rollback()
    # Close the connection once the attempt is complete
    finally:
        db.session.close()

    return jsonify({
        'success': True,
        'added': return_object
    })


# Method: Update
# Description: Updates an existing record.
# Parameters: Updated object (User, Post or Message).
def update(obj):
    updated_object = {}

    # Try to update the object in the database
    try:
        db.session.commit()
        updated_object = obj
    # If there's an error, rollback
    except Exception as e:
        db.session.rollback()
    # Close the connection once the attempt is complete
    finally:
        db.session.close()

    return jsonify({
        'success': True,
        'updated': updated_object
    })


# Method: Delete Object
# Description: Deletes an existing record.
# Parameters: Object (User, Post or Message) to delete.
def delete_object(obj):
    deleted = None

    # Try to delete the record from the database
    try:
        db.session.delete(obj)
        deleted = obj.id
    # If there's an error, rollback
    except Exception as e:
        db.session.rollback()
    # Close the connection once the attempt is complete
    finally:
        db.session.close()

    return jsonify({
        'success': True,
        'deleted': deleted
    })
