# MIT License
#
# Copyright (c) 2020-2023 Send A Hug
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# The provided Software is separate from the idea behind its website. The Send A Hug
# website and its underlying design and ideas are owned by Send A Hug group and
# may not be sold, sub-licensed or distributed in any way. The Software itself may
# be adapted for any purpose and used freely under the given conditions.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
from datetime import datetime
from flask import jsonify

from .models import Post, User, Message, Thread, Report, Notification, db


# Database management methods
# -----------------------------------------------------------------
# Method: Joined_Query
# Description: Performs a joined query.
# Parameters: target (string) - the target variable + endpoint (or just
#             endpoint if they're the same).
def joined_query(target, params={}):
    return_obj = []

    if target.lower() == "full new":
        full_new_posts = (
            db.session.query(Post, User.display_name)
            .join(User)
            .order_by(db.desc(Post.date))
            .filter(Post.open_report == db.false())
            .all()
        )

        # formats each post in the list
        for post in full_new_posts:
            new_post = post[0].format()
            new_post["user"] = post[1]
            return_obj.append(new_post)
    # If the target is the full list of suggested items
    elif target.lower() == "full suggested":
        full_sug_posts = (
            db.session.query(Post, User.display_name)
            .join(User)
            .order_by(Post.given_hugs, Post.date)
            .filter(Post.open_report == db.false())
            .all()
        )

        # formats each post in the list
        for post in full_sug_posts:
            sug_post = post[0].format()
            sug_post["user"] = post[1]
            return_obj.append(sug_post)
    # if the target is the user's messages (get messages endpoint)
    elif target.lower() == "messages":
        user_id = params["user_id"]
        type = params["type"]
        thread = params["thread_id"]

        from_user = db.aliased(User)
        for_user = db.aliased(User)

        # Checks which mailbox the user is requesting
        # For inbox, gets all incoming messages
        if type == "inbox":
            user_messages = (
                db.session.query(
                    Message,
                    from_user.display_name,
                    for_user.display_name,
                    from_user.selected_character,
                    from_user.icon_colours,
                )
                .join(from_user, from_user.id == Message.from_id)
                .join(for_user, for_user.id == Message.for_id)
                .filter(Message.for_deleted == db.false())
                .filter(Message.for_id == user_id)
                .order_by(db.desc(Message.date))
                .all()
            )
        # For outbox, gets all outgoing messages
        elif type == "outbox":
            user_messages = (
                db.session.query(
                    Message,
                    from_user.display_name,
                    for_user.display_name,
                    for_user.selected_character,
                    for_user.icon_colours,
                )
                .join(from_user, from_user.id == Message.from_id)
                .join(for_user, for_user.id == Message.for_id)
                .filter(Message.from_deleted == db.false())
                .filter(Message.from_id == user_id)
                .order_by(db.desc(Message.date))
                .all()
            )
        # For threads, gets all threads' data
        elif type == "threads":
            # Get the thread ID, and users' names and IDs
            threads_messages = (
                db.session.query(
                    db.func.count(Message.id),
                    Message.thread,
                    from_user.display_name,
                    from_user.selected_character,
                    from_user.icon_colours,
                    for_user.display_name,
                    for_user.selected_character,
                    for_user.icon_colours,
                    Thread.user_1_id,
                    Thread.user_2_id,
                )
                .join(Thread, Message.thread == Thread.id)
                .join(from_user, from_user.id == Thread.user_1_id)
                .join(for_user, for_user.id == Thread.user_2_id)
                .group_by(
                    Message.thread,
                    from_user.display_name,
                    for_user.display_name,
                    Thread.user_1_id,
                    Thread.user_2_id,
                    Thread.id,
                    from_user.selected_character,
                    from_user.icon_colours,
                    for_user.selected_character,
                    for_user.icon_colours,
                )
                .order_by(Thread.id)
                .filter(
                    (
                        (Thread.user_1_id == user_id)
                        & (Thread.user_1_deleted == db.false())
                    )
                    | (
                        (Thread.user_2_id == user_id)
                        & (Thread.user_2_deleted == db.false())
                    )
                )
                .all()
            )

            # Get the date of the latest message in the thread
            latest_message = (
                db.session.query(db.func.max(Message.date), Message.thread)
                .join(Thread, Message.thread == Thread.id)
                .group_by(Message.thread, Thread.user_1_id, Thread.user_2_id)
                .order_by(Message.thread)
                .filter(
                    (
                        (Thread.user_1_id == user_id)
                        & (Thread.user_1_deleted == db.false())
                    )
                    | (
                        (Thread.user_2_id == user_id)
                        & (Thread.user_2_deleted == db.false())
                    )
                )
                .all()
            )
        # Gets a specific thread's messages
        elif type == "thread":
            user_messages = (
                db.session.query(
                    Message,
                    from_user.display_name,
                    for_user.display_name,
                    from_user.selected_character,
                    from_user.icon_colours,
                    for_user.selected_character,
                    for_user.icon_colours,
                )
                .join(from_user, from_user.id == Message.from_id)
                .join(for_user, for_user.id == Message.for_id)
                .filter(
                    ((Message.for_id == user_id) & (Message.for_deleted == db.false()))
                    | (
                        (Message.from_id == user_id)
                        & (Message.from_deleted == db.false())
                    )
                )
                .filter(Message.thread == thread)
                .order_by(db.desc(Message.date))
                .all()
            )

        # If the mailbox type is outbox or inbox
        if (type == "outbox") or (type == "inbox") or (type == "thread"):
            # formats each message in the list
            for message in user_messages:
                user_message = message[0].format()
                user_message["from"] = {"displayName": message[1]}
                user_message["for"] = {"displayName": message[2]}

                # If it's the inbox, add the sending user's profile pic
                if type == "inbox":
                    user_message["from"]["selectedIcon"] = message[3]
                    user_message["from"]["iconColours"] = json.loads(message[4])
                # If it's the outbox, add the profile pic of the user getting
                # the message
                elif type == "outbox":
                    user_message["for"]["selectedIcon"] = message[3]
                    user_message["for"]["iconColours"] = json.loads(message[4])
                # If it's a thread, add both
                else:
                    user_message["from"]["selectedIcon"] = message[3]
                    user_message["from"]["iconColours"] = json.loads(message[4])
                    user_message["for"]["selectedIcon"] = message[5]
                    user_message["for"]["iconColours"] = json.loads(message[6])

                return_obj.append(user_message)
        # Otherwise the type is threads
        else:
            # Threads data formatting
            for index, thread in enumerate(threads_messages):
                # Get the number of messages in the thread
                thread_length = len(
                    db.session.query(Message)
                    .filter(
                        (
                            (Message.for_id == user_id)
                            & (Message.for_deleted == db.false())
                        )
                        | (
                            (Message.from_id == user_id)
                            & (Message.from_deleted == db.false())
                        )
                    )
                    .filter(Message.thread == thread[1])
                    .all()
                )
                # Set up the thread
                thread = {
                    "id": thread[1],
                    "user1": {
                        "displayName": thread[2],
                        "selectedIcon": thread[3],
                        "iconColours": json.loads(thread[4]),
                    },
                    "user1Id": thread[8],
                    "user2": {
                        "displayName": thread[5],
                        "selectedIcon": thread[6],
                        "iconColours": json.loads(thread[7]),
                    },
                    "user2Id": thread[9],
                    "numMessages": thread_length,
                    "latestMessage": latest_message[index][0],
                }
                return_obj.append(thread)
    # if the target is posts search (for the search endpoint)
    elif target.lower() == "post search":
        search_query = params["query"]
        posts = (
            db.session.query(Post, User.display_name)
            .join(User)
            .order_by(db.desc(Post.date))
            .filter(Post.text.like("%" + search_query + "%"))
            .filter(Post.open_report == db.false())
            .all()
        )

        # Formats the posts
        for post in posts:
            searched_post = post[0].format()
            searched_post["user"] = post[1]
            return_obj.append(searched_post)
    # If the target is user reports (admin dashboard)
    elif target.lower() == "user reports":
        reports = (
            db.session.query(Report, User.display_name)
            .join(User, User.id == Report.user_id)
            .filter(Report.closed == db.false())
            .filter(Report.type == "User")
            .order_by(db.desc(Report.date))
            .all()
        )

        # Formats the reports
        for report in reports:
            formatted_report = report[0].format()
            formatted_report["displayName"] = report[1]
            return_obj.append(formatted_report)
    # If the target is post reports (admin dashboard)
    elif target.lower() == "post reports":
        reports = (
            db.session.query(Report, Post.text)
            .join(Post)
            .filter(Report.closed == db.false())
            .filter(Report.type == "Post")
            .order_by(db.desc(Report.date))
            .all()
        )

        # Formats the reports
        for report in reports:
            formatted_report = report[0].format()
            formatted_report["text"] = report[1]
            return_obj.append(formatted_report)
    # If the target is notifications
    elif target.lower() == "notifications":
        user_id = params["user_id"]
        last_read = params["last_read"]

        # If there's no last_read date, it means the user never checked
        # their notifications, so set it to the time this feature was added
        if last_read is None:
            last_read = datetime(2020, 7, 1, 12, 00)

        from_user = db.aliased(User)
        for_user = db.aliased(User)

        # Gets all new notifications
        notifications = (
            db.session.query(
                Notification, from_user.display_name, for_user.display_name
            )
            .join(from_user, from_user.id == Notification.from_id)
            .join(for_user, for_user.id == Notification.for_id)
            .filter(Notification.for_id == user_id)
            .filter(Notification.date > last_read)
            .order_by(Notification.date)
            .all()
        )

        # Formats all new messages
        for notification in notifications:
            user_notification = notification[0].format()
            user_notification["from"] = notification[1]
            user_notification["for"] = notification[2]
            return_obj.append(user_notification)

    return {"return": return_obj}


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
    except Exception:
        db.session.rollback()
    # Close the connection once the attempt is complete
    finally:
        db.session.close()

    return {"success": True, "added": return_object}


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
        if type(obj) == Thread and "set_deleted" in params:
            # Just in case, makes sure that set_deleted was set to true
            if params["set_deleted"]:
                messages_for = (
                    db.session.query(Message)
                    .filter(Message.thread == obj.id)
                    .filter(Message.for_id == params["user_id"])
                    .filter(Message.from_deleted == db.false())
                    .all()
                )
                messages_from = (
                    db.session.query(Message)
                    .filter(Message.thread == obj.id)
                    .filter(Message.from_id == params["user_id"])
                    .filter(Message.for_deleted == db.false())
                    .all()
                )

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
    except Exception:
        db.session.rollback()
    # Close the connection once the attempt is complete
    finally:
        db.session.close()

    return jsonify({"success": True, "updated": updated_object})


# Method: Update Multiple
# Description: Updates multiple records.
# Parameters: A list with all objects to update.
def update_multiple(objs=[]):
    updated_objects = []

    # Try to update the object in the database
    try:
        for obj in objs:
            db.session.commit()
            updated_objects.append(obj.format())
    # If there's an error, rollback
    except Exception:
        db.session.rollback()
    # Close the connection once the attempt is complete
    finally:
        db.session.close()

    return jsonify({"success": True, "updated": updated_objects})


# Method: Delete Object
# Description: Deletes an existing record.
# Parameters: Object (User, Post or Message) to delete.
def delete_object(obj):
    deleted = None

    # Try to delete the record from the database
    try:
        # If the object to delete is a thread, delete all associated
        # messages first
        if type(obj) is Thread:
            db.session.query(Message).filter(Message.thread == obj.id).delete()

        db.session.delete(obj)
        db.session.commit()
        deleted = obj.id
    # If there's an error, rollback
    except Exception:
        db.session.rollback()
    # Close the connection once the attempt is complete
    finally:
        db.session.close()

    return jsonify({"success": True, "deleted": deleted})


# Method: Delete All
# Description: Deletes all records that match a condition.
# Parameters: Type - type of item to delete (posts or messages)
#             ID - ID of the user whose posts or messages need to be deleted.
def delete_all(type, id):
    # Try to delete the records
    try:
        # If the type of objects to delete is posts, the ID is the
        # user ID whose posts need to be deleted
        if type == "posts":
            db.session.query(Post).filter(Post.user_id == id).delete()
        # If the type of objects to delete is inbox, delete all messages
        # for the user with that ID
        if type == "inbox":
            # Separates messages that were deleted by the other user (and are
            # thus okay to delete completely) from messages that weren't
            # (so that these will only be deleted for one user rather than
            # for both)
            (
                db.session.query(Message)
                .filter(Message.for_id == id)
                .filter(Message.from_deleted == db.true())
                .delete()
            )
            messages_to_update = (
                db.session.query(Message)
                .filter(Message.for_id == id)
                .filter(Message.from_deleted == db.false())
                .all()
            )

            # For each message that wasn't deleted by the other user, the
            # value of for_deleted (indicating whether the user the message
            # is for deleted it) is updated to True
            for message in messages_to_update:
                message.for_deleted = True
        # If the type of objects to delete is outbox, delete all messages
        # from the user with that ID
        if type == "outbox":
            # Separates messages that were deleted by the other user (and are
            # thus okay to delete completely) from messages that weren't
            # (so that these will only be deleted for one user rather than
            # for both)
            (
                db.session.query(Message)
                .filter(Message.from_id == id)
                .filter(Message.for_deleted == db.true())
                .delete()
            )
            messages_to_update = (
                db.session.query(Message)
                .filter(Message.from_id == id)
                .filter(Message.for_deleted == db.false())
                .all()
            )

            # For each message that wasn't deleted by the other user, the
            # value of from_deleted (indicating whether the user who wrote
            # the message deleted it) is updated to True
            for message in messages_to_update:
                message.from_deleted = True
        # If the type of objects to delete is threads, delete all messages
        # to and from the user with that ID
        if type == "threads":
            # Get all threads in which the user is involved
            Threads = (
                db.session.query(Thread)
                .filter((Thread.user_1_id == id) or (Thread.user_2_id == id))
                .all()
            )
            # List of thread IDs to delete
            threads_to_delete = []

            # Delete the messages in each thread
            for thread in Threads:
                # Separates messages that were deleted by the other user (and
                # are thus okay to delete completely) from messages that
                # weren't (so that these will only be deleted for one user
                # rather than for both)
                (
                    db.session.query(Message)
                    .filter(Message.thread == thread.id)
                    .filter(
                        ((Message.for_id == id) and (Message.from_deleted == db.true()))
                        | (
                            (Message.from_id == id)
                            and (Message.for_deleted == db.true())
                        )
                    )
                    .delete()
                )
                messages_for_to_update = (
                    db.session.query(Message)
                    .filter(Message.thread == thread.id)
                    .filter(
                        (Message.for_id == id) and (Message.from_deleted == db.false())
                    )
                    .all()
                )
                messages_from_to_update = (
                    db.session.query(Message)
                    .filter(Message.thread == thread.id)
                    .filter(
                        (Message.from_id == id) and (Message.for_deleted == db.false())
                    )
                    .all()
                )

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
                if (
                    len(messages_for_to_update) == 0
                    and len(messages_from_to_update) == 0
                ):
                    threads_to_delete.append(thread.id)
                else:
                    # If the current user is user 1 in the threads table,
                    # set their deleted value to true
                    if thread.user_1_id == id:
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
    except Exception:
        db.session.rollback()
    # Close the connection once the attempt is complete
    finally:
        db.session.close()

    return jsonify({"success": True, "deleted": type})
