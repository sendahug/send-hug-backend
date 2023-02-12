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

from typing import Literal, Any, TypedDict, Union

from flask import abort
from sqlalchemy.exc import DataError, IntegrityError  # type: ignore

from .models import Post, Message, Thread, db


class DBReturnModel(TypedDict):
    success: bool
    resource: dict[str, Any]


class DBBulkModel(TypedDict):
    success: bool
    resource: list[dict[str, Any]]


class DBDeleteModel(TypedDict):
    success: bool
    deleted: Union[int, str]


# Database management methods
# -----------------------------------------------------------------
def add(obj: db.Model) -> DBReturnModel:  # type: ignore[name-defined]
    """
    Inserts a new record into the database.

    param obj: Object to insert (User, Post or Message).
    """
    return_object = {}

    # Try to add the object to the database
    try:
        db.session.add(obj)
        db.session.commit()
        return_object = obj.format()
    # If there's a database error
    except (DataError, IntegrityError) as err:
        db.session.rollback()
        abort(422, str(err.orig))
    # If there's an error, rollback
    except Exception as err:
        db.session.rollback()
        abort(500, str(err))
    # Close the connection once the attempt is complete
    finally:
        db.session.close()

    return {"success": True, "resource": return_object}


def update(obj: db.Model, params={}) -> DBReturnModel:  # type: ignore[name-defined]
    """
    Updates an existing record.

    param obj: Updated object (User, Post or Message).
    param params: dictionary of extra params for handling related objects
    """
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
    # If there's a database error
    except (DataError, IntegrityError) as err:
        db.session.rollback()
        abort(422, str(err.orig))
    # If there's an error, rollback
    except Exception as err:
        db.session.rollback()
        abort(500, str(err))
    # Close the connection once the attempt is complete
    finally:
        db.session.close()

    return {"success": True, "resource": updated_object}


def update_multiple(
    objs: list[db.Model] = [],  # type: ignore[name-defined]
) -> DBBulkModel:
    """
    Updates multiple records.

    param objs: A list with all objects to update.
    """
    updated_objects = []

    # Try to update the object in the database
    try:
        for obj in objs:
            db.session.commit()
            updated_objects.append(obj.format())
    # If there's a database error
    except (DataError, IntegrityError) as err:
        db.session.rollback()
        abort(422, str(err.orig))
    # If there's an error, rollback
    except Exception as err:
        db.session.rollback()
        abort(500, str(err))
    # Close the connection once the attempt is complete
    finally:
        db.session.close()

    return {"success": True, "resource": updated_objects}


def delete_object(obj: db.Model) -> DBDeleteModel:  # type: ignore[name-defined]
    """
    Deletes an existing record.

    param obj: Object (User, Post or Message) to delete.
    """
    # Try to delete the record from the database
    try:
        # If the object to delete is a thread, delete all associated
        # messages first
        if type(obj) is Thread:
            db.session.query(Message).filter(Message.thread == obj.id).delete()

        db.session.delete(obj)
        db.session.commit()
        deleted: int = obj.id
    # If there's a database error
    except (DataError, IntegrityError) as err:
        db.session.rollback()
        abort(422, str(err.orig))
    # If there's an error, rollback
    except Exception as err:
        db.session.rollback()
        abort(500, str(err))
    # Close the connection once the attempt is complete
    finally:
        db.session.close()

    return {"success": True, "deleted": deleted}


def delete_all(
    type: Literal["posts", "inbox", "outbox", "thread", "threads"], id: int
) -> DBDeleteModel:
    """
    Deletes all records that match a condition.

    param type: type of item to delete (posts or messages)
    param id: ID of the user whose posts or messages need to be deleted.
    """
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
    # If there's a database error
    except (DataError, IntegrityError) as err:
        db.session.rollback()
        abort(422, str(err.orig))
    # If there's an error, rollback
    except Exception as err:
        db.session.rollback()
        abort(500, str(err))
    # Close the connection once the attempt is complete
    finally:
        db.session.close()

    return {"success": True, "deleted": type}
