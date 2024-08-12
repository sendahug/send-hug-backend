from datetime import datetime
from typing import Literal

from quart import Blueprint, Response, abort, jsonify, request
from sqlalchemy import and_, delete, desc, false, func, or_, select, true, update

from auth import AuthError, UserData, requires_auth
from config import sah_config

from .common import (
    DATETIME_PATTERN,
    get_current_filters,
    get_thread_id_for_users,
    send_push_notification,
    validator,
)
from models import Message, Notification, Thread
from utils.push_notifications import RawPushData

messages_endpoints = Blueprint("posts", __name__)


# Endpoint: GET /messages
# Description: Gets the user's messages.
# Parameters: None.
# Authorization: read:messages.
@messages_endpoints.route("/messages")
@requires_auth(sah_config, ["read:messages"])
async def get_user_messages(token_payload: UserData) -> Response:
    page = request.args.get("page", 1, type=int)
    type = request.args.get("type", "inbox", type=str)
    thread_id = request.args.get("threadID", None, type=int)

    if type in ["inbox", "outbox", "thread"]:
        messages_query = select(Message)

        # For inbox, gets all incoming messages
        if type == "inbox":
            messages_query = messages_query.filter(
                Message.for_deleted == false()
            ).filter(Message.for_id == token_payload["id"])
        # For outbox, gets all outgoing messages
        elif type == "outbox":
            messages_query = messages_query.filter(
                Message.from_deleted == false()
            ).filter(Message.from_id == token_payload["id"])
        # Gets a specific thread's messages
        else:
            message = await sah_config.db.session.scalar(
                select(Thread).filter(Thread.id == thread_id)
            )
            # Check if there's a thread with that ID at all
            if message:
                # If the user is trying to view a thread that belongs to other
                # users, raise an AuthError
                if (message.user_1_id != token_payload["id"]) and (
                    message.user_2_id != token_payload["id"]
                ):
                    raise AuthError(
                        {
                            "code": 403,
                            "description": "You do not have permission "
                            "to view another user's messages.",
                        },
                        403,
                    )
            else:
                abort(404)

            messages_query = messages_query.filter(
                (
                    (Message.for_id == token_payload["id"])
                    & (Message.for_deleted == false())
                )
                | (
                    (Message.from_id == token_payload["id"])
                    & (Message.from_deleted == false())
                )
            ).filter(Message.thread == thread_id)

        messages = await sah_config.db.paginate(
            messages_query.order_by(desc(Message.date)),
            current_page=page,
        )

        # formats each message in the list
        formatted_messages = messages.resource
        total_pages = messages.total_pages

    # For threads, gets all threads' data
    else:
        # Get the thread ID, and users' names and IDs
        threads_messages = await sah_config.db.paginate(
            select(Thread)
            .filter(
                or_(
                    and_(
                        Thread.user_1_id == token_payload["id"],
                        Thread.user1_deleted == false(),
                    ),
                    and_(
                        Thread.user_2_id == token_payload["id"],
                        Thread.user2_deleted == false(),
                    ),
                )
            )
            .order_by(Thread.id),
            current_page=page,
            current_user_id=token_payload["id"],
        )

        total_pages = threads_messages.total_pages
        # Threads data formatting
        formatted_messages = threads_messages.resource

    return jsonify(
        {
            "success": True,
            "messages": formatted_messages,
            "current_page": int(page),
            "total_pages": total_pages,
        }
    )


# Endpoint: POST /messages
# Description: Adds a new message to the messages table.
# Parameters: None.
# Authorization: post:message.
@messages_endpoints.route("/messages", methods=["POST"])
@requires_auth(sah_config, ["post:message"])
async def add_message(token_payload: UserData) -> Response:
    # Gets the new message's data
    message_data = await request.get_json()

    validator.validate_post_or_message(
        text=message_data["messageText"],
        type="message",
        filtered_words=await get_current_filters(),
    )

    thread_id = await get_thread_id_for_users(
        user1_id=token_payload["id"],
        user2_id=message_data["forId"],
        current_user_id=token_payload["id"],
    )

    # Create a new message
    new_message = Message(
        from_id=token_payload["id"],
        for_id=int(message_data["forId"]),
        text=message_data["messageText"],
        date=datetime.strptime(message_data["date"], DATETIME_PATTERN),
        thread=thread_id,
    )

    # Create a notification for the user getting the message
    notification = Notification(
        for_id=int(message_data["forId"]),
        from_id=token_payload["id"],
        type="message",
        text="You have a new message",
        date=datetime.strptime(message_data["date"], DATETIME_PATTERN),
    )
    push_notification: RawPushData = {
        "type": "message",
        "text": f"{token_payload['displayName']} sent you a message",
    }
    notification_for = message_data["forId"]

    # Try to add the message to the database
    added = await sah_config.db.add_multiple_objects(
        objects=[new_message, notification]
    )
    sent_message = [item for item in added if "threadID" in item.keys()]
    await send_push_notification(user_id=notification_for, data=push_notification)

    return jsonify({"success": True, "message": sent_message[0]})


# Endpoint: DELETE /messages/<mailbox_type>/<item_id>
# Description: Deletes a message/thread from the database.
# Parameters: mailbox_type - the type of message to delete.
#             item_id - ID of the message/thread to delete.
# Authorization: delete:messages.
@messages_endpoints.route("/messages/<mailbox_type>/<item_id>", methods=["DELETE"])
@requires_auth(sah_config, ["delete:messages"])
async def delete_thread(  # TODO: This should be renamed to delete_message
    token_payload: UserData,
    mailbox_type: Literal["inbox", "outbox", "thread", "threads"],
    item_id: int,
) -> Response:
    # Variable indicating whether to delete the message from the databse
    # or leave it in it (for the other user)
    delete_message: bool = False
    delete_item: Message | Thread | None = None

    validator.check_type(item_id, "Message ID")

    # If the mailbox type is inbox or outbox, search for a message
    # with that ID
    if mailbox_type in ["inbox", "outbox", "thread"]:
        delete_item = await sah_config.db.one_or_404(
            item_id=int(item_id),
            item_type=Message,
        )
    # If the mailbox type is threads, search for a thread with that ID
    elif mailbox_type == "threads":
        delete_item = await sah_config.db.one_or_404(
            item_id=int(item_id),
            item_type=Thread,
        )
    else:
        abort(400)

    # If the user is attempting to delete another user's messages
    # TODO: This condition is so overcomplicated, it really needs to be simpler.
    if (
        isinstance(delete_item, Message)
        and (
            (mailbox_type == "inbox" and token_payload["id"] != delete_item.for_id)
            or (mailbox_type == "outbox" and token_payload["id"] != delete_item.from_id)
        )
        or (
            isinstance(delete_item, Thread)
            and (token_payload["id"] != delete_item.user_1_id)
            and (token_payload["id"] != delete_item.user_2_id)
        )
    ):
        raise AuthError(
            {
                "code": 403,
                "description": "You do not have permission to "
                "delete another user's messages.",
            },
            403,
        )

    # If the mailbox type is inbox/outbox/thread
    if isinstance(delete_item, Message) and mailbox_type in [
        "inbox",
        "outbox",
        "thread",
    ]:
        if delete_item.for_id == token_payload["id"]:
            delete_item.for_deleted = True
        else:
            delete_item.from_deleted = True

    # Check the type of item and which user deleted the message/thread
    if (
        type(delete_item) is Message
        and delete_item.for_deleted
        and delete_item.from_deleted
    ):
        delete_message = True
    elif (
        type(delete_item) is Thread
        and delete_item.user1_deleted
        and delete_item.user2_deleted
    ):
        delete_message = True
    else:
        delete_message = False

    # Try to delete the thread
    # If both users deleted the message/thread, delete it from
    # the database entirely
    if delete_message:
        await sah_config.db.delete_object(delete_item)
    # Otherwise, just update the appropriate deleted property
    else:
        if isinstance(delete_item, Message):
            # For each message that wasn't deleted by the other user, the
            # value of for_deleted/from_deleted (depending on which of the users
            # it is) is updated to True
            from_stmt = (
                update(Message)
                .where(
                    and_(
                        Message.thread == delete_item.id,
                        Message.for_id == token_payload["id"],
                        Message.from_deleted == false(),
                    )
                )
                .values(for_deleted=true())
            )

            for_stmt = (
                update(Message)
                .where(
                    and_(
                        Message.thread == delete_item.id,
                        Message.from_id == token_payload["id"],
                        Message.for_deleted == false(),
                    )
                )
                .values(from_deleted=true())
            )

            delete_stmt = delete(Message).where(
                and_(
                    Message.thread == delete_item.id,
                    or_(
                        and_(
                            Message.for_id == token_payload["id"],
                            Message.from_deleted == true(),
                        ),
                        and_(
                            Message.from_id == token_payload["id"],
                            Message.for_deleted == true(),
                        ),
                    ),
                )
            )

            await sah_config.db.update_object(
                obj=delete_item, current_user_id=token_payload["id"]
            )
            await sah_config.db.update_multiple_objects_with_dml(
                update_stmts=[from_stmt, for_stmt]
            )
            await sah_config.db.delete_multiple_objects(delete_stmt=delete_stmt)

        else:
            await sah_config.db.update_object(
                delete_item, current_user_id=token_payload["id"]
            )

    return jsonify({"success": True, "deleted": int(item_id)})


# Endpoint: DELETE /messages/<mailbox_type>
# Description: Clears the selected mailbox (deleting all messages in it).
# Parameters: mailbox_type - Type of mailbox to clear.
# Authorization: delete:messages.
@messages_endpoints.route("/messages/<mailbox_type>", methods=["DELETE"])
@requires_auth(sah_config, ["delete:messages"])
async def clear_mailbox(
    token_payload: UserData,
    mailbox_type: Literal["inbox", "outbox", "thread", "threads"],
) -> Response:
    num_messages = 0

    # If the user is trying to clear their inbox
    if mailbox_type == "inbox":
        num_messages = await sah_config.db.session.scalar(
            select(func.count(Message.id)).filter(Message.for_id == token_payload["id"])
        )
        # If there are no messages, abort
        if num_messages == 0:
            abort(404)

        # Separates messages that were deleted by the other user (and are
        # thus okay to delete completely) from messages that weren't
        # (so that these will only be deleted for one user rather than
        # for both)
        # delete_stmt = delete(Message).where(
        #     and_(Message.for_id == user_id, Message.from_deleted == true())
        # )

        # For each message that wasn't deleted by the other user, the
        # value of for_deleted (indicating whether the user the message
        # is for deleted it) is updated to True
        update_stmt = (
            update(Message)
            .where(
                and_(
                    Message.for_id == token_payload["id"],
                    Message.from_deleted == false(),
                )
            )
            .values(for_deleted=true())
        )

        # sah_config.db.delete_multiple_objects(delete_stmt=delete_stmt)
        await sah_config.db.update_multiple_objects_with_dml(update_stmts=update_stmt)

    # If the user is trying to clear their outbox
    if mailbox_type == "outbox":
        num_messages = await sah_config.db.session.scalar(
            select(func.count(Message.id)).filter(
                Message.from_id == token_payload["id"]
            )
        )
        # If there are no messages, abort
        if num_messages == 0:
            abort(404)

        # Separates messages that were deleted by the other user (and are
        # thus okay to delete completely) from messages that weren't
        # (so that these will only be deleted for one user rather than
        # for both)
        delete_stmt = delete(Message).where(
            and_(
                Message.from_id == token_payload["id"],
                Message.for_deleted == true(),
            )
        )

        # For each message that wasn't deleted by the other user, the
        # value of from_deleted (indicating whether the user who wrote
        # the message deleted it) is updated to True
        update_stmt = (
            update(Message)
            .where(
                and_(
                    Message.from_id == token_payload["id"],
                    Message.for_deleted == false(),
                )
            )
            .values(from_deleted=true())
        )

        await sah_config.db.delete_multiple_objects(delete_stmt=delete_stmt)
        await sah_config.db.update_multiple_objects_with_dml(update_stmts=update_stmt)

    # If the user is trying to clear their threads mailbox
    if mailbox_type == "threads":
        num_messages = await sah_config.db.session.scalar(
            select(func.count(Thread.id)).filter(
                or_(
                    and_(
                        Thread.user_1_id == token_payload["id"],
                        Thread.user1_deleted == false(),
                    ),
                    and_(
                        Thread.user_2_id == token_payload["id"],
                        Thread.user2_deleted == false(),
                    ),
                )
            )
        )
        # If there are no messages, abort
        if num_messages == 0:
            abort(404)

        # Fetch all the messages that need to be updated, then the threads
        # that need to be updated
        from_messages_stmt = (
            update(Message)
            .where(
                and_(
                    Message.from_id == token_payload["id"],
                    Message.for_deleted == false(),
                )
            )
            .values(from_deleted=true())
        )

        for_messages_stmt = (
            update(Message)
            .where(
                and_(
                    Message.for_id == token_payload["id"],
                    Message.from_deleted == false(),
                )
            )
            .values(for_deleted=true())
        )

        update_stmts = [
            from_messages_stmt,
            for_messages_stmt,
        ]

        # The compile the delete statements for everything that needs to be
        # deleted.
        delete_messages_stmt = delete(Message).where(
            or_(
                and_(
                    Message.for_id == token_payload["id"],
                    Message.from_deleted == true(),
                ),
                and_(
                    Message.from_id == token_payload["id"],
                    Message.for_deleted == true(),
                ),
            )
        )

        delete_threads_stmt = delete(Thread).where(
            or_(
                and_(
                    Thread.user_1_id == token_payload["id"],
                    Thread.user2_deleted == true(),
                ),
                and_(
                    Thread.user_2_id == token_payload["id"],
                    Thread.user1_deleted == true(),
                ),
            )
        )

        await sah_config.db.delete_multiple_objects(delete_stmt=delete_messages_stmt)
        await sah_config.db.delete_multiple_objects(delete_stmt=delete_threads_stmt)
        await sah_config.db.update_multiple_objects_with_dml(update_stmts=update_stmts)

    return jsonify(
        {"success": True, "userID": token_payload["id"], "deleted": num_messages}
    )
