from datetime import datetime
from typing import Any

from quart import Blueprint, Response, abort, jsonify, request
from sqlalchemy import and_, delete, desc, false, func, or_, select, true, update

from auth import AuthError, UserData, requires_auth
from config.config import sah_config

from .common import (
    DATETIME_PATTERN,
    get_current_filters,
    get_thread_id_for_users,
    send_notifications,
    validator,
)
from models import Message, Notification, Thread
from utils.push_notifications import RawPushData

messages_endpoints = Blueprint("messages", __name__)


# Endpoint: GET /messages
# Description: Gets the user's messages from a thread.
# Parameters: None.
# Authorization: read:messages.
@messages_endpoints.route("/messages")
@requires_auth(sah_config, ["read:messages"])
async def get_thread(token_payload: UserData) -> Response:
    page = request.args.get("page", 1, type=int)
    thread_id = request.args.get("threadID", None, type=int)

    message = await sah_config.db.session.scalar(
        select(Thread).filter(Thread.id == thread_id)
    )
    # Check if there's a thread with that ID at all
    if not message:
        abort(404)

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

    messages_query = (
        select(Message)
        .filter(
            ((Message.for_id == token_payload["id"]) & (Message.for_deleted == false()))
            | (
                (Message.from_id == token_payload["id"])
                & (Message.from_deleted == false())
            )
        )
        .filter(Message.thread == thread_id)
    )

    messages = await sah_config.db.paginate(
        messages_query.order_by(desc(Message.date)),
        current_page=page,
    )

    # formats each message in the list
    formatted_messages = messages.resource
    total_pages = messages.total_pages

    return jsonify(
        {
            "success": True,
            "messages": formatted_messages,
            "current_page": int(page),
            "total_pages": total_pages,
        }
    )


# Endpoint: GET /threads
# Description: Gets a summary of all the thread data for the user
# Parameters: None.
# Authorization: read:messages.
@messages_endpoints.route("/threads")
@requires_auth(sah_config, ["read:messages"])
async def get_threads(token_payload: UserData) -> Response:
    page = request.args.get("page", 1, type=int)

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
    await send_notifications(user_id=notification_for, data=push_notification)

    return jsonify({"success": True, "message": sent_message[0]})


# Endpoint: DELETE /messages/<message_id>
# Description: Deletes a message.
# Parameters: message_id - the ID of the message to delete.
# Authorization: delete:messages.
@messages_endpoints.route("/messages/<message_id>", methods=["DELETE"])
@requires_auth(sah_config, ["delete:messages"])
async def delete_message(
    token_payload: UserData,
    message_id: int,
) -> Response:
    message_id = int(message_id)  # flask typing is rubbish
    delete_item = await _toggle_archive_message(
        user_id=token_payload["id"],
        message_id=message_id,
        action="delete",
    )

    if delete_item.for_deleted and delete_item.from_deleted:
        # If both users have deleted the message, delete it from the database
        # it's a bit redundant to update and then delete but it will make removing the
        # delete code easier in the future
        await sah_config.db.delete_object(delete_item)

    return jsonify({"success": True, "deleted": message_id})


# Endpoint: PATCH /messages/<message_id>/archive
# Description: Archives a message.
# Parameters: message_id - the ID of the message to archive.
# Authorization: archive:messages.
@messages_endpoints.route("/messages/<message_id>/archive", methods=["PATCH"])
@requires_auth(sah_config, ["archive:messages"])
async def archive_message(
    token_payload: UserData,
    message_id: int,
) -> Response:
    message_id = int(message_id)  # flask typing is rubbish
    action = request.args.get("action", "none", type=str)
    if action not in ["archive", "unarchive", "delete"]:
        abort(
            400,
            description="The 'action' query parameter must be specified and one of"
            "archive, unarchive or delete.",
        )

    await _toggle_archive_message(
        user_id=token_payload["id"],
        message_id=message_id,
        action=action,
    )

    return jsonify({"success": True, f"{action}d": message_id})


async def _toggle_archive_message(
    user_id: int, message_id: int, action: str
) -> Message:
    validator.check_type(message_id, "Message ID")
    message_id = int(message_id)  # flask typing is rubbish

    archive_item = await sah_config.db.one_or_404(
        item_id=message_id,
        item_type=Message,
    )
    if archive_item.for_id != user_id and archive_item.from_id != user_id:
        raise AuthError(
            {
                "code": 403,
                "description": "You do not have permission to "
                f"{action} another user's messages.",
            },
            403,
        )

    # check if we are un/archiving/deleting the from or for message
    if archive_item.for_id == user_id:
        if action == "archive" and not archive_item.for_archived:
            archive_item.for_archived = True
        elif action == "unarchive" and archive_item.for_archived:
            archive_item.for_archived = False
        elif action == "delete" and not archive_item.for_deleted:
            archive_item.for_deleted = True
        else:
            raise AuthError(
                {
                    "code": 409,
                    "description": f"You cannot {action} an {action}d post.",
                },
                409,
            )
    elif archive_item.from_id == user_id:
        if action == "archive" and not archive_item.from_archived:
            archive_item.from_archived = True
        elif action == "unarchive" and archive_item.from_archived:
            archive_item.from_archived = False
        elif action == "delete" and not archive_item.from_deleted:
            archive_item.from_deleted = True
        else:
            raise AuthError(
                {
                    "code": 409,
                    "description": f"You cannot {action} an {action}d post.",
                },
                409,
            )

    # mark the object for un/archival/deletion
    await sah_config.db.update_object(archive_item, current_user_id=user_id)

    return archive_item


# Endpoint: DELETE /threads/<thread_id>
# Description: Deletes a thread.
# Parameters: thread_id - the ID of the thread to delete.
# Authorization: delete:messages.
@messages_endpoints.route("/threads/<thread_id>", methods=["DELETE"])
@requires_auth(sah_config, ["delete:messages"])
async def delete_thread(
    token_payload: UserData,
    thread_id: int,
) -> Response:
    thread_id = int(thread_id)  # flask typing is rubbish
    delete_item = await _toggle_archive_thread(
        user_id=token_payload["id"],
        thread_id=thread_id,
        action="delete",
    )

    # delete the ones that were deleted by both users
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
    await sah_config.db.delete_multiple_objects(delete_stmt=delete_stmt)

    if delete_item.user1_deleted and delete_item.user2_deleted:
        # If both users have deleted the thread, delete it from the database
        await sah_config.db.delete_object(delete_item)

    return jsonify({"success": True, "deleted": thread_id})


# Endpoint: PATCH /threads/<thread_id>/archive
# Description: Archives a thread.
# Parameters: thread_id - the ID of the thread to archive.
# Authorization: archive:messages.
@messages_endpoints.route("/threads/<thread_id>/archive", methods=["PATCH"])
@requires_auth(sah_config, ["archive:messages"])
async def archive_thread(
    token_payload: UserData,
    thread_id: int,
) -> Response:
    thread_id = int(thread_id)  # flask typing is rubbish
    action = request.args.get("action", "none", type=str)
    if action not in ["archive", "unarchive", "delete"]:
        abort(
            400,
            description="The 'action' query parameter must be specified and one of"
            "archive, unarchive or delete.",
        )

    archive_item = await _toggle_archive_thread(
        user_id=token_payload["id"],
        thread_id=thread_id,
        action=action,
    )

    return jsonify(
        {
            "success": True,
            f"{action}d": thread_id,
            "user1Archived": archive_item.user1_archived,
            "user2Archived": archive_item.user2_archived,
        }
    )


async def _toggle_archive_thread(user_id: int, thread_id: int, action: str) -> Thread:
    validator.check_type(thread_id, "Thread ID")
    thread_id = int(thread_id)  # flask typing is rubbish

    archive_item = await sah_config.db.one_or_404(
        item_id=thread_id,
        item_type=Thread,
    )

    # Check if the user is attempting to delete another user's threads
    if archive_item.user_1_id != user_id and archive_item.user_2_id != user_id:
        raise AuthError(
            {
                "code": 403,
                "description": "You do not have permission to "
                f"{action} another user's thread messages.",
            },
            403,
        )

    for_field: dict[str, dict[str, Any]] = {
        "archive": {"for_archived": true()},
        "unarchive": {"for_archived": false()},
        "delete": {"for_deleted": true()},
    }
    from_field: dict[str, dict[str, Any]] = {
        "archive": {"from_archived": true()},
        "unarchive": {"from_archived": false()},
        "delete": {"from_deleted": true()},
    }
    # For each message that wasn't un/archived/deleted by the other user, the
    # value of for_deleted/from_deleted (depending on which of the users
    # it is) is updated to True
    from_stmt = (
        update(Message)
        .where(
            and_(
                Message.thread == archive_item.id,
                Message.from_id == user_id,
            )
        )
        .values(from_field[action])
    )

    for_stmt = (
        update(Message)
        .where(
            and_(
                Message.thread == archive_item.id,
                Message.for_id == user_id,
            )
        )
        .values(for_field[action])
    )
    await sah_config.db.update_multiple_objects_with_dml(
        update_stmts=[from_stmt, for_stmt]
    )

    await sah_config.db.session.refresh(archive_item)
    archive_item = await sah_config.db.one_or_404(
        item_id=thread_id,
        item_type=Thread,
    )

    return archive_item


# Endpoint: DELETE /threads
# Description: Deletes all threads.
# Authorization: delete:messages.
@messages_endpoints.route("/threads", methods=["DELETE"])
@requires_auth(sah_config, ["delete:messages"])
async def clear_mailbox(token_payload: UserData) -> Response:
    num_messages = await _toggle_archive_mailbox(
        user_id=token_payload["id"], action="delete"
    )

    delete_stmt = delete(Message).where(
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
    await sah_config.db.delete_multiple_objects(delete_stmt=delete_stmt)

    return jsonify(
        {"success": True, "userID": token_payload["id"], "deleted": num_messages}
    )


# Endpoint: PATCH /threads/archive
# Description: Archives all threads.
# Authorization: archive:messages.
@messages_endpoints.route("/threads/archive", methods=["PATCH"])
@requires_auth(sah_config, ["archive:messages"])
async def archive_mailbox(token_payload: UserData) -> Response:
    action = request.args.get("action", "none", type=str)
    if action not in ["archive", "unarchive", "delete"]:
        abort(
            400,
            description="The 'action' query parameter must be specified and one of"
            "archive, unarchive or delete.",
        )

    num_messages = await _toggle_archive_mailbox(
        user_id=token_payload["id"], action=action
    )

    return jsonify(
        {"success": True, "userID": token_payload["id"], f"{action}d": num_messages}
    )


async def _toggle_archive_mailbox(user_id: int, action: str) -> int:
    async def get_threads_count(user_id: int, action: str) -> int | None:
        user1_condition = {
            "archive": Thread.user1_archived == false(),
            "unarchive": Thread.user1_archived == true(),
            "delete": Thread.user1_deleted == false(),
        }
        user2_condition = {
            "archive": Thread.user2_archived == false(),
            "unarchive": Thread.user2_archived == true(),
            "delete": Thread.user2_deleted == false(),
        }
        return await sah_config.db.session.scalar(
            select(func.count(Thread.id)).filter(
                or_(
                    and_(Thread.user_1_id == user_id, user1_condition[action]),
                    and_(Thread.user_2_id == user_id, user2_condition[action]),
                )
            )
        )

    num_messages = await get_threads_count(user_id, action)
    # If there are no messages, abort
    if not num_messages:
        abort(404)

    for_field: dict[str, dict[str, Any]] = {
        "archive": {"for_archived": true()},
        "unarchive": {"for_archived": false()},
        "delete": {"for_deleted": true()},
    }
    from_field: dict[str, dict[str, Any]] = {
        "archive": {"from_archived": true()},
        "unarchive": {"from_archived": false()},
        "delete": {"from_deleted": true()},
    }

    # mark each message that was either sent from or sent to the user
    # as deleted/un/archived
    update_stmts = [
        update(Message)
        .where(or_(Message.from_id == user_id))
        .values(from_field[action]),
        update(Message)
        .where(or_(Message.for_id == user_id))
        .values(**for_field[action]),
    ]
    await sah_config.db.update_multiple_objects_with_dml(update_stmts=update_stmts)

    return num_messages
