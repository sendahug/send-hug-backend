import os
from flask import abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Database configuration
database_path = os.environ.get('DATABASE_URL')

db = SQLAlchemy()


# Database setup
def create_db(app, db_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = db_path
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
    role = db.Column(db.String(), default='user')
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
            'loginCount': self.login_count,
            'role': self.role
        }


# Message Model
class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    from_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    for_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.String(480), nullable=False)
    date = db.Column(db.DateTime)
    thread = db.Column(db.Integer, db.ForeignKey('threads.id'), nullable=False)

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


# Thread Model
class Thread(db.Model):
    __tablename__ = 'threads'
    id = db.Column(db.Integer, primary_key=True)
    user_1_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                          nullable=False)
    user_2_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                          nullable=False)
    messages = db.relationship('Message', backref='threads')

    # Format method
    # Responsible for returning a JSON object
    def format(self):
        return {
            'id': self.id,
            'user1': self.user_1_id,
            'user2': self.user_2_id
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
        type = params['type']
        thread = params['thread_id']

        from_user = db.aliased(User)
        for_user = db.aliased(User)

        # Checks which mailbox the user is requesting
        # For inbox, gets all incoming messages
        if(type == 'inbox'):
            user_messages = db.session.query(Message, from_user.display_name,
                                             for_user.display_name).\
                join(from_user, from_user.id == Message.from_id).\
                join(for_user, for_user.id == Message.for_id).\
                filter(Message.for_id == user_id).all()
        # For outbox, gets all outgoing messages
        elif(type == 'outbox'):
            user_messages = db.session.query(Message, from_user.display_name,
                                             for_user.display_name).\
                join(from_user, from_user.id == Message.from_id).\
                join(for_user, for_user.id == Message.for_id).\
                filter(Message.from_id == user_id).all()
        # For threads, gets all threads' data
        elif(type == 'threads'):
            # Get the thread ID, messages count, and users' names and IDs
            threads_messages = db.session.query(db.func.count(Message.id),
                                                Message.thread,
                                                from_user.display_name,
                                                for_user.display_name,
                                                Thread.user_1_id,
                                                Thread.user_2_id).\
                join(Thread, Message.thread == Thread.id).\
                join(from_user, from_user.id == Thread.user_1_id).\
                join(for_user, for_user.id == Thread.user_2_id).\
                group_by(Message.thread, from_user.display_name,
                         for_user.display_name, Thread.user_1_id,
                         Thread.user_2_id, Thread.id).order_by(Thread.id).\
                filter((Thread.user_1_id == user_id) |
                       (Thread.user_2_id == user_id)).all()

            # Get the date of the latest message in the thread
            latest_message = db.session.query(db.func.max(Message.date),
                                              Message.thread).\
                join(Thread, Message.thread == Thread.id).\
                group_by(Message.thread, Thread.user_1_id, Thread.user_2_id).\
                order_by(Message.thread).\
                filter((Thread.user_1_id == user_id) |
                       (Thread.user_2_id == user_id)).all()
        # Gets a specific thread's messages
        elif(type == 'thread'):
            user_messages = db.session.query(Message, from_user.display_name,
                                             for_user.display_name).\
                join(from_user, from_user.id == Message.from_id).\
                join(for_user, for_user.id == Message.for_id).\
                filter(Message.thread == thread).all()

        # If the mailbox type is outbox or inbox
        if((type == 'outbox') or (type == 'inbox') or (type == 'thread')):
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
        # Otherwise the type is threads
        else:
            # Threads data formatting
            for index, thread in enumerate(threads_messages):
                thread = {
                    'id': thread[1],
                    'user1': thread[2],
                    'user1Id': thread[4],
                    'user2': thread[3],
                    'user2Id': thread[5],
                    'numMessages': thread[0],
                    'latestMessage': latest_message[index][0]
                    }
                return_obj.append(thread)
    # if the target is posts search (for the search endpoint)
    elif(target.lower() == 'post search'):
        search_query = params['query']
        posts = db.session.query(Post, User.display_name).join(User).\
            order_by(db.desc(Post.date)).filter(Post.text.like('%' +
                                                search_query + '%')).all()

        # Formats the posts
        for post in posts:
            post = {
                'id': post[0].id,
                'userId': post[0].user_id,
                'user': post[1],
                'text': post[0].text,
                'date': post[0].date,
                'givenHugs': post[0].given_hugs
            }
            return_obj.append(post)

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
        # If the object to delete is a thread, delete all associated
        # messages first
        if(type(obj) is Thread):
            db.session.query(Message).filter(Message.thread == obj.id).delete()

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


# Method: Delete All
# Description: Deletes all records that match a condition.
# Parameters: Type - type of item to delete (posts or messages)
#             ID - ID of the user whose posts or messages need to be deleted.
def delete_all(type, id):
    # Try to delete the records
    try:
        # If the type of objects to delete is posts, the ID is the
        # user ID whose posts need to be deleted
        if(type == 'posts'):
            db.session.query(Post).filter(Post.user_id == id).delete()
        # If the type of objects to delete is inbox, delete all messages
        # for the user with that ID
        if(type == 'inbox'):
            db.session.query(Message).filter(Message.for_id == id).delete()
        # If the type of objects to delete is outbox, delete all messages
        # from the user with that ID
        if(type == 'outbox'):
            db.session.query(Message).filter(Message.from_id == id).delete()
        # If the type of objects to delete is threads, delete all messages
        # to and from the user with that ID
        if(type == 'threads'):
            # Get all threads in which the user is involved
            Threads = db.session.query(Thread).filter((Thread.user_1_id == id)
                                                      or (Thread.user_2_id ==
                                                      id)).all()
            # Delete the messages in each thread
            for thread in Threads:
                db.session.query(Message).filter(Message.thread ==
                                                 thread.id).delete()

            # Then try to delete the threads
            db.session.query(Thread).filter((Thread.user_1_id == id) or
                                            (Thread.user_2_id == id)).delete()

        db.session.commit()
    # If there's an error, rollback
    except Exception as e:
        db.session.rollback()
    # Close the connection once the attempt is complete
    finally:
        db.session.close()

    return jsonify({
        'success': True,
        'deleted': type
    })
