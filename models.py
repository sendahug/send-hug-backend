import os
from datetime import datetime
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
    open_report = db.Column(db.Boolean, nullable=False, default=False)
    report = db.relationship('Report', backref='post')

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
    blocked = db.Column(db.Boolean, nullable=False, default=False)
    release_date = db.Column(db.DateTime)
    open_report = db.Column(db.Boolean, nullable=False, default=False)
    last_notifications_read = db.Column(db.DateTime)
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
            'role': self.role,
            'blocked': self.blocked,
            'releaseDate': self.release_date
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
    from_deleted = db.Column(db.Boolean, nullable=False, default=False)
    for_deleted = db.Column(db.Boolean, nullable=False, default=False)

    # Format method
    # Responsible for returning a JSON object
    def format(self):
        return {
            'id': self.id,
            'fromId': self.from_id,
            'forId': self.for_id,
            'messageText': self.text,
            'date': self.date,
            'threadID': self.thread
        }


# Thread Model
class Thread(db.Model):
    __tablename__ = 'threads'
    id = db.Column(db.Integer, primary_key=True)
    user_1_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                          nullable=False)
    user_2_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                          nullable=False)
    user_1_deleted = db.Column(db.Boolean, nullable=False, default=False)
    user_2_deleted = db.Column(db.Boolean, nullable=False, default=False)
    messages = db.relationship('Message', backref='threads')

    # Format method
    # Responsible for returning a JSON object
    def format(self):
        return {
            'id': self.id,
            'user1': self.user_1_id,
            'user2': self.user_2_id
        }


# Report Model
class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    reporter = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    report_reason = db.Column(db.String(480), nullable=False)
    date = db.Column(db.DateTime)
    dismissed = db.Column(db.Boolean, nullable=False, default=False)
    closed = db.Column(db.Boolean, nullable=False, default=False)

    # Format method
    # Responsible for returning a JSON object
    def format(self):
        # If the report was for a user
        if(self.type.lower() == 'user'):
            return_report = {
                'id': self.id,
                'type': self.type,
                'userID': self.user_id,
                'reporter': self.reporter,
                'reportReason': self.report_reason,
                'date': self.date,
                'dismissed': self.dismissed,
                'closed': self.closed
            }
        # If the report was for a post
        elif(self.type.lower() == 'post'):
            return_report = {
                'id': self.id,
                'type': self.type,
                'userID': self.user_id,
                'postID': self.post_id,
                'reporter': self.reporter,
                'reportReason': self.report_reason,
                'date': self.date,
                'dismissed': self.dismissed,
                'closed': self.closed
            }

        return return_report


# Notification Model
class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    for_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    from_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(), nullable=False)
    text = db.Column(db.String(), nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    # Format method
    def format(self):
        return {
            'id': self.id,
            'fromId': self.from_id,
            'forId': self.for_id,
            'date': self.date
        }

# Notification Subscription Model
class NotificationSub(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    endpoint = db.Column(db.String(), nullable=False)
    subscription_data = db.Column(db.Text, nullable=False)

    # Format method
    def format(self):
        return {
            'id': self.id,
            'user_id': self.user,
            'endpoint': self.endpoint,
            'subscription_data': self.subscription_data
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
                    order_by(db.desc(Post.date)).\
                    filter(Post.open_report == False).limit(10).all()

        # formats each post in the list
        for post in new_posts:
            new_post = post[0].format()
            new_post['user'] = post[1]
            return_obj.append(new_post)
    # if the target is the suggested_posts array in the main page endpoint
    elif(target.lower() == 'main suggested'):
        sug_posts = db.session.query(Post, User.display_name).join(User).\
                    order_by(Post.given_hugs).\
                    filter(Post.open_report == False).limit(10).all()

        # formats each post in the list
        for post in sug_posts:
            sug_post = post[0].format()
            sug_post['user'] = post[1]
            return_obj.append(sug_post)
    # If the target is the full list of new items
    elif(target.lower() == 'full new'):
        full_new_posts = db.session.query(Post, User.display_name).join(User).\
                         order_by(db.desc(Post.date)).\
                         filter(Post.open_report == False).all()

        # formats each post in the list
        for post in full_new_posts:
            new_post = post[0].format()
            new_post['user'] = post[1]
            return_obj.append(new_post)
    # If the target is the full list of suggested items
    elif(target.lower() == 'full suggested'):
        full_sug_posts = db.session.query(Post, User.display_name).join(User).\
                    order_by(Post.given_hugs).\
                    filter(Post.open_report == False).all()

        # formats each post in the list
        for post in full_sug_posts:
            sug_post = post[0].format()
            sug_post['user'] = post[1]
            return_obj.append(sug_post)
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
                filter(Message.for_deleted == False).\
                filter(Message.for_id == user_id).all()
        # For outbox, gets all outgoing messages
        elif(type == 'outbox'):
            user_messages = db.session.query(Message, from_user.display_name,
                                             for_user.display_name).\
                join(from_user, from_user.id == Message.from_id).\
                join(for_user, for_user.id == Message.for_id).\
                filter(Message.from_deleted == False).\
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
                filter(((Thread.user_1_id == user_id) &
                        (Thread.user_1_deleted == False)) |
                       ((Thread.user_2_id == user_id) &
                        (Thread.user_2_deleted == False))).all()

            # Get the date of the latest message in the thread
            latest_message = db.session.query(db.func.max(Message.date),
                                              Message.thread).\
                join(Thread, Message.thread == Thread.id).\
                group_by(Message.thread, Thread.user_1_id, Thread.user_2_id).\
                order_by(Message.thread).\
                filter(((Thread.user_1_id == user_id) &
                        (Thread.user_1_deleted == False)) |
                       ((Thread.user_2_id == user_id) &
                        (Thread.user_2_deleted == False))).all()
        # Gets a specific thread's messages
        elif(type == 'thread'):
            user_messages = db.session.query(Message, from_user.display_name,
                                             for_user.display_name).\
                join(from_user, from_user.id == Message.from_id).\
                join(for_user, for_user.id == Message.for_id).\
                filter(((Message.for_id == user_id) &
                        (Message.for_deleted == False)) |
                       ((Message.from_id == user_id) &
                        (Message.from_deleted == False))).\
                filter(Message.thread == thread).all()

        # If the mailbox type is outbox or inbox
        if((type == 'outbox') or (type == 'inbox') or (type == 'thread')):
            # formats each message in the list
            for message in user_messages:
                user_message = message[0].format()
                user_message['from'] = message[1]
                user_message['for'] = message[2]
                return_obj.append(user_message)
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
                                                search_query + '%')).\
            filter(Post.open_report == False).all()

        # Formats the posts
        for post in posts:
            searched_post = post[0].format()
            searched_post['user'] = post[1]
            return_obj.append(searched_post)
    # If the target is user reports (admin dashboard)
    elif(target.lower() == 'user reports'):
        reports = db.session.query(Report, User.display_name).\
            join(User, User.id == Report.user_id).\
            filter(Report.closed == False).filter(Report.type == 'User').\
            order_by(db.desc(Report.date)).all()

        # Formats the reports
        for report in reports:
            formatted_report = report[0].format()
            formatted_report['displayName'] = report[1]
            return_obj.append(formatted_report)
    # If the target is post reports (admin dashboard)
    elif(target.lower() == 'post reports'):
        reports = db.session.query(Report, Post.text).join(Post).\
            filter(Report.closed == False).filter(Report.type == 'Post').\
            order_by(db.desc(Report.date)).all()

        # Formats the reports
        for report in reports:
            formatted_report = report[0].format()
            formatted_report['text'] = report[1]
            return_obj.append(formatted_report)
    # If the target is notifications
    elif(target.lower() == 'notifications'):
        user_id = params['user_id']
        last_read = params['last_read']

        # If there's no last_read date, it means the user never checked
        # their notifications, so set it to the time this feature was added
        if(last_read is None):
            last_read = datetime(2020, 7, 1, 12, 00)

        from_user = db.aliased(User)
        for_user = db.aliased(User)

        # Gets all new notifications
        notifications = db.session.query(Notification, from_user.display_name,
                                             for_user.display_name).\
            join(from_user, from_user.id == Notification.from_id).\
            join(for_user, for_user.id == Notification.for_id).\
            filter(Notification.for_id == user_id).\
            filter(Notification.date > last_read).\
            order_by(Notification.date).all()

        # Formats all new messages
        for notification in notifications:
            user_notification = notification[0].format()
            user_notification['from'] = notification[1]
            user_notification['for'] = notification[2]
            return_obj.append(user_notification)

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
def update(obj, params={}):
    updated_object = {}

    # Try to update the object in the database
    try:
        # If the item to update is a thread and 'set_deleted' appears in
        # params, this means the messages in the thread need to be updated
        # as deleted
        if(type(obj) == Thread and 'set_deleted' in params):
            # Just in case, makes sure that set_deleted was set to true
            if(params['set_deleted']):
                messages_for = db.session.query(Message).\
                                filter(Message.thread == obj.id).\
                                filter(Message.for_id == params['user_id']).\
                                filter(Message.from_deleted == False).all()
                messages_from = db.session.query(Message).\
                    filter(Message.thread == obj.id).\
                    filter(Message.from_id == params['user_id']).\
                    filter(Message.for_deleted == False).all()

                # For each message that wasn't deleted by the other user, the
                # value of for_deleted (indicating whether the user the message
                # is for deleted it) is updated to True
                for message in messages_for:
                    message.for_deleted = True

                # For each message that wasn't deleted by the other user, the
                # value of from_deleted (indicating whether the user who wrote
                # the message deleted it) is updated to True
                for message in messages_from:
                    message.from_deleted = True

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
            # Separates messages that were deleted by the other user (and are
            # thus okay to delete completely) from messages that weren't
            # (so that these will only be deleted for one user rather than
            # for both)
            messages_to_delete = db.session.query(Message).\
                                 filter(Message.for_id == id).\
                                 filter(Message.from_deleted == True).delete()
            messages_to_update = db.session.query(Message).\
                filter(Message.for_id == id).\
                filter(Message.from_deleted == False).all()

            # For each message that wasn't deleted by the other user, the
            # value of for_deleted (indicating whether the user the message
            # is for deleted it) is updated to True
            for message in messages_to_update:
                message.for_deleted = True
        # If the type of objects to delete is outbox, delete all messages
        # from the user with that ID
        if(type == 'outbox'):
            # Separates messages that were deleted by the other user (and are
            # thus okay to delete completely) from messages that weren't
            # (so that these will only be deleted for one user rather than
            # for both)
            messages_to_delete = db.session.query(Message).\
                                 filter(Message.from_id == id).\
                                 filter(Message.for_deleted == True).delete()
            messages_to_update = db.session.query(Message).\
                filter(Message.from_id == id).\
                filter(Message.for_deleted == False).all()

            # For each message that wasn't deleted by the other user, the
            # value of from_deleted (indicating whether the user who wrote
            # the message deleted it) is updated to True
            for message in messages_to_update:
                message.from_deleted = True
        # If the type of objects to delete is threads, delete all messages
        # to and from the user with that ID
        if(type == 'threads'):
            # Get all threads in which the user is involved
            Threads = db.session.query(Thread).filter((Thread.user_1_id == id)
                                                      or (Thread.user_2_id ==
                                                      id)).all()
            # List of thread IDs to delete
            threads_to_delete = []

            # Delete the messages in each thread
            for thread in Threads:
                # Separates messages that were deleted by the other user (and
                # are thus okay to delete completely) from messages that
                # weren't (so that these will only be deleted for one user
                # rather than for both)
                messages_to_delete = db.session.query(Message).\
                                     filter(Message.thread == thread.id).\
                                     filter(((Message.for_id == id) and
                                            (Message.from_deleted == True)) |
                                            ((Message.from_id == id) and
                                            (Message.for_deleted == True))).\
                                     delete()
                messages_for_to_update = db.session.query(Message).\
                    filter(Message.thread == thread.id).\
                    filter((Message.for_id == id) and (Message.from_deleted ==
                                                       False)).all()
                messages_from_to_update = db.session.query(Message).\
                    filter(Message.thread == thread.id).\
                    filter((Message.from_id == id) and
                           (Message.for_deleted == False)).all()

                # For each message that wasn't deleted by the other user, the
                # value of for_deleted (indicating whether the user the message
                # is for deleted it) is updated to True
                for message in messages_for_to_update:
                    message.for_deleted = True

                # For each message that wasn't deleted by the other user, the
                # value of from_deleted (indicating whether the user who wrote
                # the message deleted it) is updated to True
                for message in messages_from_to_update:
                    message.from_deleted = True

                # If there are no messages left in this thread, both users
                # deleted all messages in it, so the thread can be added
                # to the "to delete" list
                if(len(messages_for_to_update) == 0 and
                   len(messages_from_to_update) == 0):
                    threads_to_delete.append(thread.id)
                else:
                    # If the current user is user 1 in the threads table,
                    # set their deleted value to true
                    if(thread.user_1_id == id):
                        thread.user_1_deleted = True
                    # Otherwise it's user 2, so set their deleted value
                    # to true
                    else:
                        thread.user_2_deleted = True

            # Then try to delete the threads that are okay to delete
            for thread in threads_to_delete:
                db.session.query(Thread).filter(Thread.id == thread).delete()

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
