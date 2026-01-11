from datetime import datetime

from quart import Blueprint, Response, abort, jsonify, request
from sqlalchemy import (
    Update,
    and_,
    delete,
    desc,
    false,
    func,
    or_,
    select,
    true,
    update,
)

from auth import AuthError, UserData, requires_auth
from config.config import sah_config
from controllers.common import (
    DATETIME_PATTERN,
    ActionType,
    get_archive_action_from_body,
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
    delete_item = await _fetch_message(
        user_id=token_payload["id"],
        message_id=message_id,
    )

    # check if we are deleting the from or for message
    if delete_item.for_id == token_payload["id"]:
        delete_item.for_deleted = True
    elif delete_item.from_id == token_payload["id"]:
        delete_item.from_deleted = True

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
    action = await get_archive_action_from_body(await request.get_json())

    archive_item = await _fetch_message(
        user_id=token_payload["id"],
        message_id=message_id,
    )

    # check if we are un/archiving/deleting the from or for message
    if archive_item.for_id == token_payload["id"]:
        if action == "archive":
            archive_item.for_archived = True
        elif action == "unarchive":
            archive_item.for_archived = False
    elif archive_item.from_id == token_payload["id"]:
        if action == "archive":
            archive_item.from_archived = True
        elif action == "unarchive":
            archive_item.from_archived = False

    # mark the object for un/archival/deletion
    await sah_config.db.update_object(archive_item, current_user_id=token_payload["id"])

    return jsonify({"success": True, f"{action}d": message_id})


async def _fetch_message(user_id: int, message_id: int) -> Message:
    validator.check_type(message_id, "Message ID")
    message_id = int(message_id)  # flask typing is rubbish

    message_item = await sah_config.db.one_or_404(
        item_id=message_id,
        item_type=Message,
    )
    if message_item.for_id != user_id and message_item.from_id != user_id:
        raise AuthError(
            {
                "code": 403,
                "description": "You do not have permission to "
                "alter another user's messages.",
            },
            403,
        )

    return message_item


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
    delete_item = await _fetch_thread(
        user_id=token_payload["id"],
        thread_id=thread_id,
    )

    # For each message that wasn't deleted by the other user, the
    # value of for_deleted/from_deleted (depending on which of the users
    # it is) is updated to True
    from_stmt = _get_update_from_stmt(token_payload["id"], thread_id)
    for_stmt = _get_update_for_stmt(token_payload["id"], thread_id)

    from_stmt = from_stmt.values({"from_deleted": true()})
    for_stmt = for_stmt.values({"for_deleted": true()})

    await sah_config.db.update_multiple_objects_with_dml(
        update_stmts=[from_stmt, for_stmt]
    )

    await sah_config.db.session.refresh(delete_item)
    delete_item = await sah_config.db.one_or_404(
        item_id=thread_id,
        item_type=Thread,
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
    action = await get_archive_action_from_body(await request.get_json())

    archive_item = await _fetch_thread(user_id=token_payload["id"], thread_id=thread_id)

    # For each message that wasn't un/archived by the other user, the
    # value of for_deleted/from_deleted (depending on which of the users
    # it is) is updated to True
    from_stmt = _get_update_from_stmt(token_payload["id"], thread_id)
    for_stmt = _get_update_for_stmt(token_payload["id"], thread_id)

    if action == "archive":
        from_stmt = from_stmt.values({"from_archived": true()})
        for_stmt = for_stmt.values({"for_archived": true()})
    elif action == "unarchive":
        from_stmt = from_stmt.values({"from_archived": false()})
        for_stmt = for_stmt.values({"for_archived": false()})

    await sah_config.db.update_multiple_objects_with_dml(
        update_stmts=[from_stmt, for_stmt]
    )

    await sah_config.db.session.refresh(archive_item)
    archive_item = await sah_config.db.one_or_404(
        item_id=thread_id,
        item_type=Thread,
    )

    return jsonify(
        {
            "success": True,
            f"{action}d": thread_id,
            "currentUserArchived": (
                archive_item.user1_archived
                if token_payload["id"] == archive_item.user_1_id
                else archive_item.user2_archived
            ),
        }
    )


async def _fetch_thread(user_id: int, thread_id: int) -> Thread:
    validator.check_type(thread_id, "Thread ID")
    thread_id = int(thread_id)  # flask typing is rubbish

    thread_item = await sah_config.db.one_or_404(
        item_id=thread_id,
        item_type=Thread,
    )

    # Check if the user is attempting to delete another user's threads
    if thread_item.user_1_id != user_id and thread_item.user_2_id != user_id:
        raise AuthError(
            {
                "code": 403,
                "description": "You do not have permission to "
                "alter another user's thread messages.",
            },
            403,
        )

    return thread_item


def _get_update_from_stmt(user_id: int, thread_id: int | None = None) -> Update:
    if not thread_id:
        return update(Message).where(Message.from_id == user_id)

    return update(Message).where(
        and_(Message.thread == thread_id, Message.from_id == user_id)
    )


def _get_update_for_stmt(user_id: int, thread_id: int | None = None) -> Update:
    if not thread_id:
        return update(Message).where(Message.for_id == user_id)

    return update(Message).where(
        and_(Message.thread == thread_id, Message.for_id == user_id)
    )


# Endpoint: DELETE /threads
# Description: Deletes all threads.
# Authorization: delete:messages.
@messages_endpoints.route("/threads", methods=["DELETE"])
@requires_auth(sah_config, ["delete:messages"])
async def clear_mailbox(token_payload: UserData) -> Response:
    num_messages = await _get_threads_count(
        user_id=token_payload["id"], action="delete"
    )

    update_from_stmt = _get_update_from_stmt(token_payload["id"])
    update_for_stmt = _get_update_for_stmt(token_payload["id"])

    update_from_stmt = update_from_stmt.values({"from_deleted": true()})
    update_for_stmt = update_for_stmt.values({"for_deleted": true()})

    # mark each message that was either sent from or sent to the user
    # as deleted
    update_stmts = [update_from_stmt, update_for_stmt]
    await sah_config.db.update_multiple_objects_with_dml(update_stmts=update_stmts)

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
    action = await get_archive_action_from_body(await request.get_json())

    num_messages = await _get_threads_count(user_id=token_payload["id"], action=action)

    update_from_stmt = _get_update_from_stmt(token_payload["id"])
    update_for_stmt = _get_update_for_stmt(token_payload["id"])
    if action == "archive":
        update_from_stmt = update_from_stmt.values({"from_archived": true()})
        update_for_stmt = update_for_stmt.values({"for_archived": true()})
    elif action == "unarchive":
        update_from_stmt = update_from_stmt.values({"from_archived": false()})
        update_for_stmt = update_for_stmt.values({"for_archived": false()})

    # mark each message that was either sent from or sent to the user
    # as un/archived
    update_stmts = [update_from_stmt, update_for_stmt]
    await sah_config.db.update_multiple_objects_with_dml(update_stmts=update_stmts)

    return jsonify(
        {"success": True, "userID": token_payload["id"], f"{action}d": num_messages}
    )


async def _get_threads_count(user_id: int, action: ActionType) -> int:
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
    threads_count = await sah_config.db.session.scalar(
        select(func.count(Thread.id)).filter(
            or_(
                and_(Thread.user_1_id == user_id, user1_condition[action]),
                and_(Thread.user_2_id == user_id, user2_condition[action]),
            )
        )
    )

    if not threads_count:
        abort(404)

    return threads_count
