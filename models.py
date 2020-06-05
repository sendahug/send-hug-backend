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
# Method: Joined_Query
# Description: Performs a joined query.
# Parameters: target (string) - the target variable + endpoint (or just
#             endpoint if they're the same).
def joined_query(target, params={}):
    return_obj = []

    # if the target is the recent_posts array in the main page endpoint
    if(target.lower() == 'main new'):
        new_posts = db.session.query(Post, User.display_name).join(User).\
                    order_by(db.desc(Post.date)).limit(10).all()

        # formats each post in the list
        for post in new_posts:
            post = {
                'id': post[0].id,
                'userId': post[0].user_id,
                'user': post[1],
                'text': post[0].text,
                'date': post[0].date,
                'givenHugs': post[0].given_hugs
            }
            return_obj.append(post)
    # if the target is the suggested_posts array in the main page endpoint
    elif(target.lower() == 'main suggested'):
        sug_posts = db.session.query(Post, User.display_name).join(User).\
                    order_by(Post.given_hugs).limit(10).all()

        # formats each post in the list
        for post in sug_posts:
            post = {
                'id': post[0].id,
                'userId': post[0].user_id,
                'user': post[1],
                'text': post[0].text,
                'date': post[0].date,
                'givenHugs': post[0].given_hugs
            }
            return_obj.append(post)
    # If the target is the full list of new items
    elif(target.lower() == 'full new'):
        full_new_posts = db.session.query(Post, User.display_name).join(User).\
                         order_by(db.desc(Post.date)).all()

        # formats each post in the list
        for post in full_new_posts:
            post = {
                'id': post[0].id,
                'userId': post[0].user_id,
                'user': post[1],
                'text': post[0].text,
                'date': post[0].date,
                'givenHugs': post[0].given_hugs
            }
            return_obj.append(post)
    # If the target is the full list of suggested items
    elif(target.lower() == 'full suggested'):
        full_sug_posts = db.session.query(Post, User.display_name).join(User).\
                    order_by(Post.given_hugs).all()

        # formats each post in the list
        for post in full_sug_posts:
            post = {
                'id': post[0].id,
                'userId': post[0].user_id,
                'user': post[1],
                'text': post[0].text,
                'date': post[0].date,
                'givenHugs': post[0].given_hugs
            }
            return_obj.append(post)
    # if the target is the user's messages (get messages endpoint)
    elif(target.lower() == 'messages'):
        user_id = params['user_id']

        from_user = db.aliased(User)
        for_user = db.aliased(User)

        user_messages = db.session.query(Message, from_user.display_name,
                                         for_user.display_name).\
            join(from_user, from_user.id == Message.from_id).\
            join(for_user, for_user.id == Message.for_id).all()

        # formats each message in the list
        for message in user_messages:
            message = {
                'id': message[0].id,
                'from': message[1],
                'fromId': message[0].from_id,
                'for': message[2],
                'forId': message[0].for_id,
                'messageText': message[0].text,
                'date': message[0].date
            }
            return_obj.append(message)

    return {
        'return': return_obj
    }


# Method: Add
# Description: Inserts a new record into the database.
# Parameters: Object to insert (User, Post or Message).
def add(obj):
    return_object = {}

    # Try to add the object to the database
    try:
        db.session.add(obj)
        db.session.commit()
        return_object = obj.format()
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
        updated_object = obj.format()
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
        db.session.commit()
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
