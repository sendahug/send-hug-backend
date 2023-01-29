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

from typing import Literal, Any, Union

from flask import jsonify, Response

from .models import Post, Message, Thread, db


# Database management methods
# -----------------------------------------------------------------
# Method: Add
# Description: Inserts a new record into the database.
# Parameters: Object to insert (User, Post or Message).
def add(
    obj: db.Model,  # type: ignore[name-defined]
) -> dict[str, Union[bool, dict[str, Any]]]:
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
def update(obj: db.Model, params={}) -> Response:  # type: ignore[name-defined]
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
def update_multiple(
    objs: list[db.Model] = [],  # type: ignore[name-defined]
) -> Response:
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
def delete_object(obj: db.Model) -> Response:  # type: ignore[name-defined]
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
def delete_all(
    type: Literal["posts", "inbox", "outbox", "threads"], id: int
) -> Response:
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
